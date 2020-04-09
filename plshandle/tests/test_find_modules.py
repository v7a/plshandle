"""Checks whether or not all the packages, subpackages and modules are found."""

from pathlib import Path

import pytest

from plshandle.tests import cli, resource


def test_find_modules():
    """Assert that all packages, subpackages and modules are found."""
    args = [
        "-d",
        str(resource("test_find_modules", "dir")),
        "-p",
        "test_find_modules.package",
        "-m",
        "test_find_modules.free_module",
    ]
    collected_modules = {Path(x.path) for x in cli(args).modules}
    assert collected_modules == {
        resource("test_find_modules", "free_module.py"),
        resource("test_find_modules", "package", "module.py"),
        resource("test_find_modules", "dir", "package1", "module1.py"),
        resource("test_find_modules", "dir", "package1", "module2.py"),
        resource("test_find_modules", "dir", "package2", "module3.py"),
        resource("test_find_modules", "dir", "package2", "subpackage", "module4.py"),
    }


def test_invalid_package():
    """Assert that FNF is raised if a package cannot be found."""
    with pytest.raises(FileNotFoundError):
        cli(["-p", "invalidpackagename"])


def test_invalid_module():
    """Assert that MNF is raised if a module cannot be found."""
    with pytest.raises(ModuleNotFoundError):
        cli(["-m", "invalidpackage.invalidmodule"])
