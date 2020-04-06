"""Command-line interface of plshandle."""

from argparse import ArgumentParser
import sys
from typing import Iterable

from plshandle._gather_contracts import _gather_contracts
from plshandle._gather_modules import _gather_modules


def _make_arg_parser(description: str):
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "-d",
        "--directory",
        nargs="*",
        help="additionally gathers all modules from all packages in this directory recursively",
    )
    parser.add_argument(
        "-p",
        "--package",
        nargs="*",
        help="additionally gathers all modules from this package recursively",
    )
    parser.add_argument(
        "-m", "--module", nargs="*", help="additionally include these modules in the check"
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


def cli(args):
    """Collect all functions decorated with 'plshandle' for all provided
    modules/packages/directories and check whether their callers handle the exceptions passed to
    the decorator.
    """
    args = _make_arg_parser(cli.__doc__).parse_args(args)
    if args.directory:
        # to be able to import the gathered modules later on
        sys.path[:0] = args.directory

    modules = tuple(_gather_modules(args.directory or [], args.package or [], args.module or []))
    if args.verbose:
        print(_verbose_list("sys.path", sys.path))
        print(_verbose_list("gathered modules", modules))

    contracts = tuple(_gather_contracts(modules))
    if args.verbose:
        print(_verbose_list("gathered contracts", contracts))
