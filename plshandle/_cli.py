"""Command-line interface of plshandle."""

from argparse import ArgumentParser
from dataclasses import dataclass
import sys
from typing import Iterable, Optional, List, Sequence

from mypy.options import Options

from plshandle._cache import _MypyCache
from plshandle._check_contracts import _check_contracts, CheckResult
from plshandle._gather_contracts import _gather_contracts, Contract
from plshandle._gather_modules import _gather_modules, BuildSource


def _make_arg_parser(description: Optional[str] = None):
    parser = ArgumentParser(description=description or __doc__)
    parser.add_argument(
        "-d",
        "--directory",
        action="append",
        help="additionally gathers all modules from all packages in this directory recursively",
    )
    parser.add_argument(
        "-p",
        "--package",
        action="append",
        help="additionally gathers all modules from this package recursively",
    )
    parser.add_argument(
        "-m", "--module", action="append", help="additionally include these modules in the check"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        # pylint: disable=line-too-long
        help="if specified, requires the try block and its handlers to be exactly one level above the function call",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="if specified, prints error information as JSON array to stderr",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="if specified, prints additional information during module processing",
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
    """All arguments, gathered modules, contracts and check results."""

    args: Arguments
    modules: Sequence[BuildSource]
    contracts: Sequence[Contract]
    results: Sequence[CheckResult]


def cli(args, mypy_options: Options = Options()):
    """Collect all functions decorated with 'plshandle' for all provided
    modules/packages/directories and check whether their callers handle the exceptions passed to
    the decorator. Optionally accepts mypy options.
    """
    args: Arguments = _make_arg_parser(cli.__doc__).parse_args(args)  # type: ignore

    # be able to find module specs
    sys.path[:0] = list(args.directory or [])

    package_roots: List[str] = []
    modules = tuple(
        _gather_modules(args.directory or [], args.package or [], args.module or [], package_roots)
    )
    if args.verbose:
        print(_verbose_list("sys.path", sys.path))
        print(_verbose_list("gathered modules", modules))

    # have mypy seamlessly find all modules
    sys.path[:0] = package_roots

    mypy_options.package_root = package_roots
    cache = _MypyCache(modules, mypy_options)
    contracts = tuple(_gather_contracts(modules, cache))
    if args.verbose:
        print(_verbose_list("gathered contracts", contracts))

    results = tuple(_check_contracts(contracts, modules, cache))
    if args.verbose:
        print(_verbose_list("contract check results", results))

    return CLIResult(args, modules, contracts, results)
