"""Build version string containing plshandle version, interpreter type and Python version."""

import sys

from plshandle._version import __version__


def _version_to_string(version_info):
    return "{}.{}.{}".format(version_info.major, version_info.minor, version_info.micro)


def build_version():
    """Build version string containing plshandle version, interpreter type and Python version."""
    return "plshandle {version}, {intp} {intp_version}, Python {py_version}".format(
        version=__version__,
        intp=sys.implementation.name,
        intp_version=_version_to_string(sys.implementation.version),
        py_version=sys.version,
    )
