"""Gather modules from directories and packages."""

from importlib.util import find_spec
from pathlib import Path
import pkgutil
from typing import Iterable, Iterator, List

import setuptools

from mypy.modulefinder import BuildSource


def _find_package_dirs(package: str):
    spec = find_spec(package)
    if not spec or not spec.submodule_search_locations:
        raise FileNotFoundError("Cannot find location of package '{}'".format(package))
    return spec.submodule_search_locations


def _gather_modules_in(packages: Iterable[str], package_roots: List[str]) -> Iterator[str]:
    for package in packages:
        dirs = _find_package_dirs(package)
        package_roots.extend(dirs)
        for module_info in pkgutil.iter_modules([Path(x).as_posix() for x in dirs]):
            if not module_info.ispkg:
                yield "{}.{}".format(package, module_info.name)


def _gather_module_infos(modules: Iterable[str]) -> Iterator[BuildSource]:
    for module in modules:
        spec = find_spec(module)
        if spec and spec.origin and spec.origin != "builtin":
            yield BuildSource(spec.origin, spec.name, None, None)


def _gather_modules(
    directories: Iterable[str],
    packages: Iterable[str],
    modules: Iterable[str],
    package_roots: List[str],
):
    all_packages = list(packages)
    for directory in directories:
        native_dir = str(Path(directory))
        all_packages.extend(setuptools.find_namespace_packages(native_dir))

    yield from _gather_module_infos(_gather_modules_in(all_packages, package_roots))
    yield from _gather_module_infos(modules)
