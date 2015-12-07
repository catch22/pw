.PHONY: test test-coverage upload-release pretty encrypt-test-db

test:
	py.test

test-pw-python2:
	PYTHONPATH=. python2 -m pw --file test/db.pw ${ARGS}

test-pw-python3:
	PYTHONPATH=. python3 -m pw --file test/db.pw ${ARGS}

upload-release:
	python3 -c "import wheel, pypandoc"  # check upload dependencies
	python3 -c "import subprocess; assert b'dev' not in subprocess.check_output('python3 setup.py --version', shell=True).strip(), 'trying to upload dev release'"
	python3 setup.py sdist bdist_wheel
	#python setup.py upload
	twine upload dist/*

pretty:
	yapf --verify -i pw/*.py test/*.py

encrypt-test-db:
	gpg2 --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.gpg test/db.pw
	gpg2 --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.asc --armor test/db.pw
