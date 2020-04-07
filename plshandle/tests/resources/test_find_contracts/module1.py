from plshandle import plshandle


@plshandle(KeyError)
def foo():
    pass


class CustomError(Exception):
    pass


class Bar:
    @plshandle(AttributeError)
    @plshandle(CustomError)
    def __init__(self):
        pass

    @plshandle(KeyError)
    def __call__(self):
        pass
