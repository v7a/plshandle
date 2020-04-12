"""Test that types are correctly inferred from call expressions."""

from plshandle.tests import cli, transform_results, Result, Contract


def test_call_expression():
    """Assert that contracts are checked if the callee is a call expression itself."""
    args = ["-m", "test_call_expression.module"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_call_expression.module.Foo.method",
            scope="test_call_expression.module",
            line=34,
            results=(Result("builtins.KeyError", is_propagated=False, is_handled=True, level=1,),),
        ),
        Contract(
            function="test_call_expression.module.Foo.method",
            scope="test_call_expression.module",
            line=35,
            results=(Result("builtins.KeyError", is_propagated=False, is_handled=True, level=1,),),
        ),
    }
