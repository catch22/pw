# coding: utf-8
from __future__ import absolute_import, division, print_function
from functools import partial
from click.testing import CliRunner
import os.path
import pytest
import pw, pw.__main__
import pyperclip


@pytest.fixture(scope='module',
                params=['db.pw', 'db.pw.gpg', 'db.pw.asc', 'db.yaml'])
def runner(request):
    # override GPG homedir
    dirname = os.path.dirname(os.path.abspath(__file__))
    pw._gpg.OVERRIDE_HOMEDIR = os.path.join(dirname, 'keys')

    # instantiate runner and provide database path
    runner = CliRunner()
    return (
        lambda *args: runner.invoke(pw.__main__.pw, ('--file', request.param, ) + args)
    )


@pytest.mark.parametrize("args, exit_code, output_expected", [
    # version
    (["--version"], 0, "pw version " + pw.__version__),
    # default options
    ([], 0, u"""
goggles: alice@gogglemail.com
   https://mail.goggles.com/
   second line
goggles: bob+spam@gogglemail.com
laptop: alice | default user
laptop: bob
phones.myphone
phones.samson
router: ädmin | multiple (...)"""),
    # querying for path and user
    (["goggle"], 0, """
goggles: alice@gogglemail.com
   https://mail.goggles.com/
   second line
goggles: bob+spam@gogglemail.com
  """),
    (["bob@"], 0, """
goggles: bob+spam@gogglemail.com
laptop: bob
  """),
    (["bob@goggle"], 0, "goggles: bob+spam@gogglemail.com"),
    (["goggle", "bob"], 0, "goggles: bob+spam@gogglemail.com"),
    (["bob@goggle", "bob"], 0, ""),
    # strictness
    (["--strict", "myphone"], 0, "phones.myphone"),
    (["--strict", "phones"], 2,
     "error: multiple or no records found (but using --strict mode)"),
    # raw
    (["--raw", "myphone"], 0, "0000"),
    (["--strict", "--raw", "myphone"], 0, "0000"),
    (["--raw", "phones"], 0, "0000\n111"),
    (["--strict", "--raw", "phones"], 2,
     "error: multiple or no records found (but using --strict mode)"),
])
def test_basic(runner, args, exit_code, output_expected):
    result = runner("--no-passwords", *args)
    assert result.exit_code == exit_code
    assert result.output.strip() == output_expected.strip()


def test_missing():
    runner = CliRunner()
    result = runner.invoke(pw.__main__.pw, ('--file', 'MISSING'))
    assert result.exit_code == 1
    assert "error: password store not found at 'MISSING'" == result.output.strip(
    )


CLIPBOARD_NOT_TOUCHED = u'CLIPBOARD_NOT_TOUCHED'


@pytest.mark.parametrize(
    "args, exit_code, output_expected, clipboard_expected", [
        (["myphone"], 0,
         "phones.myphone | *** PASSWORD COPIED TO CLIPBOARD ***", "0000"),
        (["--copy", "myphone"], 0,
         "phones.myphone | *** PASSWORD COPIED TO CLIPBOARD ***", "0000"),
        (["--echo", "myphone"], 0, "phones.myphone | 0000",
         CLIPBOARD_NOT_TOUCHED),
        (["--raw", "myphone"], 0, "0000", CLIPBOARD_NOT_TOUCHED),
        (["--no-passwords", "myphone"], 0, "phones.myphone",
         CLIPBOARD_NOT_TOUCHED),
    ])
def test_modes(runner, args, exit_code, output_expected, clipboard_expected):
    pyperclip.copy(CLIPBOARD_NOT_TOUCHED)
    result = runner(*args)
    assert result.exit_code == exit_code
    assert result.output.strip() == output_expected.strip()
    assert pyperclip.paste() == clipboard_expected.strip()
