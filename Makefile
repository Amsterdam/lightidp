.PHONY: docs

init:
	pip install pipenv==3.1.9
	pipenv lock
	pipenv install --dev

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	AUTH_SKIP_CONF_CHECK=1 pipenv run py.test -p no:cacheprovider tests

coverage:
	AUTH_SKIP_CONF_CHECK=1 pipenv run py.test -p no:cacheprovider --verbose --cov-report term --cov=auth --cov-config .coveragerc tests

coverage-noenv:
	# WARNING: The *-noenv targets exist because we cannot get pipenv to work propoerly under Jenkins (no tty). This should be fixed in the future.
	AUTH_SKIP_CONF_CHECK=1 python setup.py test -a "-p no:cacheprovider --verbose --cov=auth --cov-report=term --cov-config .coveragerc tests"

pep8:
	# we make pep8 ignores the following rules
	# E501 line too long
	pipenv run pep8 --ignore=E501 auth

pep8-noenv:
	# WARNING: The *-noenv targets exist because we cannot get pipenv to work propoerly under Jenkins (no tty). This should be fixed in the future.
	pip install pep8; \
	pep8 --ignore=E501 auth

run-dev:
	# WARNING: only use this for development purposes
	@set -e; \
	FLASK_APP=auth.server pipenv run python -m flask run -p 8109 --reload

run:
	# NOTICE: running with uWSGI
	# This needs the auth module to be installed in the current environment
	@set -e; \
	uwsgi --ini uwsgi.ini

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
