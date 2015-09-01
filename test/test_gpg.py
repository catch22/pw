from __future__ import absolute_import, division, print_function
import os, os.path, tempfile
import pytest
import pw._gpg
from pw._gpg import is_encrypted, has_armor, unencrypted_ext, decrypt, encrypt


@pytest.fixture(scope='module')
def dirname():
    return os.path.dirname(os.path.abspath(__file__))


def setup_module(module):
    # override GPG homedir
    pw._gpg._OVERRIDE_HOMEDIR = os.path.join(dirname(), 'keys')


def test_detection():
    # is_encrypted
    assert not is_encrypted('test.txt')
    assert is_encrypted('test.asc')
    assert is_encrypted('test.txt.asc')
    assert is_encrypted('test.gpg')
    assert is_encrypted('test.txt.gpg')

    # has_armor
    with pytest.raises(ValueError):
        has_armor('test.txt')
    assert has_armor('test.asc')
    assert has_armor('test.txt.asc')
    assert not has_armor('test.gpg')
    assert not has_armor('test.txt.gpg')

    # unencrypted_ext
    assert unencrypted_ext('test.txt') == '.txt'
    assert unencrypted_ext('test.asc') == ''
    assert unencrypted_ext('test.txt.asc') == '.txt'
    assert unencrypted_ext('test.gpg') == ''
    assert unencrypted_ext('test.txt.gpg') == '.txt'


@pytest.mark.parametrize("filename", ["db.pw.asc", "db.pw.gpg"])
def test_decrypt(dirname, filename):
    # manually decrypt password file & compare with unencrypted file in repository
    decrypted = decrypt(os.path.join(dirname, filename))
    unencrypted = open(os.path.join(dirname, 'db.pw'), 'rb').read()
    assert decrypted == unencrypted


@pytest.mark.parametrize("filename", ["db.pw.asc", "db.pw.gpg"])
def test_encrypt(dirname, filename):
    # load unencrypted password file
    unencrypted = open(os.path.join(dirname, 'db.pw'), 'rb').read()

    # encrypt into temporary file, decrypt again, and compare result
    fp = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
    try:
        fp.close()

        encrypt(recipient='test.user@localhost',
                dest_path=fp.name,
                content=unencrypted)
        decrypted = decrypt(fp.name)
        assert decrypted == unencrypted
    finally:
        os.unlink(fp.name)
