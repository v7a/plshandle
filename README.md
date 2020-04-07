# plshandle
Create a contract between caller and function that requires the caller to handle specific
exceptions raised by the function.

### Why
Sometimes, we just _have to_ recover from an error. And because you are a human being, you might not
always keep exception handling in mind at all times. This library helps reduce this mental overhead.

### Before committing

_Download development dependencies_
```
pip -r requirements-dev.txt
```
_Ensure there are no linting errors_
```sh
pylint plshandle
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
