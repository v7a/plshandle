"""Collect the errors from contract check results."""

from pathlib import Path
from typing import Iterator

from plshandle._cli import CLIResult


def _is_handled(res, is_strict_mode):
    return res.level == 1 if is_strict_mode else True if res.is_handled else res.is_propagated


def _get_unhandled(results, is_strict_mode):
    return [res for res in results if not _is_handled(res, is_strict_mode)]


def collect_errors(output: CLIResult) -> Iterator[str]:
    """Collect the errors from the contract check results and yield corresponding error messages."""
    for result, report, unhandled in [
        (result, report, unhandled)
        for result in output.results
        for report in result.reports
        for unhandled in _get_unhandled(report.results, output.config.strict)
    ]:
        if unhandled.is_handled and output.config.strict and unhandled.level != 1:
            msg = "{path}:{line}: {exc} not handled at level 1"
        else:
            msg = "{path}:{line}: Violated contract of {func}. Not handled nor propagated {exc}"
        yield msg.format(
            path=Path(result.source.path),
            line=report.context.line,
            func=report.contract.function.fullname,
            exc=unhandled.exception.fullname,
        )
