from typing import Dict

from plshandle import plshandle


class Child:
    @plshandle(TypeError)
    def __init__(self):
        pass

    @plshandle(TypeError)
    @classmethod
    def create(cls):
        return cls()


class Parent(Child):
    attribute = 0

    @plshandle(TypeError)
    def __call__(self):
        pass

    @plshandle(TypeError)
    def get_attribute(self):
        return self.attribute


try:
    instance: Parent = Parent.create()
    instance()
    instance.get_attribute()
except TypeError:
    pass

# special cases
Parent()()
Parent().get_attribute()
map_: Dict[int, Parent] = {0: Parent()}
map_[0].get_attribute()
