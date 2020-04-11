"""Test if exception types are resolved correctly."""

import pytest

from plshandle.tests import cli, transform_results, Result, Contract


def test_except_handler_tuple():
    """Assert that types are correctly deduced from ``except (Type1, Type2, ...)``."""
    args = ["-m", "test_exception_resolution.handler_tuple"]
    contracts = transform_results(cli(args).results)
    assert contracts == {
        Contract(
            function="test_exception_resolution.handler_tuple.foo",
            scope="test_exception_resolution.handler_tuple",
            line=13,
            results=(
                Result("builtins.KeyError", is_propagated=False, is_handled=True, level=1,),
                Result("builtins.AttributeError", is_propagated=False, is_handled=True, level=1,),
            ),
        ),
    }


def test_invalid_exception_type_1():
    """Assert that a ``TypeError`` is raised if a type specified in a contract or except handler
    is not valid.
    """
    with pytest.raises(TypeError):
        cli(["-m", "test_exception_resolution.invalid_type_1"])


def test_invalid_exception_type_2():
    """Assert that a ``TypeError`` is raised if a type specified in a contract or except handler
    is not valid.
    """
    with pytest.raises(TypeError):
        cli(["-m", "test_exception_resolution.invalid_type_2"])
