"""Expose various directories."""

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Set, Iterator, Optional
import os
import sys

from mypy.options import Options

from plshandle import cli as _cli, CheckResult, ContractReport


TEST_DIR = Path(__file__).parent
RESOURCE_DIR = TEST_DIR / "resources"

sys.path.insert(0, str(RESOURCE_DIR))


@dataclass(frozen=True)
class Result:
    """ExceptionResult, but only simple types."""

    exception: str
    is_propagated: bool
    is_handled: bool
    level: int


@dataclass(init=False, unsafe_hash=True)
class Contract:
    """ContractReport, but heavily simplified."""

    function: str
    scope: str
    line: int
    results: Sequence[Result]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        function: Optional[str] = None,
        scope: Optional[str] = None,
        line: Optional[int] = None,
        results: Optional[Sequence[Result]] = None,
        report: Optional[ContractReport] = None,
    ):
        if function:
            self.function = function
        if scope:
            self.scope = scope
        if line:
            self.line = line
        if results:
            self.results = results
        if report:
            self.function = report.contract.function.fullname
            self.line = report.context.line
            self.scope = report.scope.fullname
            self.results = tuple(
                Result(
                    exception=x.exception.fullname,
                    is_propagated=x.is_propagated,
                    is_handled=x.is_handled,
                    level=x.level,
                )
                for x in report.results
            )


def transform_results(results: Sequence[CheckResult]) -> Set[Contract]:
    """From check results, yield structures containing only the most necessary fields. Those fields
    are exclusively builtin types so they can be easily compared.
    """
    return {Contract(report=report) for result in results for report in result.reports}


def cli(args):
    """Wrap plshandle.cli and inject custom options."""
    options = Options()
    options.incremental = False
    options.cache_dir = os.devnull
    options.skip_cache_mtime_checks = True
    return _cli(args, options)


def resource(*path_parts) -> Path:
    """Get the absolute path to an resource in the resources directory."""
    return RESOURCE_DIR.joinpath(*path_parts)
