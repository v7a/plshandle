from plshandle import plshandle


AliasedError = KeyError


@plshandle(AliasedError, AttributeError)
def foo():
    pass


try:
    foo()
except (KeyError, AttributeError):
    pass
