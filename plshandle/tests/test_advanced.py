"""Advanced test testing all the nasty stuff: aliases, special methods, ..."""

from plshandle.tests import cli, transform_results, Result, Contract


def test_advanced():
    """Assert that contracts are handled as described in resources/test_advanced/app.py."""
    args = ["-p", "test_advanced"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_advanced.utils.foo",
            scope="test_advanced.app",
            line=15,
            results=(
                Result(
                    "test_advanced.errors.CustomError",
                    is_propagated=False,
                    is_handled=True,
                    level=4,
                ),
            ),
        ),
        Contract(
            function="test_advanced.utils.Bar.__call__",
            scope="test_advanced.app",
            line=21,
            results=(Result("re.error", is_propagated=False, is_handled=False, level=0),),
        ),
        Contract(
            function="test_advanced.utils.Bar.__call__",
            scope="test_advanced.app",
            line=24,
            results=(Result("re.error", is_propagated=False, is_handled=True, level=1),),
        ),
    }
