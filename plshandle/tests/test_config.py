"""Test config file support and merging it with CLI args."""

import pytest

from plshandle.tests import cli, resource
from plshandle._cli_utils.config import Config


def test_config():
    """Assert that merging config file and CLI args works as intended."""
    result = cli(["-p", "test_simple", "--config", str(resource("test_config", "config.toml"))])
    assert result.config == Config(
        config=str(resource("test_config", "config.toml")),
        directory=[],
        package=["test_unions", "test_simple"],
        module=[],
        strict=True,
        json=False,
        verbose=True,
        version=False,
        help_requested=False,
    )


def test_invalid_config_file():
    """Assert that FNF is raised for invalid config files."""
    with pytest.raises(FileNotFoundError):
        cli(["--config", "invalidfile.toml"])


def test_missing_config_section():
    """Assert that FNF is raised if tool.plshandle config section is missing."""
    with pytest.raises(FileNotFoundError):
        cli(["--config", str(resource("test_config", "invalid.toml"))])


def test_invalid_list():
    """Assert that TypeError is raised if a list config entry is not a list."""
    with pytest.raises(TypeError):
        cli(["--config", str(resource("test_config", "invalid_list.toml"))])


def test_invalid_boolean():
    """Assert that TypeError is raised if a boolean config entry is not a boolean."""
    with pytest.raises(TypeError):
        cli(["--config", str(resource("test_config", "invalid_bool.toml"))])
