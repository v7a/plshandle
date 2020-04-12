from typing import Type

from plshandle import plshandle


@plshandle(KeyError, AttributeError)
def foo():
    pass


try:
    foo()
except int:
    pass
