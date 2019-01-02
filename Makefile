.PHONY: test test-coverage upload-release pretty encrypt-test-db

PW_GPG ?= gpg

test:
	py.test

pw-with-test-db:
	python -m pw --file test/db.pw ${ARGS}

upload-release:
	python -c "import wheel"  # check upload dependencies
	python -c "import subprocess; assert b'dev' not in subprocess.check_output('python setup.py --version', shell=True).strip(), 'trying to upload dev release'"
	python setup.py sdist bdist_wheel
	#python setup.py upload
	twine upload dist/* --sign

pretty:
	#yapf -i *.py pw/*.py test/*.py
	black *.py pw/*.py test/*.py

encrypt-test-db:
	$(PW_GPG) --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.gpg test/db.pw
	$(PW_GPG) --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.asc --armor test/db.pw

mypy:
	mypy -m pw --strict
