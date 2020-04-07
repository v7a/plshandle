"""Keep track of the scope so it can be traversed upwards."""

from typing import List, Iterator, Tuple

from mypy.nodes import Statement
from mypy.traverser import TraverserVisitor

from mypy_extensions import mypyc_attr


@mypyc_attr(allow_interpreted_subclasses=True)
class _TrackScopeVisitor(TraverserVisitor):
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
