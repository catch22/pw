from __future__ import absolute_import, division, print_function
from collections import namedtuple
from io import StringIO
from shlex import shlex
from typing import List, Iterable
from . import _gpg

Entry = namedtuple("Entry", ["key", "user", "password", "notes"])


def _normalized_key(key: str) -> str:
    return key.replace(" ", "_").lower()


class Store:
    """Password store."""

    def __init__(self, path: str, entries: Iterable[Entry]) -> None:
        # normalize keys
        self.entries = [e._replace(key=_normalized_key(e.key)) for e in entries]
        self.path = path

    def search(self, key_pattern: str, user_pattern: str) -> List[Entry]:
        """Search database for given key and user pattern."""
        # normalize key
        key_pattern = _normalized_key(key_pattern)

        # search
        results = []
        for entry in self.entries:
            if key_pattern in entry.key and user_pattern in entry.user:
                results.append(entry)

        # sort results according to key (stability of sorted() ensures that the order of accounts for any given key remains untouched)
        return sorted(results, key=lambda e: e.key)

    @staticmethod
    def load(path: str) -> "Store":
        """Load password store from file."""
        # load source (decrypting if necessary)
        if _gpg.is_encrypted(path):
            src_bytes = _gpg.decrypt(path)
        else:
            src_bytes = open(path, "rb").read()
        src = src_bytes.decode("utf-8")

        # parse database source
        ext = _gpg.unencrypted_ext(path)
        if ext in [".yml", ".yaml"]:
            from . import _yaml

            entries = _yaml.parse_entries(src)
        else:
            entries = _parse_entries(src)

        return Store(path, entries)


class SyntaxError(Exception):
    def __init__(self, lineno: int, line: str, reason: str) -> None:
        super(SyntaxError, self).__init__(
            "line %s: %s (%r)" % (lineno + 1, reason, line)
        )


_EXPECT_ENTRY = "expecting entry"
_EXPECT_ENTRY_OR_NOTES = "expecting entry or notes"


def _parse_entries(src: str) -> List[Entry]:
    entries = []  # type: List[Entry]
    state = _EXPECT_ENTRY

    for lineno, line in enumerate(src.splitlines()):
        # empty lines are skipped (but also terminate the notes section)
        sline = line.strip()
        if not sline or line.startswith("#"):
            state = _EXPECT_ENTRY
            continue

        # non-empty line with leading spaces is interpreted as a notes line
        if line[0] in [" ", "\t"]:
            if state != _EXPECT_ENTRY_OR_NOTES:
                raise SyntaxError(lineno, line, state)

            # add line of notes
            notes = entries[-1].notes
            if notes:
                notes += "\n"
            notes += sline
            entries[-1] = entries[-1]._replace(notes=notes)
            continue

        # otherwise, parse as an entry
        sio = StringIO(line)
        lexer = shlex(sio, posix=True)  # type: ignore
        lexer.whitespace_split = True

        try:
            key = lexer.get_token()
        except ValueError as e:
            raise SyntaxError(lineno, line, str(e))
        key = key.rstrip(":")
        assert key

        try:
            user = lexer.get_token()
        except ValueError as e:
            raise SyntaxError(lineno, line, str(e))

        try:
            password = lexer.get_token()
        except ValueError as e:
            raise SyntaxError(lineno, line, str(e))

        if not user and not password:
            raise SyntaxError(lineno, line, state)

        if not password:
            password = user
            user = notes = u""
        else:
            password = password
            notes = sio.read().strip()

        entries.append(Entry(key, user, password, notes))
        state = _EXPECT_ENTRY_OR_NOTES

    return entries
