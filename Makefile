tests = tests
package = harlib

check:
	# No unused imports, no undefined vars,
	flake8 --ignore=E731,W503 --exclude $(package)/__init__.py,$(package)/compat.py --max-complexity 10 $(package)/
	# Basic error checking in test code
	pyflakes $(tests)
	# PEP257 docstring conventions
	#pydocstyle --add-ignore=D100,D101,D102,D103,D104,D105,D204,D301 $(package)/
	# Python linter errors only
	pylint --rcfile .pylintrc $(package)

pylint:
	pylint --rcfile .pylintrc $(package)

test:
	py.test -v $(tests)

typecheck:
	python -m mypy -p $(package) --ignore-missing-imports --disallow-untyped-defs --strict-optional --warn-no-return

coverage:
	py.test --cov $(package) --cov-report term-missing --cov-fail-under 80 $(tests)

.PHONY: htmlcov
htmlcov:
	py.test --cov $(package) --cov-report html $(tests)
	open htmlcov/index.html

prcheck: check typecheck test
