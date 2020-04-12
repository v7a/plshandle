"""Test contract checking when unions are involved."""

from plshandle.tests import cli, transform_results, Result, Contract


def test_unions():
    """Assert that contracts are checked for all types in a union."""
    args = ["-m", "test_unions.module"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_unions.module.Foo.__init__",
            scope="test_unions.module",
            line=24,
            results=(Result("builtins.KeyError", is_propagated=False, is_handled=True, level=1,),),
        ),
        Contract(
            function="test_unions.module.Foo.__call__",
            scope="test_unions.module",
            line=24,
            results=(
                Result("builtins.AttributeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_unions.module.Bar.foo",
            scope="test_unions.module",
            line=30,
            results=(Result("builtins.TypeError", is_propagated=False, is_handled=True, level=1,),),
        ),
    }
