"""Command-line interface of plshandle."""

from argparse import ArgumentParser
from dataclasses import dataclass
import sys
from typing import Iterable, Optional, List, Sequence, Tuple

from mypy.options import Options

from plshandle._cache import MypyCache
from plshandle._visitors.contract_checker import ContractChecker, CheckResult
from plshandle._visitors.contract_collector import ContractCollector, Contract
from plshandle._gather_modules import _gather_modules, BuildSource


def _make_arg_parser(description: Optional[str] = None):
    parser = ArgumentParser(description=description or __doc__)
    parser.add_argument(
        "-d",
        "--directory",
        action="append",
        help="additionally collects all modules from all packages in this directory recursively",
    )
    parser.add_argument(
        "-p",
        "--package",
        action="append",
        help="additionally collects all modules from this package recursively",
    )
    parser.add_argument(
        "-m", "--module", action="append", help="additionally include these modules in the check"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        # pylint: disable=line-too-long
        help="requires the try block and its handlers to be exactly one level above the function call",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="prints a JSON array containing all checked contracts and their results to stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="prints additional information during module processing",
    )
    return parser


def _verbose_list(prefix: str, items: Iterable):
    return "{}:\n- {}\n".format(prefix, "\n- ".join([repr(item) for item in items]) or "<none>")


class Arguments:
    """Parsed arguments."""

    directory: Optional[Iterable[str]]
    package: Optional[Iterable[str]]
    module: Optional[Iterable[str]]
    strict: bool  #: try block + handlers must be one level above call
    json: bool  #: print error information as JSON array to stderr
    verbose: bool  #: verbose output


@dataclass(frozen=True)
class CLIResult:
    """All arguments, collected modules, contracts and check results."""

    args: Arguments
    modules: Sequence[BuildSource]
    contracts: Sequence[Contract]
    results: Sequence[CheckResult]


def _collect_modules_and_package_roots(args: Arguments) -> Tuple[Sequence[BuildSource], List[str]]:
    sys.path[:0] = list(args.directory or [])  # be able to find module specs

    package_roots: List[str] = []
    modules = tuple(
        _gather_modules(args.directory or [], args.package or [], args.module or [], package_roots)
    )
    if args.verbose:
        print(_verbose_list("sys.path", sys.path))
        print(_verbose_list("collected modules", modules))
    if not modules:
        print("error: No modules found")

    return modules, package_roots


def _make_cache(modules: Sequence[BuildSource], package_roots: List[str], options: Options):
    sys.path[:0] = package_roots  # be able to find all modules

    options.package_root = package_roots
    return MypyCache(modules, options)


def _collect_contracts(modules: Sequence[BuildSource], cache: MypyCache, args: Arguments):
    contracts = ContractCollector(modules, cache).contracts
    if args.verbose:
        print(_verbose_list("collected contracts", contracts))
    if not contracts:
        print("error: No contracts found")

    return contracts


def _check_contracts(
    contracts: Sequence[Contract], modules: Sequence[BuildSource], cache: MypyCache, args: Arguments
):
    results = ContractChecker(contracts, modules, cache).results
    if args.verbose:
        print(_verbose_list("contract check results", results))
    if not any(result.reports for result in results):
        print("error: No contracts checked")

    return results


def cli(args, mypy_options: Options = Options()):
    """Collect all functions decorated with 'plshandle' for all provided
    modules/packages/directories and check whether their callers handle the exceptions passed to
    the decorator. Optionally accepts mypy options.
    """
    args: Arguments = _make_arg_parser(cli.__doc__).parse_args(args)  # type: ignore
    modules, package_roots = _collect_modules_and_package_roots(args)
    cache = _make_cache(modules, package_roots, mypy_options)
    contracts = _collect_contracts(modules, cache, args) if modules else []
    results = _check_contracts(contracts, modules, cache, args) if contracts else []
    return CLIResult(args, modules, contracts, results)
