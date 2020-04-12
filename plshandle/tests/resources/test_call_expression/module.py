from typing import overload

from plshandle import plshandle


class Foo:
    def __init__(self):
        pass

    @plshandle(KeyError)
    def method(self):
        pass


@overload
def make_foo(x: int) -> Foo:
    ...


@overload
def make_foo(x: str) -> Foo:
    ...


def make_foo(x) -> Foo:
    return Foo()


def make_foo_2() -> Foo:
    return Foo()


try:
    make_foo(0).method()
    make_foo_2().method()
except KeyError:
    pass
