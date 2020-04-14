"""Check whether all contracts are fulfilled in all modules."""

from dataclasses import dataclass
from typing import Sequence, List

from mypy.modulefinder import BuildSource
from mypy.nodes import Context, FuncDef, TryStmt, Decorator, CallExpr, SymbolNode, TypeInfo

from mypy_extensions import mypyc_attr

from plshandle._cache import MypyCache
from plshandle._visitors.contract_collector import Contract
from plshandle._visitors.alias_resolver import AliasResolver
from plshandle._visitors.scope_tracker import ScopeTracker
from plshandle._ast_utils.resolve_called_functions import resolve_called_functions
from plshandle._ast_utils.resolve_contract import resolve_contract
from plshandle._ast_utils.resolve_handled_types import resolve_handled_types


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


@dataclass(init=False)
class _CheckerState:
    # ugly per-source state
    module: str
    root: SymbolNode
    reports: List[ContractReport]

    def __init__(self, source: BuildSource, cache: MypyCache):
        self.module = source.module
        self.root = cache.build.files[source.module]
        self.reports = []


@mypyc_attr(allow_interpreted_subclasses=True)
class ContractChecker(ScopeTracker, AliasResolver):
    """Check whether all contracts are fulfilled in all modules."""

    def __init__(
        self, contracts: Sequence[Contract], sources: Sequence[BuildSource], cache: MypyCache
    ):
        super().__init__()
        self.contracts = contracts
        self.cache = cache
        self.results: List[CheckResult] = []

        # traverse all nodes and populate self.results
        for source in sources:
            self.current_state = _CheckerState(source, cache)
            self.visit_mypy_file(self.current_state.root)
            self.results.append(CheckResult(source, self.current_state.reports))

    def visit_call_expr(self, o: CallExpr):
        super().visit_call_expr(o)

        functions = tuple(resolve_called_functions(o, self, self.cache.build.types))
        self.current_state.reports.extend(self._get_reports(o, functions))

    def _is_propagated(self, decorator: Decorator, exception: TypeInfo):
        return any(
            type_ == exception
            for type_ in resolve_contract(
                decorator, self, self.cache.build.types, self.current_state.module
            )
        )

    def _is_handled(self, try_: TryStmt, exception: TypeInfo):
        return any(
            type_ == exception
            for type_ in resolve_handled_types(
                try_, self.cache.build.types, self.current_state.module
            )
        )

    def _check_exception(self, exception: TypeInfo):
        for stmt, level in self.traverse_scope():
            if isinstance(stmt, TryStmt) and self._is_handled(stmt, exception):
                return ExceptionResult(exception, False, True, level)
            if isinstance(stmt, Decorator) and self._is_propagated(stmt, exception):
                return ExceptionResult(exception, True, False, 0)

        return ExceptionResult(exception, False, False, 0)

    def _get_reports(self, context: Context, functions: Sequence[FuncDef]):
        for contract in self.contracts:
            if contract.function in functions:
                yield ContractReport(
                    contract,
                    context,
                    self.determine_current_node(self.current_state.root),
                    [self._check_exception(e) for e in contract.exception_types],
                )
