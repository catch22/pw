.PHONY: test upload-release

test:
	cd test && python -m pytest

upload-release:
	python -c "import wheel, pypandoc"  # check upload dependencies
	python -c "import subprocess; assert not subprocess.check_output('python setup.py --version', shell=True).strip().endswith('-dev'), 'trying to upload -dev release'"
	python setup.py sdist bdist_wheel upload
