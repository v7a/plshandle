"""Gather contracts defined in modules."""

import ast
from dataclasses import dataclass
import inspect
from importlib import import_module
from typing import Iterable, Iterator, Dict

from plshandle._gather_modules import _Module
from plshandle._resolve import _resolve_alias, _resolve_attribute, _resolve_function


_DECORATOR_QUALIFIED_NAME = "plshandle.plshandle"


@dataclass(frozen=True)
class _Contract:
    module: _Module
    function: str
    exception_types: Iterable[str]


def _get_import_aliases(node: ast.Import):
    return {alias.asname: alias.name for alias in node.names if alias.asname}


def _get_import_from_aliases(node: ast.ImportFrom):
    return {
        alias.asname or alias.name: "{}.{}".format(node.module, alias.name) for alias in node.names
    }


def _get_assign_aliases(node: ast.Assign):
    if isinstance(node.value, ast.Name):
        value = node.value.id
    elif isinstance(node.value, ast.Attribute):
        value = _resolve_attribute(node.value)
    else:
        return {}

    return {target.id: value for target in node.targets if isinstance(target, ast.Name)}


def _get_eligible_decorators(node: ast.FunctionDef, aliases: Dict[str, str]):
    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and _resolve_alias(decorator.func.id, aliases) == _DECORATOR_QUALIFIED_NAME
        ):
            yield decorator


def _get_required_exceptions(decorators: Iterable[ast.Call], aliases: Dict[str, str]):
    for decorator in decorators:
        for arg in decorator.args:
            if isinstance(arg, ast.Name):
                yield _resolve_alias(arg.id, aliases)


def _find_contracts(module: _Module, tree: ast.AST) -> Iterator[_Contract]:
    parents: Dict[ast.AST, ast.AST] = {}
    aliases: Dict[str, str] = {}

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

            if isinstance(child, ast.Import):
                aliases.update(_get_import_aliases(child))
            elif isinstance(child, ast.ImportFrom):
                aliases.update(_get_import_from_aliases(child))
            elif isinstance(child, ast.Assign):
                aliases.update(_get_assign_aliases(child))
            elif isinstance(child, ast.FunctionDef):
                types = tuple(
                    _get_required_exceptions(_get_eligible_decorators(child, aliases), aliases)
                )
                if types:
                    yield _Contract(
                        module, _resolve_function(child, module.full_name, parents), types
                    )


def _gather_contracts(modules: Iterable[_Module]):
    for module in modules:
        module_inst = import_module(str(module.full_name))
        try:
            tree = ast.parse(inspect.getsource(module_inst))
            yield from _find_contracts(module, tree)
        except OSError:
            pass  # o.k. may happen if the module is empty
