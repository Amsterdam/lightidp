.PHONY: docs

init:
	pip install -r requirements.txt

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	py.test -p no:cacheprovider tests

coverage:
	py.test -p no:cacheprovider --verbose --cov-report term --cov=auth --cov-config .coveragerc tests

pep8:
	# we make pep8 ignores the following rules
	# E501 line too long
	pep8 --ignore=E501 auth

run:
	@set -e; \
	FLASK_APP=auth.server python -m flask run -p 8109 --reload

run-uwsgi:
	@set -e; \
	uwsgi --ini uwsgi.ini

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
