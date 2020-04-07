"""Mypy node utils."""

from typing import List, Optional

from mypy.nodes import (
    NameExpr,
    FuncDef,
    Decorator,
    CallExpr,
    Expression,
    TupleExpr,
    MemberExpr,
)

from plshandle._resolve_alias import _ResolveAliasVisitor


_PLSHANDLE_QUALIFIER = "plshandle._decorator.plshandle"


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
                yield from [
                    visitor.resolve_alias(arg.node)
                    for arg in deco.args
                    if isinstance(arg, NameExpr) and arg.node is not None
                ]


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
        # type not of instance TypeInfo, names does not exist or method does not exist
        pass

    return None


def _resolve_unbound_callee(visitor: _ResolveAliasVisitor, callee: NameExpr):
    resolved = visitor.resolve_alias(callee.node)
    if isinstance(resolved, Decorator):
        return resolved.func
    if isinstance(resolved, FuncDef):
        return resolved
    return None


def _get_handled_exceptions(visitor: _ResolveAliasVisitor, types: List[Expression]):
    for type_ in types:
        if isinstance(type_, TupleExpr):
            # except (Error1, Error2):
            yield from _parse_tuple_expr(visitor, type_)
        elif isinstance(type_, NameExpr):
            # except Error:
            yield visitor.resolve_alias(type_.node)


def _get_called_function_from_call_expr(
    visitor: _ResolveAliasVisitor, call: CallExpr
) -> Optional[FuncDef]:
    if isinstance(call.callee, MemberExpr) and isinstance(call.callee.expr, NameExpr):
        return _get_called_method(call.callee, _resolve_member_expr(call.callee))
    if _is_unbound_callee(call.callee):
        return _resolve_unbound_callee(visitor, call.callee)
    return None


def _parse_tuple_expr(visitor: _ResolveAliasVisitor, tup: TupleExpr):
    return [visitor.resolve_alias(name.node) for name in tup.items if isinstance(name, NameExpr)]
