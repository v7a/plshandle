"""Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.
"""

from ._cli import cli
from ._decorator import plshandle
from ._gather_contracts import Contract
from ._check_contracts import CheckResult, ContractReport, ExceptionResult
