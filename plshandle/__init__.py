"""Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.
"""

from ._cli import cli
from ._decorator import plshandle


if __name__ == "__main__":
    import sys

    cli(sys.argv[1:])
