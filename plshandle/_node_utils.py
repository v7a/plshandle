"""Mypy node utils."""

from typing import Any, List, Optional, TYPE_CHECKING

from mypy.types import Instance
from mypy.nodes import (
    Context,
    NameExpr,
    FuncDef,
    Decorator,
    CallExpr,
    Expression,
    TupleExpr,
    MemberExpr,
    RefExpr,
    TypeInfo,
    TypeAlias,
    TryStmt,
    Var,
)

if TYPE_CHECKING:
    from plshandle._resolve_alias import _ResolveAliasVisitor
else:
    _ResolveAliasVisitor = Any


_PLSHANDLE_QUALIFIER = "plshandle._decorator.plshandle"


def _resolve_type_info_from_ref(expr: RefExpr) -> Optional[TypeInfo]:
    if isinstance(expr.node, TypeAlias) and isinstance(expr.node.target, Instance):
        return expr.node.target.type
    if isinstance(expr.node, TypeInfo):
        return expr.node
    return None


def _is_exception_type(info: TypeInfo):
    return any(t.fullname == "builtins.BaseException" for t in info.mro)


def _check_type_info(info: Optional[TypeInfo], context: Context):
    if info and _is_exception_type(info):
        return info

    raise TypeError(
        "{}:{}: Type passed to plshandle is not an exception type".format(
            context.line, context.column
        )
    )


def _resolve_exception_types(deco: CallExpr):
    for arg in deco.args:
        if isinstance(arg, RefExpr):
            yield _check_type_info(_resolve_type_info_from_ref(arg), arg)


def _get_contract_exceptions(visitor: _ResolveAliasVisitor, decorator: Decorator):
    for deco in decorator.decorators:
        if (
            isinstance(deco, CallExpr)
            and isinstance(deco.callee, NameExpr)
            and deco.callee.node is not None
        ):
            # decorator might be an aliased plshandle.plshandle
            resolved_callee = visitor.resolve_alias(deco.callee.node)

            if resolved_callee.fullname == _PLSHANDLE_QUALIFIER:
                yield from _resolve_exception_types(deco)


def _is_unbound_callee(callee: Expression):
    return isinstance(callee, NameExpr) and callee.node is not None


def _resolve_member_expr(member) -> NameExpr:
    while isinstance(member, MemberExpr):
        member = member.expr
    return member


def _get_called_method(callee: MemberExpr, var: NameExpr) -> Optional[FuncDef]:
    try:
        node = var.node.type.type.names[callee.name].node
        if isinstance(node, Decorator):
            return node.func
        if isinstance(node, FuncDef):
            return node
    except (KeyError, TypeError, AttributeError):
        pass

    return None


def _resolve_unbound_callee(visitor: _ResolveAliasVisitor, callee: Expression):
    if isinstance(callee, CallExpr) and isinstance(callee.callee, NameExpr):
        pass  # node -> TypeInfo

    resolved = visitor.resolve_alias(callee.node)
    if isinstance(resolved, Decorator):
        return resolved.func
    if isinstance(resolved, FuncDef):
        return resolved
    if isinstance(resolved, TypeInfo):
        try:
            node = resolved.names["__init__"].node
            if isinstance(node, Decorator):
                return node.func
            if isinstance(node, FuncDef):
                return node
        except (KeyError, TypeError, AttributeError):
            return None
    if isinstance(resolved, Var):
        try:
            node = resolved.type.type.names["__call__"].node
            if isinstance(node, Decorator):
                return node.func
            if isinstance(node, FuncDef):
                return node
        except (KeyError, TypeError, AttributeError):
            return None

    return None


def _get_handled_exceptions(types: List[Expression]):
    for type_ in types:
        if isinstance(type_, TupleExpr):
            # except (Error1, Error2):
            yield from _resolve_types_from_tuple(type_)
        elif isinstance(type_, RefExpr):
            # except Error:
            yield _resolve_type_info_from_ref(type_)


def _get_called_function_from_call_expr(
    visitor: _ResolveAliasVisitor, call: CallExpr
) -> Optional[FuncDef]:
    if isinstance(call.callee, MemberExpr) and isinstance(call.callee.expr, NameExpr):
        return _get_called_method(call.callee, _resolve_member_expr(call.callee))
    if _is_unbound_callee(call.callee):
        return _resolve_unbound_callee(visitor, call.callee)
    return None


def _resolve_types_from_tuple(tup: TupleExpr):
    return [_resolve_type_info_from_ref(item) for item in tup.items if isinstance(item, RefExpr)]


def _is_exception_handled(try_: TryStmt, exception: TypeInfo):
    return any(type_ == exception for type_ in _get_handled_exceptions(try_.types))
