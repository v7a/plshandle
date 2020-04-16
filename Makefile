lint:
	pylint plshandle
	mypy -p plshandle

test:
	pytest && coverage report --fail-under=100

format:
	black plshandle

check: lint test format
	@echo Everything seems fine, ready to commit.

docs:
	sphinx-build -M html doc ../plshandle-doc
