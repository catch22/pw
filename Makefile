.PHONY: test test-coverage upload-release pretty encrypt-test-db

PW_GPG ?= gpg

test:
	poetry run pytest

pw-with-test-db:
	poetry run pw --file test/db.pw ${ARGS}

pretty:
	# poetry run yapf -i *.py pw/*.py test/*.py
	poetry run black pw/*.py test/*.py

encrypt-test-db:
	$(PW_GPG) --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.gpg test/db.pw
	$(PW_GPG) --batch --yes --homedir test/keys --encrypt --recipient "test.user@localhost" --output test/db.pw.asc --armor test/db.pw

mypy:
	poetry run mypy -m pw --strict
