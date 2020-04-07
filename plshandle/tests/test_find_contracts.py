"""Checks whether or not all contracts in all modules are found."""

from plshandle.tests import cli


def test_find_contracts():
    """Assert that all contracts are found, even if the decorator is aliased."""
    args = ["-m", "test_find_contracts.module1", "-m", "test_find_contracts.module2"]
    collected_contracts = {
        (x.source.module, x.function.fullname, tuple(y.fullname for y in x.exception_types))
        for x in cli(args).contracts
    }
    assert collected_contracts == {
        ("test_find_contracts.module1", "test_find_contracts.module1.foo", ("builtins.KeyError",)),
        (
            "test_find_contracts.module1",
            "test_find_contracts.module1.Bar.__init__",
            ("builtins.AttributeError", "test_find_contracts.module1.CustomError"),
        ),
        (
            "test_find_contracts.module1",
            "test_find_contracts.module1.Bar.__call__",
            ("builtins.KeyError",),
        ),
        (
            "test_find_contracts.module2",
            "test_find_contracts.module2.bar",
            ("builtins.KeyError", "builtins.TypeError"),
        ),
    }
