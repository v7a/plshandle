"""Resolve the called function from a call expression."""

from typing import Dict, Optional, Iterator, Tuple, Union

from mypy.nodes import (
    CallExpr,
    Expression,
    RefExpr,
    FuncDef,
    MemberExpr,
    Decorator,
    TypeInfo,
    NameExpr,
)
from mypy.types import (
    Type,
    CallableType,
    Instance,
    Overloaded,
    FunctionLike,
    TypeType,
    UnionType,
)

from plshandle._visitors.alias_resolver import AliasResolver


def _resolve_ref(ref: Expression) -> Optional[Expression]:
    while isinstance(ref, MemberExpr):
        ref = ref.expr
    return ref


def _get_function_from_node(symbol) -> Optional[FuncDef]:
    if isinstance(symbol, Decorator):
        return symbol.func
    if isinstance(symbol, FuncDef):
        return symbol
    return None


def _get_function_from_ref(ref: Expression, resolver: AliasResolver) -> Optional[FuncDef]:
    ref = _resolve_ref(ref)
    if isinstance(ref, RefExpr):
        return _get_function_from_node(resolver.resolve_alias(ref.node))
    return None


def _resolve_unbound_function(callee: Expression, resolver: AliasResolver) -> Optional[FuncDef]:
    return _get_function_from_ref(callee, resolver)


def _try_find_in_type_map(callee: Expression, types: Dict[Expression, Type]) -> Optional[Type]:
    try:
        if isinstance(callee, MemberExpr):
            callee = callee.expr
        return types[callee]
    except KeyError:  # pragma: no cover
        return None


def _type_info_from_expr(expr: Expression) -> Optional[TypeInfo]:
    if isinstance(expr, NameExpr) and isinstance(expr.node, TypeInfo):
        return expr.node
    return None


def _try_resolve_method_call(callee: Expression) -> Optional[Type]:
    # Mypy does not infer the type of expression ``Class()`` correctly if __init__ it is not in
    # mro[0] (maybe that is intended behavior), so manually resolve it. TBD: maybe assist mypy
    # and store it in type map beforehand?

    if isinstance(callee, MemberExpr):
        callee = callee.expr

    if isinstance(callee, CallExpr):
        info = _type_info_from_expr(callee.callee)  # Class()() and Class().method()
        if info:  # pragma: no branch
            return Instance(info, [])
    else:
        info = _type_info_from_expr(callee)
        if info:
            return TypeType(Instance(info, []))  # Class() and Class.method()

    return None


def _find_callee_type(callee: Expression, types: Dict[Expression, Type]) -> Optional[Type]:
    return _try_resolve_method_call(callee) or _try_find_in_type_map(callee, types)


def _resolve_class_types(
    type_: Union[Type, TypeInfo], fallback_method: str = "__init__"
) -> Iterator[Tuple[TypeInfo, Optional[str]]]:
    # mypy states they do not use this type yet, uncomment once they do
    # if isinstance(type_, TypeAliasType):
    #    type_ = type_.expand_all_if_possible()

    if isinstance(type_, TypeInfo):
        yield type_, fallback_method
    else:
        if isinstance(type_, Instance):
            yield from _resolve_class_types(type_.type, "__call__")
        elif isinstance(type_, TypeType):
            yield from _resolve_class_types(type_.item.type, "__init__")
        elif isinstance(type_, UnionType):
            for item in type_.items:
                yield from _resolve_class_types(item, fallback_method)
        elif isinstance(type_, FunctionLike):  # pragma: no branch
            if isinstance(type_, Overloaded):  # pragma: no branch
                type_ = type_.items()[0]
            # just in case Python ever receives another function-like statement
            if isinstance(type_, CallableType):  # pragma: no branch
                yield from _resolve_class_types(type_.ret_type, fallback_method)


def _try_get_callee_method(callee: Expression) -> Optional[str]:
    if isinstance(callee, MemberExpr):
        return callee.name
    return None


def _find_method(class_: TypeInfo, method: str) -> Optional[FuncDef]:
    for base in class_.mro:
        try:
            func = _get_function_from_node(base.names[method].node)
            if func:
                return func
        except (KeyError, AttributeError):
            pass  # o.k, function may be defined in subclass

    return None


def _find_methods(type_: Type, callee: Expression) -> Iterator[FuncDef]:
    for class_, fallback_method in _resolve_class_types(type_):
        method = _find_method(class_, _try_get_callee_method(callee) or fallback_method)
        if method:
            yield method


def _resolve_bound_functions(
    callee: Expression, types: Dict[Expression, Type]
) -> Iterator[FuncDef]:
    yield from _find_methods(_find_callee_type(callee, types), callee)


def resolve_called_functions(
    call: CallExpr, resolver: AliasResolver, types: Dict[Expression, Type]
) -> Iterator[FuncDef]:
    """Yield the called functions from a call expression. This might yield multiple functions
    since the underlying callee might be an union type.
    """

    function = _resolve_unbound_function(call.callee, resolver)
    if function:
        yield function
    else:
        yield from _resolve_bound_functions(call.callee, types)
