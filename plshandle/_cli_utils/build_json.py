"""Build a JSON array from contract check results."""

import json
from typing import Sequence

from plshandle._cli import CheckResult


def build_json(results: Sequence[CheckResult]) -> str:
    """Build a JSON array from contract check results."""
    return json.dumps(
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
            for result in results
        ]
    )
