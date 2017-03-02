.PHONY: test coverage run-dev run docs showdocs

PYTHON=python3

test:
	@. test.env; \
	$(PYTHON) setup.py test -a "-p no:cacheprovider --verbose tests"

coverage:
	@. test.env; \
	$(PYTHON) setup.py test -a "-p no:cacheprovider --verbose --cov=auth --cov-report=term --cov-config .coveragerc tests"

run-dev:
	# WARNING: running with Flask server, *only* use this for development purposes
	@set -e; \
	FLASK_APP=auth.server flask run -p 8109 --reload

run:
	# WARNING: running with uWSGI
	@set -e; \
	uwsgi --ini uwsgi.ini

docs:
	make -C docs/ html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"

showdocs:
	open docs/_build/html/index.html
