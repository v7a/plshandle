from re import error

from test_advanced.errors import CustomError
from test_advanced.utils import foo, Bar


foo_alias_1 = foo
foo_alias_2 = foo_alias_1


try:
    for i in range(0):
        while False:
            with open("file", "w"):
                foo_alias_2()  #  nested in multiple statements, scope of call correctly determined
except CustomError:
    pass


bar = Bar()
bar()  # call member function __call__ correctly detected and flagged

try:
    bar()  # "RegexError" correctly translated to re.error
except error:  # correctly resolved to re.error
    pass
