"""Keep track of the scope so it can be traversed upwards."""

from typing import List, Iterator, Tuple

from mypy.nodes import Statement, FuncDef, ClassDef, SymbolNode
from mypy.traverser import TraverserVisitor

from mypy_extensions import mypyc_attr


@mypyc_attr(allow_interpreted_subclasses=True)
class ScopeTracker(TraverserVisitor):
    """Keep track of the scope so it can be traversed upwards."""

    def __init__(self):
        super().__init__()
        self.scope: List[Statement] = []

    def visit_decorator(self, o):
        self.scope.append(o)
        super().visit_decorator(o)
        self.scope.pop()

    def visit_func_def(self, o):
        self.scope.append(o)
        super().visit_func_def(o)
        self.scope.pop()

    def visit_try_stmt(self, o):
        self.scope.append(o)
        super().visit_try_stmt(o)
        self.scope.pop()

    def visit_if_stmt(self, o):
        self.scope.append(o)
        super().visit_if_stmt(o)
        self.scope.pop()

    def visit_for_stmt(self, o):
        self.scope.append(o)
        super().visit_for_stmt(o)
        self.scope.pop()

    def visit_while_stmt(self, o):
        self.scope.append(o)
        super().visit_while_stmt(o)
        self.scope.pop()

    def visit_with_stmt(self, o):
        self.scope.append(o)
        super().visit_with_stmt(o)
        self.scope.pop()

    def traverse_scope(self) -> Iterator[Tuple[Statement, int]]:
        """Traverse the current scope upwards."""
        level = 1
        for scope in reversed(self.scope):
            yield scope, level
            level += 1

    def determine_current_node(self, fallback: SymbolNode) -> SymbolNode:
        """Determine the current node, that is a function or class. The fallback is used if not
        in a function nor in a class definition.
        """
        for stmt, _ in self.traverse_scope():
            if isinstance(stmt, (FuncDef, ClassDef)):
                return stmt

        return fallback
