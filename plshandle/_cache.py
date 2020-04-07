"""Mypy build cache."""

from typing import Iterable

from mypy.build import build
from mypy.fscache import FileSystemCache
from mypy.options import Options
from mypy.modulefinder import BuildSource


class _MypyCache:
    def __init__(self, sources: Iterable[BuildSource], options: Options = Options()):
        # we need these to traverse the AST later on
        options.preserve_asts = True
        options.export_types = True

        # make mypy cache type info to improve performance on subsequent runs
        fs_cache = FileSystemCache()
        fs_cache.set_package_root(options.package_root)

        self.build = build(list(sources), options, None, None, fs_cache)
