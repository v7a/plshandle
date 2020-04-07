"""Expose various directories."""

import os
import sys
from pathlib import Path

from mypy.options import Options

from plshandle import cli as _cli


TEST_DIR = Path(__file__).parent
RESOURCE_DIR = TEST_DIR / "resources"

sys.path.insert(0, str(RESOURCE_DIR))


def cli(args):
    """Wrap plshandle.cli and inject custom options."""
    options = Options()
    options.incremental = False
    options.cache_dir = os.devnull
    options.skip_cache_mtime_checks = True
    return _cli(args, options)


def resource(*path_parts) -> Path:
    """Get the absolute path to an resource in the resources directory."""
    return RESOURCE_DIR.joinpath(*path_parts)
