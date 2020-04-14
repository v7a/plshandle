"""Resolve a contract from a decorator."""

from typing import Dict, Iterator, Optional

from mypy.types import Type
from mypy.nodes import Context, CallExpr, Expression, Decorator, TypeInfo

from plshandle._visitors.alias_resolver import AliasResolver
from plshandle._ast_utils.resolve_called_functions import resolve_called_functions
from plshandle._ast_utils.resolve_exception_types import resolve_exception_types


_PLSHANDLE_QUALIFIER = "plshandle._decorator.plshandle"


def _get_exception_types(
    call: CallExpr, types: Dict[Expression, Type], context: Optional[Context], module: Optional[str]
):
    for arg in call.args:
        try:
            yield from resolve_exception_types(types[arg], context, module)
        except KeyError:  # pragma: no cover
            pass  # o.k., might be code that does not even concern us


def resolve_contract(
    decorator: Decorator, resolver: AliasResolver, types: Dict[Expression, Type], module: str
) -> Iterator[TypeInfo]:
    """Resolve a contract from a decorator. Yields all provided exception types. Yields nothing if
    no contract was defined.
    """
    for call in decorator.decorators:
        if isinstance(call, CallExpr):
            for function in resolve_called_functions(call, resolver, types):
                if function.fullname == _PLSHANDLE_QUALIFIER:
                    yield from _get_exception_types(call, types, decorator, module)
