.PHONY: test test-coverage upload-release pretty encrypt-test-db

test:
	cd test && python -m pytest

upload-release:
	python -c "import wheel, pypandoc"  # check upload dependencies
	python -c "import subprocess; assert not subprocess.check_output('python setup.py --version', shell=True).strip().endswith('-dev'), 'trying to upload -dev release'"
	python setup.py sdist bdist_wheel
	#python setup.py upload
	twine upload dist/*

pretty:
	yapf -i pw/*.py test/*.py

encrypt-test-db:
	gpg2 --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.gpg test/db.pw
	gpg2 --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.asc --armor test/db.pw
