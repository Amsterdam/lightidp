.PHONY: init test


init:
	pip install -r requirements.txt

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	py.test tests

coverage:
	py.test --verbose --cov-report term --cov=auth tests

pep8:
	# we make pep8 ignores the following rules
	# E501 line too long
	pep8 --ignore=E501 auth

