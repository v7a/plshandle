# plshandle
Create an explicit contract between caller and function that requires the caller to handle specific
exceptions raised by the function.

### Why
Sometimes, we just _have to_ recover from an error. And because you are a human being, you might not
always keep exception handling in mind at all times. This tool helps reduce this mental overhead by
reporting all contract violations.

### How
A simple example:
```py
from plshandle import plshandle

@plshandle(KeyError)
def get_item(key):
    return {}[key]

get_item(0)  # tool reports this call expression as a contract violation
```
It is also possible to propagate errors, similar to Java:
```py
@plshandle(KeyError)
def foo():
    return get_item(0)  # o.k., KeyError is propagated, caller's responsibility to handle it
```
Note: This tool performs static analysis only. As such, dynamic constructs are most likely not supported:
```py
@plshandle(KeyError)
def foo():
    pass
def bar(callback):
    callback()  # nothing reported
bar(foo)
```
Refer to https://plshandle.readthedocs.io for more in-depth examples.

### Before committing

_Fetch development dependencies_
```
pip -r requirements-dev.txt
```
_Ensure there are no linting errors_
```sh
pylint plshandle && mypy -p plshandle
```
_Ensure all tests are successful and code coverage is 100%_
```sh
pytest && coverage report --fail-under=100
```
_Reformat all files_
```sh
black plshandle
```
_Or just do this if you have make installed_
```sh
make check
```
