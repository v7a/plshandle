"""Collect verbose messages from CLI output."""

import sys
from typing import Iterable, Iterator

from plshandle._cli import CLIResult


def _verbose_list(prefix: str, items: Iterable):
    return "{}:\n- {}\n".format(prefix, "\n- ".join([repr(item) for item in items]) or "<none>")


def collect_verbose_messages(output: CLIResult) -> Iterator[str]:
    """Collect verbose messages from CLI output."""
    yield "CLI args merged with config: {}\n".format(output.config)
    yield _verbose_list("sys.path", sys.path)
    yield _verbose_list("collected modules", output.modules)
    yield _verbose_list("collected contracts", output.contracts)
    yield _verbose_list("contract check results", output.results)
