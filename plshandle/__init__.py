"""Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.
"""

from ._cli import cli
from ._decorator import plshandle
from ._visitors.contract_collector import Contract
from ._visitors.contract_checker import CheckResult, ContractReport, ExceptionResult
from ._version import __version__
