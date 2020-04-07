from plshandle import plshandle as plshandle_alias

plshandle_alias2 = plshandle_alias


@plshandle_alias2(KeyError, TypeError)
def bar():
    pass
