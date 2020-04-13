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

### Things to consider
- This tool performs static analysis only. As such, dynamic constructs are most likely not supported:
  ```py
  @plshandle(KeyError)
  def foo():
      pass
  def bar(callback):
      callback()  # nothing reported
  bar(foo)
  ```
- As mypy is the base for this tool, anything related to types that does not work there will not work
  with this tool either. You are strongly advised to heavily type-annotate your code to allow seamless
  type resolution:
  ```py
  class Base:
      def __init__(self):
          pass
      @plshandle(TypeError)
      def __call__(self):
          pass
  class Derived(Base):
      @plshandle(TypeError)
      def foo(self):
          pass

  obj = Derived()
  obj.foo()  # nothing reported, mypy infers obj as type "Any"
  obj: Derived = Derived()
  obj.foo()  # o.k., mypy infers obj as type "Derived"

  def bar():
      return Base()

  bar()()  # nothing reported, mypy infers expression bar() as type "Any"
  # either annotate return type or assign to a var with a type annotation
  ```

### Before committing

_Download development dependencies_
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
