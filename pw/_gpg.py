from __future__ import absolute_import, division, print_function
import os.path
import subprocess
from typing import List, Optional, cast

_HAS_ARMOR = {".gpg": False, ".asc": True}
_EXTENSIONS = _HAS_ARMOR.keys()
_OVERRIDE_HOMEDIR = None  # type: Optional[str]  # useful for unit tests


def is_encrypted(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext in _EXTENSIONS


def has_armor(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if ext not in _EXTENSIONS:
        raise ValueError("File extension not recognized as encrypted (%r)." % ext)
    return _HAS_ARMOR[ext]


def unencrypted_ext(path: str) -> str:
    root, ext = os.path.splitext(path)
    if ext in _EXTENSIONS:
        _, ext = os.path.splitext(root)
    return ext


def _base_args() -> List[str]:
    binary = os.environ.get("PW_GPG", "gpg")
    args = [binary, "--use-agent", "--quiet", "--batch", "--yes"]
    if _OVERRIDE_HOMEDIR is not None:
        args += ["--homedir", _OVERRIDE_HOMEDIR]
    return args


def decrypt(path: str) -> bytes:
    args = ["--decrypt", path]
    return cast(bytes, subprocess.check_output(_base_args() + args))


def encrypt(recipient: str, dest_path: str, content: bytes) -> None:
    args = ["--encrypt"]
    if has_armor(dest_path):
        args += ["--armor"]
    args += ["--recipient", recipient, "--output", dest_path]
    popen = subprocess.Popen(
        _base_args() + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = popen.communicate(content)
    assert popen.returncode == 0, stderr
