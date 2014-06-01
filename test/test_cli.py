from functools import partial
from click.testing import CliRunner
from pw.cli import pw
import xerox


def test_basic():
  runner = CliRunner()

  expected = """
goggles: alice@gogglemail.com | *** PASSWORD COPIED TO CLIPBOARD *** | https://mail.goggles.com/
goggles: bob+spam@gogglemail.com
laptop: alice
laptop: bob
phones.myphone
phones.samson
"""
  result = runner.invoke(pw, ['--database-path', 'db.yaml'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()


def test_search():
  runner = CliRunner()

  # search for key
  expected = """
goggles: alice@gogglemail.com | https://mail.goggles.com/
goggles: bob+spam@gogglemail.com
"""
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', 'goggle'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # search for user
  expected = """
goggles: bob+spam@gogglemail.com
laptop: bob
"""
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', 'bob@'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # search for both user and key
  expected = "goggles: bob+spam@gogglemail.com"
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', 'bob@goggle'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()


def test_echo_vs_copy():
  runner = CliRunner()

  # no copy nor echo
  expected = "phones.myphone"
  xerox.copy('')
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', 'myphone'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == ''

  # only echo
  expected = "phones.myphone | 0000"
  xerox.copy('')
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--echo', 'myphone'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == ''

  # only echo
  expected = "phones.myphone | *** PASSWORD COPIED TO CLIPBOARD ***"
  xerox.copy('')
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--copy', '--no-echo', 'myphone'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == '0000'

  # both copy and echo
  expected = "phones.myphone | 0000 | *** PASSWORD COPIED TO CLIPBOARD ***"
  xerox.copy('')
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--copy', '--echo', 'myphone'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()
  assert xerox.paste() == '0000'


def test_strict():
  runner = CliRunner()

  # single result
  expected = "phones.myphone"
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', '--strict', 'myphone'])
  assert not result.exception and result.exit_code == 0
  assert result.output.strip() == expected.strip()

  # multiple results (expect failure)
  result = runner.invoke(pw, ['--database-path', 'db.yaml', '--no-copy', '--no-echo', '--strict', 'phones'])
  assert isinstance(result.exception, SystemExit) and result.exit_code != 0
