from re import error as RegexError

import plshandle

from test_advanced import errors

serious_business_alias = plshandle.plshandle
AliasedError = errors.CustomError
AliasedAliasedError = AliasedError


@serious_business_alias(AliasedAliasedError)
def foo():
    pass


class Bar:
    @serious_business_alias(RegexError)
    def __call__(self):
        pass
