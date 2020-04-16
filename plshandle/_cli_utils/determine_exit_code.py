"""Determine the exit code from CLI arguments and check results."""

from plshandle._cli import CLIResult
from plshandle._cli_utils.collect_errors import _get_unhandled


def determine_exit_code(output: CLIResult):
    """Determine the exit code from CLI arguments and check results."""
    if output.config.help_requested:
        return 20
    if output.config.version:
        return 21
    if not output.modules:
        return 10
    if not output.contracts:
        return 11
    if not any(result.reports for result in output.results):
        return 12
    if any(
        _get_unhandled(report.results, output.config.strict)
        for result in output.results
        for report in result.reports
    ):
        return 1
    return 0
