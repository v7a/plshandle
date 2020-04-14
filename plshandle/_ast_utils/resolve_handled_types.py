"""Resolve handled types in a try statement."""

from typing import Dict, Iterator

from mypy.types import Type
from mypy.nodes import Expression, TypeInfo, TryStmt

from plshandle._ast_utils.resolve_exception_types import resolve_exception_types


def resolve_handled_types(
    try_: TryStmt, types: Dict[Expression, Type], module: str
) -> Iterator[TypeInfo]:
    """Yield handled exception types in a try statement."""
    for handler_type, handler_context in zip(try_.types, try_.handlers):
        try:
            yield from resolve_exception_types(types[handler_type], handler_context, module)
        except KeyError:  # pragma: no cover
            pass  # o.k., might be code that does not even concern us
