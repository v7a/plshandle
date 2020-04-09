"""Resolve aliases while keeping the scope in mind."""

from functools import reduce
from typing import List, Dict

from mypy.nodes import NameExpr, FuncDef, AssignmentStmt, SymbolNode, RefExpr
from mypy.traverser import TraverserVisitor

from mypy_extensions import mypyc_attr


@mypyc_attr(allow_interpreted_subclasses=True)
class AliasResolver(TraverserVisitor):
    """Resolve aliases while keeping the scope in mind."""

    def __init__(self):
        super().__init__()
        self.alias_scopes: List[Dict[SymbolNode, SymbolNode]] = [{}]

    def visit_func_def(self, o: FuncDef):
        self.alias_scopes.append({})
        super().visit_func_def(o)
        self.alias_scopes.pop()

    def visit_assignment_stmt(self, o: AssignmentStmt):
        super().visit_assignment_stmt(o)

        if (
            len(o.lvalues) == 1
            and isinstance(o.lvalues[0], NameExpr)
            and o.lvalues[0].node is not None
            and isinstance(o.rvalue, RefExpr)
            and o.rvalue.node is not None
        ):
            self.alias_scopes[-1][o.lvalues[0].node] = o.rvalue.node

    def resolve_alias(self, alias: SymbolNode):
        """Resolve the given node alias or returns itself if no alias."""
        all_aliases = reduce(lambda x, y: {**x, **y}, self.alias_scopes)
        while alias in all_aliases:
            alias = all_aliases[alias]
        return alias
