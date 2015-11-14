from __future__ import absolute_import, division, print_function
import os.path
import subprocess

_HAS_ARMOR = {'.gpg': False, '.asc': True}
_EXTENSIONS = _HAS_ARMOR.keys()
_OVERRIDE_HOMEDIR = None  # useful for unit tests


def is_encrypted(path):
    _, ext = os.path.splitext(path)
    return ext in _EXTENSIONS


def has_armor(path):
    _, ext = os.path.splitext(path)
    if ext not in _EXTENSIONS:
        raise ValueError('File extension not recognized as encrypted (%r).' %
                         ext)
    return _HAS_ARMOR[ext]


def unencrypted_ext(path):
    root, ext = os.path.splitext(path)
    if ext in _EXTENSIONS:
        _, ext = os.path.splitext(root)
    return ext


def _base_args():
    args = ['gpg2', '--use-agent', '--quiet', '--batch', '--yes']
    if _OVERRIDE_HOMEDIR:
        args += ['--homedir', _OVERRIDE_HOMEDIR]
    return args


def decrypt(path):
    args = ['--decrypt', path]
    return subprocess.check_output(_base_args() + args)


def encrypt(recipient, dest_path, content):
    args = ["--encrypt"]
    if has_armor(dest_path):
        args += ["--armor"]
    args += ["--recipient", recipient, "--output", dest_path]
    popen = subprocess.Popen(_base_args() + args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    stdout, stderr = popen.communicate(content)
    assert popen.returncode == 0, stderr
