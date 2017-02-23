.PHONY: test coverage run-dev run docs

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	JWT_ACCESS_SECRET=jas JWT_REFRESH_SECRET=jrs python setup.py test -a "-p no:cacheprovider --verbose tests"

coverage:
	JWT_ACCESS_SECRET=jas JWT_REFRESH_SECRET=jrs python setup.py test -a "-p no:cacheprovider --verbose --cov=auth --cov-report=term --cov-config .coveragerc tests"

run-dev:
	# WARNING: running with Flask server, *only* use this for development purposes
	@set -e; \
	JWT_ACCESS_SECRET=jas JWT_REFRESH_SECRET=jrs FLASK_APP=auth.server python -m flask run -p 8109 --reload

run:
	# WARNING: running with uWSGI
	@set -e; \
	uwsgi --ini uwsgi.ini

docs:
	make -C docs/ html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
