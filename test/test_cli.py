# coding: utf-8
from __future__ import unicode_literals
from functools import partial
import os
from click.testing import CliRunner
import pw, pw.cli
import xerox


DIRNAME = os.path.dirname(os.path.abspath(__file__))

def invoke_cli(*args, **kwargs):
  # determine db path
  assert not kwargs.keys() or list(kwargs.keys()) == ['db_path']
  db_path = kwargs.get('db_path', 'db.yaml')
  db_path = os.path.join(DIRNAME, db_path)

  # run CLI
  runner = CliRunner()
  os.environ['PW_GPG_HOMEDIR'] = os.path.join(DIRNAME, 'keys')
  return runner.invoke(pw.cli.pw, ['--database-path', db_path] + list(args))


def test_basic():
  expected = u"""
goggles: alice@gogglemail.com | *** PASSWORD COPIED TO CLIPBOARD *** | https://mail.goggles.com/
goggles: bob+spam@gogglemail.com
laptop: alice | default user
laptop: bob
phones.myphone
phones.samson
router: ädmin
"""
  result = invoke_cli()
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()


def test_version():
  result = invoke_cli('--version')
  assert not result.exception and result.exit_code == 0
  assert pw.__version__ in result.output.strip()


def test_missing():
  result = invoke_cli(db_path='MISSING')
  assert isinstance(result.exception, SystemExit) and result.exit_code != 0
  assert "not found" in result.output


def test_search():
  # search for key
  expected = """
goggles: alice@gogglemail.com | https://mail.goggles.com/
goggles: bob+spam@gogglemail.com
"""
  result = invoke_cli('--no-copy', '--no-echo', 'goggle')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # search for user
  expected = """
goggles: bob+spam@gogglemail.com
laptop: bob
"""
  result = invoke_cli('--no-copy', '--no-echo', 'bob@')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # search for both user and key
  expected = "goggles: bob+spam@gogglemail.com"
  result = invoke_cli('--no-copy', '--no-echo', 'bob@goggle')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()


def test_echo_vs_copy():
  # no copy nor echo
  expected = "phones.myphone"
  xerox.copy('')
  result = invoke_cli('--no-copy', '--no-echo', 'myphone')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == ''

  # only echo
  expected = "phones.myphone | 0000"
  xerox.copy('')
  result = invoke_cli('--no-copy', '--echo', 'myphone')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == ''

  # only echo
  expected = "phones.myphone | *** PASSWORD COPIED TO CLIPBOARD ***"
  xerox.copy('')
  result = invoke_cli('--copy', '--no-echo', 'myphone')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == '0000'

  # both copy and echo
  expected = "phones.myphone | 0000 | *** PASSWORD COPIED TO CLIPBOARD ***"
  xerox.copy('')
  result = invoke_cli('--copy', '--echo', 'myphone')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == '0000'


def test_strict():
  # single result
  expected = "phones.myphone"
  result = invoke_cli('--no-copy', '--no-echo', '--strict', 'myphone')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # multiple results (expect failure)
  result = invoke_cli('--no-copy', '--no-echo', '--strict', 'phones')
  assert isinstance(result.exception, SystemExit) and result.exit_code != 0


def test_gpg():
  expected = "pin | *** PASSWORD COPIED TO CLIPBOARD ***"

  # ASCII armor
  result = invoke_cli(db_path='db.yaml.asc')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # binary
  result = invoke_cli(db_path='db.yaml.gpg')
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
