"""Read config from ./pyproject.toml or --config and merge it with the other args."""

from dataclasses import dataclass
from typing import Optional, Iterable

import toml


@dataclass
class Config:
    """Parsed arguments."""

    config: Optional[str] = None
    directory: Optional[Iterable[str]] = None
    package: Optional[Iterable[str]] = None
    module: Optional[Iterable[str]] = None
    strict: bool = False  #: try block + handlers must be one level above call
    json: bool = False  #: print checked contracts as JSON array to stdout
    verbose: bool = False  #: verbose output
    version: bool = False
    help_requested: bool = False


def _read_list(config: dict, key: dict, file: str):
    try:
        dirs = config[key]
        if isinstance(dirs, list):
            return dirs
        raise TypeError("{}: '{}' must be a list".format(file, key))
    except KeyError:
        return []


def _read_bool(config: dict, key: dict, file: str, default=False):
    try:
        value = config[key]
        if isinstance(value, bool):
            return value
        raise TypeError("{}: '{}' must be a boolean".format(file, key))
    except KeyError:
        return default


def _read_from_file(file: str) -> Config:
    config = toml.load(file)
    try:
        config = config["tool"]["plshandle"]
    except KeyError:
        raise FileNotFoundError("No such section 'tool.plshandle' in {}".format(file))

    return Config(
        directory=_read_list(config, "directories", file),
        package=_read_list(config, "packages", file),
        module=_read_list(config, "modules", file),
        strict=_read_bool(config, "strict", file),
        json=_read_bool(config, "json", file),
        verbose=_read_bool(config, "verbose", file),
    )


def read_and_merge_config(cli_args: Config) -> Config:
    """Read config from ./pyproject.toml or --config and merge it with the other args."""
    try:
        cfg_file = cli_args.config or "pyproject.toml"
        cfg_args = _read_from_file(cfg_file)
    except FileNotFoundError as exc:
        if cli_args.config:
            raise exc  # we explicitly specified a config, so raise if FNF
        cfg_args = Config()
        cfg_file = None

    return Config(
        config=cfg_file,
        directory=(cfg_args.directory or []) + (cli_args.directory or []),
        package=(cfg_args.package or []) + (cli_args.package or []),
        module=(cfg_args.module or []) + (cli_args.module or []),
        strict=cfg_args.strict or cli_args.strict,
        json=cfg_args.json or cli_args.json,
        verbose=cfg_args.verbose or cli_args.verbose,
    )
