"""Gather modules from directories and packages."""

from importlib.util import find_spec
from pathlib import Path
import pkgutil
from typing import Iterable, Iterator, Optional

import setuptools

from mypy.build import BuildResult
from mypy.modulefinder import BuildSource


def _find_package_dir(package: str):
    spec = find_spec(package)
    if not spec or not spec.submodule_search_locations:
        raise FileNotFoundError("Cannot find location of package '{}'".format(package))
    return Path(spec.submodule_search_locations[0]).as_posix()


def _gather_modules_in(packages: Iterable[str]) -> Iterator[str]:
    for package in packages:
        for module_info in pkgutil.iter_modules([_find_package_dir(package)]):
            if not module_info.ispkg:
                yield "{}.{}".format(package, module_info.name)


def _gather_module_infos(modules: Iterable[str]) -> Iterator[BuildSource]:
    for module in modules:
        spec = find_spec(module)
        if spec and spec.origin and spec.origin != "builtin":
            with open(spec.origin, "r") as source:
                yield BuildSource(spec.origin, spec.name, source.read(), None)


def _gather_modules(directories: Iterable[str], packages: Iterable[str], modules: Iterable[str]):
    all_packages = list(packages)
    for directory in directories:
        native_dir = str(Path(directory))
        all_packages.extend(setuptools.find_namespace_packages(native_dir))

    yield from _gather_module_infos(_gather_modules_in(all_packages))
    yield from _gather_module_infos(modules)
