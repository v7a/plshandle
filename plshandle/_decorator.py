"""Decorator used to mark contracts."""

from typing import Iterable


def _unused(*_, **__):
    pass


def plshandle(*exception_types: Iterable[BaseException]):
    """Require the caller to handle the given ``exception_types``. This decorator does not modify
    the original function."""
    _unused(exception_types)

    def decorator(function):
        return function

    return decorator
