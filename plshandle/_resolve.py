"""Resolve the fully qualified names of AST nodes and aliases."""

import ast
from typing import Dict


def _resolve_attribute(node: ast.Attribute):
    qualified_name = [node.attr]
    while True:
        node = node.value  # type: ignore
        if isinstance(node, ast.Name):
            return ".".join([node.id] + list(reversed(qualified_name)))

        qualified_name.append(node.attr)


def _resolve_alias(alias: str, aliases: Dict[str, str]):
    old_root = ""
    alias_parts = alias.split(".")
    while old_root != alias_parts[0] and alias_parts[0] in aliases:
        old_root = alias_parts[0]
        alias_parts[:1] = aliases[old_root].split(".")
    return ".".join(alias_parts)


def _resolve_function(node: ast.FunctionDef, module_name: str, parents: Dict[ast.AST, ast.AST]):
    qualified_name = [node.name]
    while True:
        node = parents[node]  # type: ignore
        if isinstance(node, ast.Module):
            return ".".join([module_name] + list(reversed(qualified_name)))

        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            qualified_name.append(node.name)
