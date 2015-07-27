import os.path
from collections import namedtuple
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from shlex import shlex
from . import _gpg

Entry = namedtuple('Entry', ['key', 'user', 'password', 'notes'])


def normalized_key(key):
    return key.replace(' ', '_').lower()


class Store:
    """Password store."""

    def __init__(self, path, entries):
        self.path = path
        self.entries = [e._replace(key=normalized_key(e.key)) for e in entries]

    def search(self, key_pattern, user_pattern):
        """Search database for given key and user pattern."""
        key_pattern = normalized_key(key_pattern)
        for entry in self.entries:
            if key_pattern in entry.key and user_pattern in entry.user:
                yield entry

    @staticmethod
    def load(path):
        """Load password store from file."""
        # load source
        src = Store._load_source(path)
        ext = _gpg.unencrypted_ext(path)

        # parse database source
        if ext in ['.yml', '.yaml']:
            from . import _yaml
            entries = _yaml.parse_entries(src)
        else:
            entries = _parse_entries(src)

        return Store(path, entries)

    @staticmethod
    def _load_source(path):
        """Load database source (decrypting if necessary)."""
        if _gpg.is_encrypted(path):
            return _gpg.decrypt(path)
        return open(path, 'rb').read()


class SyntaxError(Exception):
    def __init__(self, lineno, line, reason):
        super(SyntaxError, self).__init__('line %s: %s (%r)' %
                                          (lineno, reason, line))


EXPECT_ENTRY = 'expecting entry'
EXPECT_ENTRY_OR_NOTES = 'expecting entry or notes'


def _parse_entries(src):
    entries = []
    state = EXPECT_ENTRY

    for lineno, line in enumerate(src.splitlines()):
        # empty lines are skipped (but also terminate the notes section)
        sline = line.strip()
        if not sline or sline.startswith('#'):
            state = EXPECT_ENTRY
            continue

        # non-empty line with leading spaces is interpreted as a notes line
        if line[0] in [' ', '\t']:
            if state != EXPECT_ENTRY_OR_NOTES:
                raise SyntaxError(lineno, line, state)

            # add line of notes
            notes = entries[-1].notes
            if notes:
                notes += "\n"
            notes += sline
            entries[-1] = entries[-1]._replace(notes=notes)
            continue

        # parse line using shlex
        sio = StringIO(line)
        lexer = shlex(sio, posix=True)
        lexer.whitespace_split = True

        # otherwise, parse as an entry
        key = lexer.get_token()
        if not key:
            raise SyntaxError(lineno, line, state)
        key = key.decode('utf-8').rstrip(':')

        user = lexer.get_token()
        if not user:
            raise SyntaxError(lineno, line, state)
        user = user.decode('utf-8')

        password = lexer.get_token()
        if not password:
            password = user
            user = notes = ''
        else:
            password = password.decode('utf-8')
            notes = sio.read().strip()

        entries.append(Entry(key, user, password, notes))
        state = EXPECT_ENTRY_OR_NOTES

    return entries
