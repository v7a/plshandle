"""Attempt to resolve a Type[BaseException] from a mypy.types.Type."""

from typing import Optional, Iterator

from mypy.types import Type, Instance, TypeType, TupleType, CallableType, Overloaded
from mypy.nodes import Context, TypeInfo


def _is_exception_type(type_: TypeInfo):
    return any(sub.fullname == "builtins.BaseException" for sub in type_.mro)  # pragma: no branch


def _raise_invalid_type(type_: Type, context: Optional[Context], module: Optional[str]):
    raise TypeError(
        "{}:{}: Invalid exception type '{}'".format(
            module or "?", context.line if context else "?", type_
        )
    )


def resolve_exception_types(
    type_: Type, context: Optional[Context], module: Optional[str]
) -> Iterator[TypeInfo]:
    """Attempt to resolve a Type[BaseException] or Tuple[Type[BaseException], ...] (nested) from a
    mypy.types.Type. Raises ``TypeError`` if failed to resolve.
    """
    if isinstance(type_, Overloaded):
        type_ = type_.items()[0]
    if isinstance(type_, CallableType):
        type_ = TypeType(type_.ret_type, line=type_.line, column=type_.column)

    if isinstance(type_, TupleType):
        for item in type_.items:  # pragma: no branch
            yield from resolve_exception_types(item, context, module)
    elif isinstance(type_, TypeType) and isinstance(type_.item, Instance):  # pragma: no branch
        if _is_exception_type(type_.item.type):
            yield type_.item.type
        else:
            _raise_invalid_type(type_, context, module)
