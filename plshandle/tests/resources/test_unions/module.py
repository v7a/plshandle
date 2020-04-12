from typing import Type, Union

from plshandle import plshandle


class Foo:
    @plshandle(KeyError)
    def __init__(self):
        pass

    @plshandle(AttributeError)
    def __call__(self):
        pass


class Bar:
    @plshandle(TypeError)
    def foo(self):
        pass


bar: Union[Foo, Type[Foo]]
try:
    bar()
except KeyError:
    pass

foo: Union[Bar, Foo]
try:
    foo.foo()
except TypeError:
    pass
