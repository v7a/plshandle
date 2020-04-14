"""Collect contracts defined in modules."""

from dataclasses import dataclass
from typing import Iterable, List

from mypy.modulefinder import BuildSource
from mypy.nodes import FuncDef, Decorator, TypeInfo

from mypy_extensions import mypyc_attr

from plshandle._cache import MypyCache
from plshandle._visitors.alias_resolver import AliasResolver
from plshandle._ast_utils.resolve_contract import resolve_contract


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
class ContractCollector(AliasResolver):
    """Collect contracts defined in the given sources."""

    def __init__(self, sources: Iterable[BuildSource], cache: MypyCache):
        super().__init__()
        self.types = cache.build.types
        self.contracts: List[Contract] = []

        # traverse all nodes and populate self.contracts
        for source in sources:
            self.source = source
            self.visit_mypy_file(cache.build.files[source.module])

    def visit_decorator(self, o: Decorator):
        super().visit_decorator(o)
        types = tuple(resolve_contract(o, self, self.types, self.source.module))
        if types:
            self.contracts.append(Contract(self.source, o.func, types))
