"""Simple test checking whether or not some of the exceptions were handled."""

from plshandle.tests import cli, transform_results, Result, Contract


def test_simple():
    """Assert that contracts are handled as described in resources/test_simple/module.py."""
    args = ["-m", "test_simple.module"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_simple.module.foo",
            scope="test_simple.module.Bar.__init__",
            line=16,
            results=(
                Result("builtins.KeyError", is_propagated=True, is_handled=False, level=0),
                Result(
                    "test_simple.module.CustomError", is_propagated=False, is_handled=False, level=0
                ),
            ),
        ),
        Contract(
            function="test_simple.module.foo",
            scope="test_simple.module.Bar.__init__",
            line=19,
            results=(
                Result("builtins.KeyError", is_propagated=True, is_handled=False, level=0),
                Result(
                    "test_simple.module.CustomError", is_propagated=False, is_handled=True, level=1
                ),
            ),
        ),
        Contract(
            function="test_simple.module.foo",
            scope="test_simple.module.Bar.__init__",
            line=27,
            results=(
                Result("builtins.KeyError", is_propagated=False, is_handled=True, level=2),
                Result(
                    "test_simple.module.CustomError", is_propagated=False, is_handled=True, level=2
                ),
            ),
        ),
    }
