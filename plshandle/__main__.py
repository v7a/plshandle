"""Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.
"""

import json
from pathlib import Path
import sys

from ._cli import cli, CLIResult


def _is_handled(res, is_strict_mode):
    return res.level == 1 if is_strict_mode else True if res.is_handled else res.is_propagated


def _get_unhandled(results, is_strict_mode):
    return [res for res in results if not _is_handled(res, is_strict_mode)]


def _print_errors(output: CLIResult):
    for result in output.results:
        for report in result.reports:
            unhandled = _get_unhandled(report.results, output.args.strict)
            for res in unhandled:
                if res.is_handled and output.args.strict and res.level != 1:
                    msg = "{path}:{line}: {exc} not handled at level 1"
                else:
                    # pylint: disable=line-too-long
                    msg = "{path}:{line}: Violated contract of {func}. Not handled nor propagated {exc}"
                print(
                    msg.format(
                        path=Path(result.source.path),
                        line=report.context.line,
                        func=report.contract.function.fullname,
                        exc=res.exception.fullname,
                    ),
                    file=sys.stderr,
                )


def _print_json(output: CLIResult):
    json.dump(
        [
            {
                "source": {"path": result.source.path, "module": result.source.module,},
                "reports": [
                    {
                        "contract": {
                            "function": report.contract.function.fullname,
                            "exceptions": [exc.fullname for exc in report.contract.exception_types],
                            "source": {
                                "path": report.contract.source.path,
                                "module": report.contract.source.module,
                            },
                        },
                        "context": {
                            "scope": report.scope.fullname,
                            "line": report.context.line,
                            "column": report.context.column,
                        },
                        "results": [
                            {
                                "exception": exc_result.exception.fullname,
                                "is_propagated": exc_result.is_propagated,
                                "is_handled": exc_result.is_handled,
                                "level": exc_result.level,
                            }
                            for exc_result in report.results
                        ],
                    }
                    for report in result.reports
                ],
            }
            for result in output.results
        ],
        sys.stdout,
    )


def _determine_exit_code(output: CLIResult):
    if not output.modules:
        return 10
    if not output.contracts:
        return 11
    if not any(result.reports for result in output.results):
        return 12
    if any(
        _get_unhandled(report.results, output.args.strict)
        for result in output.results
        for report in result.reports
    ):
        return 1
    return 0


if __name__ == "__main__":
    cli_output = cli(sys.argv[1:])
    if cli_output.args.json:
        _print_json(cli_output)
    else:
        _print_errors(cli_output)

    sys.exit(_determine_exit_code(cli_output))
