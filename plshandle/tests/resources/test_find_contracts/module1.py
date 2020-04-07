from plshandle import plshandle


@plshandle(KeyError)
def foo():
    pass
