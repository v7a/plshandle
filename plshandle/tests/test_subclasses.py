"""Test checking whether contract checking works with subclasses."""

from plshandle.tests import cli, transform_results, Result, Contract


def test_subclasses():
    """Assert that contracts are handled as described in resources/test_subclasses/module.py."""
    args = ["-m", "test_subclasses.module"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_subclasses.module.Child.__init__",
            scope="test_subclasses.module.Child.create",
            line=14,
            results=(Result("builtins.TypeError", is_propagated=True, is_handled=False, level=0,),),
        ),
        Contract(
            function="test_subclasses.module.Child.create",
            scope="test_subclasses.module",
            line=30,
            results=(Result("builtins.TypeError", is_propagated=False, is_handled=True, level=1,),),
        ),
        Contract(
            function="test_subclasses.module.Parent.__call__",
            scope="test_subclasses.module",
            line=31,
            results=(Result("builtins.TypeError", is_propagated=False, is_handled=True, level=1,),),
        ),
        Contract(
            function="test_subclasses.module.Parent.get_attribute",
            scope="test_subclasses.module",
            line=32,
            results=(Result("builtins.TypeError", is_propagated=False, is_handled=True, level=1,),),
        ),
        Contract(
            function="test_subclasses.module.Child.__init__",
            scope="test_subclasses.module",
            line=37,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_subclasses.module.Parent.__call__",
            scope="test_subclasses.module",
            line=37,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_subclasses.module.Child.__init__",
            scope="test_subclasses.module",
            line=38,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_subclasses.module.Parent.get_attribute",
            scope="test_subclasses.module",
            line=38,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_subclasses.module.Child.__init__",
            scope="test_subclasses.module",
            line=39,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
        Contract(
            function="test_subclasses.module.Parent.get_attribute",
            scope="test_subclasses.module",
            line=40,
            results=(
                Result("builtins.TypeError", is_propagated=False, is_handled=False, level=0,),
            ),
        ),
    }
