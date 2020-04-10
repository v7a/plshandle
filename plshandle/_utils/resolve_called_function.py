"""Resolve the called function from a call expression."""

from typing import Dict, Optional

from mypy.types import Type, CallableType, Instance, Overloaded, FunctionLike, TypeType
from mypy.nodes import CallExpr, Expression, RefExpr, FuncDef, MemberExpr, Decorator, TypeInfo

from plshandle._visitors.alias_resolver import AliasResolver


def _resolve_ref(ref: RefExpr, resolver: AliasResolver):
    while isinstance(ref, MemberExpr):
        ref = ref.expr
    return resolver.resolve_alias(ref.node)


def _get_function_from_decorator(symbol) -> Optional[FuncDef]:
    if isinstance(symbol, Decorator):
        return symbol.func
    if isinstance(symbol, FuncDef):
        return symbol
    return None


def _get_function_from_ref(ref: RefExpr, resolver: AliasResolver) -> Optional[FuncDef]:
    # covers edge cases where mypy is not able to find the type of the underlying callee
    return _get_function_from_decorator(_resolve_ref(ref, resolver))


def _find_method(class_: TypeInfo, method: str) -> Optional[FuncDef]:
    for base in class_.mro:
        try:
            func = _get_function_from_decorator(base.names[method].node)
            if func:
                return func
        except (KeyError, AttributeError):
            pass  # o.k, function may be defined in subclass

    return None


def _get_method_name(expr: CallExpr) -> Optional[str]:
    # very special case, usually obj.method() is resolved through other means beforehand
    if isinstance(expr.callee, MemberExpr):  # pragma: no cover
        return expr.callee.name
    return None


def _resolve_callable(
    callable_: CallableType, original_expr: Optional[CallExpr] = None
) -> Optional[FuncDef]:
    if callable_.definition:
        return callable_.definition
    if callable_.bound_args:
        arg = callable_.bound_args[0]
        if isinstance(arg, TypeType) and isinstance(arg.item, Instance):
            return _find_method(arg.item.type, _get_method_name(original_expr) or "__init__")
        if isinstance(arg, Instance):
            return _find_method(arg.type, _get_method_name(original_expr) or "__call__")

    return None


def _get_function_from_type(type_: Type, original_expr: Optional[CallExpr] = None):
    if isinstance(type_, Instance):
        return _find_method(type_.type, _get_method_name(original_expr) or "__call__")
    if isinstance(type_, FunctionLike):
        if isinstance(type_, Overloaded):
            type_ = type_.items()[0]
        # just in case Python ever receives another function-like statement
        if isinstance(type_, CallableType):  # pragma: no branch
            return _resolve_callable(type_, original_expr)

    return None


def resolve_called_function(
    call: CallExpr, resolver: AliasResolver, types: Dict[Expression, Type]
) -> Optional[FuncDef]:
    """Resolve the called function from a call expression."""
    if isinstance(call.callee, RefExpr):
        func = _get_function_from_ref(call.callee, resolver)
        if func:
            return func

    try:
        return _get_function_from_type(types[call.callee], call)
    except KeyError:  # pragma: no cover # rare edge case
        return None
