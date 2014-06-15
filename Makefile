.PHONY: test upload-release

test:
	cd test && python -m pytest

upload-release:
	python setup.py sdist bdist_wheel upload
