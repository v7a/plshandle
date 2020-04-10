from plshandle import plshandle


class CustomError(Exception):
    pass


@plshandle(KeyError, CustomError)  # contract created, requires handling KeyError and CustomError
def foo():
    pass


class Bar:
    @plshandle(KeyError)
    def __init__(self):
        foo()  # error: did not handle CustomError

        try:
            foo()  # o.k. handled CustomError and propagated KeyError
        except CustomError:
            pass
        except AttributeError:
            pass

        try:
            if True:
                foo()  # o.k., handled both CustomError and KeyError at level 2
        except (CustomError, KeyError):
            pass

        CustomError()  # no report created for this call

    @classmethod  # no contract created for this decorator
    def bar2(cls):
        pass

    def __call__(self):
        pass
