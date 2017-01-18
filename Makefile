.PHONY: init test


init:
	pip install -r requirements.txt

test:
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	py.test tests

coverage:
	py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=requests tests

