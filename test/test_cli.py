# coding: utf-8
from __future__ import absolute_import, division, print_function
from functools import partial
from click.testing import CliRunner
import os.path, sys, tempfile
import pytest
import pw, pw.__main__
import pyperclip


@pytest.fixture()
def dirname():
    return os.path.dirname(os.path.abspath(__file__))


def setup_module(module):
    # override GPG homedir
    pw._gpg._OVERRIDE_HOMEDIR = os.path.join(dirname(), 'keys')


@pytest.fixture(scope='module',
                params=['db.pw', 'db.pw.gpg', 'db.pw.asc', 'db.yaml'])
def runner(request):
    # instantiate runner and provide database path
    runner = CliRunner()
    abspath = os.path.join(dirname(), request.param)
    return lambda *args: runner.invoke(pw.__main__.pw, ('--file', abspath) + args)


def test_version(runner):
    result = runner("--version")
    assert result.exit_code == 0
    assert result.output.strip().startswith("pw version ")


@pytest.mark.parametrize("args, exit_code, output_expected", [
    # default query
    (
        [],
        0,
        u"""
goggles: alice@gogglemail.com
   https://mail.goggles.com/
   second line
goggles: bob+spam@gogglemail.com
laptop: alice | default user
laptop: bob
phones.myphone
phones.samson
router: ädmin | multiple (...)
        """,
    ),
    # querying for path and user
    (
        ["goggle"],
        0,
        """
goggles: alice@gogglemail.com
   https://mail.goggles.com/
   second line
goggles: bob+spam@gogglemail.com
        """,
    ),
    (
        ["bob@"],
        0,
        """
goggles: bob+spam@gogglemail.com
laptop: bob
        """,
    ),
    (
        ["bob@goggle"],
        0,
        "goggles: bob+spam@gogglemail.com",
    ),
    (
        ["goggle", "bob"],
        0,
        "goggles: bob+spam@gogglemail.com",
    ),
    (
        ["bob@goggle", "bob"],
        0,
        "",
    ),
    # strictness
    (
        ["--strict", "myphone"],
        0,
        "phones.myphone",
    ),
    (
        ["--strict", "phones"],
        2,
        "error: multiple or no records found (but using --strict flag)",
    ),
])  # yapf: disable
def test_query(runner, args, exit_code, output_expected):
    result = runner("--echo", "--user", *args)
    assert result.exit_code == exit_code
    assert result.output.strip() == output_expected.strip()


def test_missing():
    runner = CliRunner()
    result = runner.invoke(pw.__main__.pw, ('--file', 'XXX'))
    assert result.exit_code == 1
    assert "error: password store not found at 'XXX'" == result.output.strip()


CLIPBOARD_NOT_TOUCHED = u'CLIPBOARD_NOT_TOUCHED'

@pytest.mark.parametrize("args, output_expected, clipboard_expected", [
    (
        ["laptop", "bob"],
        "laptop: bob | *** PASSWORD COPIED TO CLIPBOARD ***",
        "b0b",
    ),
    (
        ["--copy", "laptop", "bob"],
        "laptop: bob | *** PASSWORD COPIED TO CLIPBOARD ***",
        "b0b",
    ),
    (
        ["--copy", "--user", "laptop", "bob"],
        "laptop: bob | *** USERNAME COPIED TO CLIPBOARD ***",
        "bob",
    ),
    (
        ["--echo", "laptop", "bob"],
        "laptop: bob | b0b",
        CLIPBOARD_NOT_TOUCHED,
    ),
    (
        ["--echo", "--user", "laptop", "bob"],
        "laptop: bob",
        CLIPBOARD_NOT_TOUCHED,
    ),
    (
        ["--raw", "laptop", "bob"],
        "b0b",
        CLIPBOARD_NOT_TOUCHED,
    ),
    (
        ["--raw", "--user", "laptop", "bob"],
        "bob",
        CLIPBOARD_NOT_TOUCHED,
    ),
])  # yapf: disable
def test_modes(runner, args, output_expected, clipboard_expected):
    pyperclip.copy(CLIPBOARD_NOT_TOUCHED)
    result = runner(*args)
    assert result.exit_code == 0
    assert result.output.strip() == output_expected.strip()
    assert pyperclip.paste() == clipboard_expected.strip()


