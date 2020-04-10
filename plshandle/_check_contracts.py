"""Check whether all contracts are fulfilled in all modules."""

from dataclasses import dataclass
from typing import Iterable, Sequence, List

from mypy.modulefinder import BuildSource
from mypy.nodes import Context, FuncDef, TryStmt, Decorator, CallExpr, SymbolNode, TypeInfo

from mypy_extensions import mypyc_attr

from plshandle._cache import _MypyCache
from plshandle._gather_contracts import Contract
from plshandle._visitors.alias_resolver import AliasResolver
from plshandle._visitors.scope_tracker import ScopeTracker
from plshandle._utils.resolve_called_function import resolve_called_function
from plshandle._utils.resolve_contract import resolve_contract
from plshandle._utils.resolve_handled_types import resolve_handled_types


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
    scope: SymbolNode
    results: Sequence[ExceptionResult]

    def __repr__(self):
        return "ContractReport(contract={}, context={}, scope={}, results={})".format(
            self.contract,
            "Context(line={}, column={}, end_line={})".format(
                self.context.line, self.context.column, self.context.end_line
            ),
            self.scope.fullname,
            self.results,
        )


@dataclass(frozen=True)
class CheckResult:
    """Result of a check for a single module."""

    source: BuildSource
    reports: Sequence[ContractReport]


@mypyc_attr(allow_interpreted_subclasses=True)
class _ReportVisitor(ScopeTracker, AliasResolver):
    def __init__(self, source: BuildSource, contracts: Sequence[Contract], cache: _MypyCache):
        ScopeTracker.__init__(self, cache.build.files[source.module])
        AliasResolver.__init__(self)
        self.source = source
        self.contracts = contracts
        self.cache = cache
        self.reports: List[ContractReport] = []

    def get_result(self):
        """Visit the underlying mypy file and create the result."""
        self.visit_mypy_file(self.root)

        return CheckResult(self.source, self.reports)

    def visit_call_expr(self, o: CallExpr):
        super().visit_call_expr(o)

        called_function = resolve_called_function(o, self, self.cache.build.types)
        if called_function is not None:
            self.reports.extend(self._get_reports(o, called_function))

    def _is_propagated(self, decorator: Decorator, exception: TypeInfo):
        return any(
            type_ == exception
            for type_ in resolve_contract(
                decorator, self, self.cache.build.types, self.source.module
            )
        )

    def _is_handled(self, try_: TryStmt, exception: TypeInfo):
        return any(
            type_ == exception
            for type_ in resolve_handled_types(try_, self.cache.build.types, self.source.module)
        )

    def _check_exception(self, exception: TypeInfo):
        for stmt, level in self.traverse_scope():
            if isinstance(stmt, TryStmt) and self._is_handled(stmt, exception):
                return ExceptionResult(exception, False, True, level)
            if isinstance(stmt, Decorator) and self._is_propagated(stmt, exception):
                return ExceptionResult(exception, True, False, 0)

        return ExceptionResult(exception, False, False, 0)

    def _get_reports(self, context: Context, function: FuncDef):
        for contract in self.contracts:
            if contract.function == function:
                results = [self._check_exception(e) for e in contract.exception_types]
                yield ContractReport(contract, context, self.determine_current_node(), results)


def _check_contracts(
    contracts: Sequence[Contract], sources: Iterable[BuildSource], cache: _MypyCache
):
    for source in sources:
        yield _ReportVisitor(source, contracts, cache).get_result()
