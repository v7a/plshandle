"""Gather contracts defined in modules."""

from dataclasses import dataclass
from functools import partial
from typing import Iterable, List, Optional, Dict
from types import MethodType

from mypy.build import build, BuildResult
from mypy.errors import Errors
from mypy.modulefinder import BuildSource
from mypy.nodes import Expression, NameExpr, FuncDef, Decorator
from mypy.options import Options
from mypy.plugin import Plugin
from mypy.traverser import TraverserVisitor
from mypy.types import Type

from mypy_extensions import mypyc_attr


_DECORATOR_QUALIFIED_NAME = "plshandle.plshandle"


@dataclass
class MypyCache:
    """Mutable object that contains the mypy build result after gathering contracts."""

    build: Optional[BuildResult] = None


@dataclass(frozen=True)
class _Contract:
    source: BuildSource
    function: FuncDef
    exception_types: Iterable[NameExpr]


def _visit_decorator(
    source: BuildSource,
    types: Dict[Expression, Type],
    contracts: List[_Contract],
    self,
    decorator: Decorator,
):
    print("halo")
    TraverserVisitor.visit_decorator(self, decorator)


def _gather_contracts(sources: Iterable[BuildSource], cache: MypyCache):
    options = Options()
    options.preserve_asts = True
    options.export_types = True
    cache.build = build(list(sources), options)

    for source in sources:
        contracts: List[_Contract] = []
        visitor = TraverserVisitor()
        visit_func = partial(_visit_decorator, source, cache.build.types, contracts)
        visitor.visit_decorator = MethodType(visit_func, visitor)
        visitor.visit_mypy_file(cache.build.files[source.module])
        yield from contracts
