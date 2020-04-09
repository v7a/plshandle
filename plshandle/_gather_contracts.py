"""Gather contracts defined in modules."""

from dataclasses import dataclass
from typing import Iterable, List

from mypy.modulefinder import BuildSource
from mypy.nodes import FuncDef, Decorator, TypeInfo

from mypy_extensions import mypyc_attr

from plshandle._cache import _MypyCache
from plshandle._resolve_alias import _ResolveAliasVisitor
from plshandle._node_utils import _get_contract_exceptions


@dataclass(frozen=True, repr=False)
class Contract:
    """Contract created by ``function``, requires handling ``exception_types``."""

    source: BuildSource
    function: FuncDef
    exception_types: Iterable[TypeInfo]

    def __repr__(self):
        return "_Contract(source={}, function={}, exception_types={})".format(
            self.source,
            self.function.fullname,
            "[{}]".format(", ".join([t.fullname for t in self.exception_types])),
        )


@mypyc_attr(allow_interpreted_subclasses=True)
class _ContractVisitor(_ResolveAliasVisitor):
    def __init__(self, source: BuildSource, cache: _MypyCache):
        super().__init__()
        self.source = source
        self.cache = cache
        self.contracts: List[Contract] = []

    def get_contracts(self):
        """Visit the underlying mypy file and return all contracts found in it."""
        self.visit_mypy_file(self.cache.build.files[self.source.module])
        return self.contracts

    def visit_decorator(self, o: Decorator):
        super().visit_decorator(o)
        types = tuple(_get_contract_exceptions(self, o))
        if types:
            self.contracts.append(Contract(self.source, o.func, types))


def _gather_contracts(sources: Iterable[BuildSource], cache: _MypyCache):
    for source in sources:
        yield from _ContractVisitor(source, cache).get_contracts()
