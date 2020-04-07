"""Check whether all contracts are fulfilled in all modules."""

from dataclasses import dataclass
from typing import Iterable, Sequence, List, Optional

from mypy.modulefinder import BuildSource
from mypy.nodes import (
    ClassDef,
    FakeInfo,
    Context,
    NameExpr,
    FuncDef,
    TryStmt,
    Decorator,
    CallExpr,
    Statement,
    SymbolNode,
    Expression,
    TupleExpr,
    MemberExpr,
)

from mypy_extensions import mypyc_attr

from plshandle._cache import _MypyCache
from plshandle._gather_contracts import _get_contract_exceptions, Contract
from plshandle._resolve_alias import _ResolveAliasVisitor


@dataclass(frozen=True, repr=False)
class ExceptionResult:
    """Determines whether and when the exception is handled."""

    exception: SymbolNode
    is_propagated: bool  #: does the function calling the function propagate this contract?
    is_handled: bool  #: is the exception handled at all? is false if ``is_propagated`` is true
    level: int  #: the level on which the exception is handled (1 = directly above, 0 = not handled)

    def __repr__(self):
        return "ExceptionResult(exception={}, is_propagated={}, is_handled={}, level={})".format(
            self.exception.fullname, self.is_propagated, self.is_handled, self.level
        )


@dataclass(frozen=True, repr=False)
class ContractReport:
    """Report about a contract's fulfillment."""

    contract: Contract
    context: Context
    results: Sequence[ExceptionResult]

    def __repr__(self):
        return "ContractReport(contract={}, context={}, results={})".format(
            self.contract,
            "Context(line={}, column={}, end_line={})".format(
                self.context.line, self.context.column, self.context.end_line
            ),
            self.results,
        )


@dataclass(frozen=True)
class CheckResult:
    """Result of a check for a single module."""

    source: BuildSource
    reports: Sequence[ContractReport]


def _is_unbound_callee(callee: Expression):
    return isinstance(callee, NameExpr) and callee.node is not None


def _resolve_member_expr(member) -> NameExpr:
    while isinstance(member, MemberExpr):
        member = member.expr
    return member


def _get_called_method(callee: MemberExpr, var: NameExpr) -> Optional[FuncDef]:
    if var.node is None or var.node.type is None or isinstance(var.node.type.type, FakeInfo):
        return None

    try:
        node = var.node.type.type.names[callee.name].node
        if isinstance(node, Decorator):
            return node.func
    except KeyError:
        pass

    return None


@mypyc_attr(allow_interpreted_subclasses=True)
class _ReportVisitor(_ResolveAliasVisitor):
    def __init__(self, source: BuildSource, contracts: Sequence[Contract], cache: _MypyCache):
        super().__init__()
        self.source = source
        self.contracts = contracts
        self.cache = cache
        self.reports: List[ContractReport] = []
        self.scope: List[Statement] = []

    def get_result(self):
        """Visit the underlying mypy file and create the result."""
        tree = self.cache.build.files[self.source.module]
        self.visit_mypy_file(tree)

        return CheckResult(self.source, self.reports)

    def visit_decorator(self, o: Decorator):
        self.scope.append(o)
        super().visit_decorator(o)
        self.scope.pop()

    def visit_func_def(self, o: FuncDef):
        self.scope.append(o)
        super().visit_func_def(o)
        self.scope.pop()

    def visit_try_stmt(self, o: TryStmt):
        self.scope.append(o)
        super().visit_try_stmt(o)
        self.scope.pop()

    def visit_if_stmt(self, o):
        self.scope.append(o)
        super().visit_if_stmt(o)
        self.scope.pop()

    def visit_for_stmt(self, o):
        self.scope.append(o)
        super().visit_for_stmt(o)
        self.scope.pop()

    def visit_while_stmt(self, o):
        self.scope.append(o)
        super().visit_while_stmt(o)
        self.scope.pop()

    def visit_with_stmt(self, o):
        self.scope.append(o)
        super().visit_with_stmt(o)
        self.scope.pop()

    def visit_call_expr(self, o: CallExpr):
        super().visit_call_expr(o)

        called_function = None
        if isinstance(o.callee, MemberExpr) and isinstance(o.callee.expr, NameExpr):
            called_function = _get_called_method(o.callee, _resolve_member_expr(o.callee))
        elif _is_unbound_callee(o.callee):
            called_function = self._resolve_unbound_callee(o.callee)

        if called_function is not None:
            self._check_contracts(o, called_function)

    def _resolve_unbound_callee(self, callee: NameExpr):
        resolved = self.resolve_alias(callee.node)
        if isinstance(resolved, Decorator):
            return resolved.func
        if isinstance(resolved, FuncDef):
            return resolved
        return None

    def _check_contracts(self, context: Context, function: FuncDef):
        for contract in self.contracts:
            if contract.function == function:
                results = [self._check_exception(e) for e in contract.exception_types]
                self.reports.append(ContractReport(contract, context, results))

    def _check_exception(self, exception: SymbolNode):
        scope = -1
        while scope >= -len(self.scope) and not isinstance(self.scope[scope], FuncDef):
            current_scope = self.scope[scope]
            if isinstance(current_scope, TryStmt) and self._is_handled(current_scope, exception):
                return ExceptionResult(exception, False, True, -scope)
            scope -= 1

        # instead of handling the exception, devs may want to propagate it further up the stack
        if scope > -len(self.scope):
            decorator = self.scope[scope - 1]
            if isinstance(decorator, Decorator) and self._is_propagated(decorator, exception):
                return ExceptionResult(exception, True, False, 0)

        return ExceptionResult(exception, False, False, 0)

    def _get_handled_exceptions(self, types: List[Expression]):
        for type_ in types:
            if isinstance(type_, TupleExpr):
                # except (Error1, Error2):
                yield from self._parse_tuple_expr(type_)
            elif isinstance(type_, NameExpr):
                # except Error:
                yield self.resolve_alias(type_.node)

    def _parse_tuple_expr(self, tup: TupleExpr):
        return [self.resolve_alias(name.node) for name in tup.items if isinstance(name, NameExpr)]

    def _is_handled(self, try_: TryStmt, exception: SymbolNode):
        return any(type_ == exception for type_ in self._get_handled_exceptions(try_.types))

    def _is_propagated(self, decorator: Decorator, exception: SymbolNode):
        return any(type_ == exception for type_ in _get_contract_exceptions(self, decorator))


def _check_contracts(
    contracts: Sequence[Contract], sources: Iterable[BuildSource], cache: _MypyCache
):
    for source in sources:
        yield _ReportVisitor(source, contracts, cache).get_result()
