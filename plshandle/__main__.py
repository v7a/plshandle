"""Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.
"""

import sys

from plshandle._cli import cli
from plshandle._cli_utils.build_json import build_json
from plshandle._cli_utils.build_version import build_version
from plshandle._cli_utils.collect_errors import collect_errors
from plshandle._cli_utils.collect_verbose_messages import collect_verbose_messages
from plshandle._cli_utils.determine_exit_code import determine_exit_code
from plshandle._version import __version__


if __name__ == "__main__":
    cli_output = cli(sys.argv[1:])

    if cli_output.config.verbose:
        for msg in collect_verbose_messages(cli_output):
            print(msg)

    if cli_output.config.version:
        print(build_version())
    elif cli_output.config.help_requested:
        pass  # prevent printing the rest if help was requested
    elif not cli_output.modules:
        print("error: No modules found", file=sys.stderr)
    elif not cli_output.contracts:
        print("error: No contracts found", file=sys.stderr)
    elif not any(result.reports for result in cli_output.results):
        print("error: No contracts checked", file=sys.stderr)

    if cli_output.config.json:
        print(build_json(cli_output.results))

    for msg in collect_errors(cli_output):
        print(msg, file=sys.stderr)

    sys.exit(determine_exit_code(cli_output))