@pytest.mark.parametrize("args, use_clipboard, length_expected", [
    (
        ["--gen"],
        True,
        pw.__main__.RANDOM_PASSWORD_DEFAULT_LENGTH,
    ),
    (
        ["--gen", "--copy"],
        True,
        pw.__main__.RANDOM_PASSWORD_DEFAULT_LENGTH,
    ),
    (
        ["--gen", "--echo"],
        False,
        pw.__main__.RANDOM_PASSWORD_DEFAULT_LENGTH,
    ),
    (
        ["--gen", "--echo", "--raw"],
        False,
        pw.__main__.RANDOM_PASSWORD_DEFAULT_LENGTH,
    ),
    (
        ["--gen", "8"],
        True,
        8,
    ),
    (
        ["--gen", "--copy", "8"],
        True,
        8,
    ),
    (
        ["--gen", "--echo", "8"],
        False,
        8,
    ),
    (
        ["--gen", "--echo", "--raw", "8"],
        False,
        8,
    ),
])  # yapf: disable
def test_gen(runner, args, use_clipboard, length_expected):
    pyperclip.copy(CLIPBOARD_NOT_TOUCHED)
    result = runner(*args)
    assert result.exit_code == 0
    output = result.output.strip()
    clipboard = pyperclip.paste()
    if use_clipboard:
        assert output == "*** PASSWORD COPIED TO CLIPBOARD ***"
        assert len(clipboard) == length_expected
        assert all(c in pw.__main__.RANDOM_PASSWORD_ALPHABET
                   for c in clipboard)
    else:
        assert len(output) == length_expected
        assert all(c in pw.__main__.RANDOM_PASSWORD_ALPHABET for c in output)
        assert clipboard == CLIPBOARD_NOT_TOUCHED


def test_edit_without_changes(runner):
    os.environ['PW_EDITOR'] = 'echo CALLED FOR'
    os.environ['PW_GPG_RECIPIENT'] = 'test.user@localhost'
    result = runner('--edit')
    assert result.exit_code == 0
    assert result.output.strip() == 'not modified'


def test_edit_editor_missing(runner):
    os.environ.pop('PW_EDITOR', None)
    os.environ['PW_GPG_RECIPIENT'] = 'test.user@localhost'
    result = runner("--edit")
    assert result.exit_code == 1
    assert result.output.strip().startswith('error: no editor set')


@pytest.fixture(scope='module', params=['db.pw.gpg', 'db.pw.asc'])
def encrypted_runner(request):
    return runner(request)


def test_edit_recipient_missing(encrypted_runner):
    os.environ['PW_EDITOR'] = 'echo CALLED FOR'
    os.environ.pop('PW_GPG_RECIPIENT', None)
    result = encrypted_runner("--edit")
    assert result.exit_code == 1
    assert result.output.strip().startswith('error: no recipient set')


def test_edit_file_missing():
    os.environ['PW_EDITOR'] = 'echo CALLED FOR'
    os.environ['PW_GPG_RECIPIENT'] = 'test.user@localhost'
    runner = CliRunner()
    result = runner.invoke(pw.__main__.pw, ('--file', 'XXX', '--edit'))
    assert result.exit_code == 1
    assert "error: password store not found at 'XXX'" == result.output.strip()


@pytest.mark.parametrize('filename, addendum', [
    ('db.pw', 'fancy_new_entry: user pass interesting notes'),
    ('db.pw.gpg', 'fancy_new_entry: user pass interesting notes'),
    ('db.pw.asc', 'fancy_new_entry: user pass interesting notes'),
    ('db.yaml', 'fancy_new_entry: {U: user, P: pass, N: interesting notes}'),
])
def test_edit_with_changes(dirname, filename, addendum):
    fp = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
    try:
        # copy password file to temporary file
        abspath = os.path.join(dirname, filename)
        original = open(abspath, 'rb').read()
        fp.write(original)
        fp.close()

        # call pw --edit and modify file
        editor = os.path.join(dirname, 'add_a_line.py')
        os.environ['PW_EDITOR'] = '%s "%s" "%s"' % (sys.executable, editor,
                                                    addendum)
        os.environ['PW_GPG_RECIPIENT'] = 'test.user@localhost'
        runner = CliRunner()
        result = runner.invoke(pw.__main__.pw, ('--file', fp.name, '--edit'))
        assert result.exit_code == 0
        assert result.output.strip() == ''

        # try to find new entry
        store = pw.Store.load(fp.name)
        result = store.search(key_pattern='fancy', user_pattern='')
        assert len(result) == 1
        assert result[0] == pw.Entry('fancy_new_entry', 'user', 'pass',
                                     'interesting notes')
    finally:
        os.unlink(fp.name)
