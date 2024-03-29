# coding: utf-8
import pytest
import os.path
import pw
from pw.store import _normalized_key, _parse_entries, Entry, Store, SyntaxError


def test_normalized_key():
    assert _normalized_key("My secret aCcOuNt") == "my_secret_account"


@pytest.mark.parametrize(
    "src, expected",
    [
        ("", []),
        (
            """
# this is a comment
        """,
            [],
        ),
        (
            """
key pass
key: pass
#
"key word" pass
"key word": pass
#
key "pass word"
key: "pass word"
#
"key word" "pass word"
"key word": "pass word"
        """,
            [
                Entry(key="key", user="", password="pass", notes=""),
                Entry(key="key", user="", password="pass", notes=""),
                Entry(key="key word", user="", password="pass", notes=""),
                Entry(key="key word", user="", password="pass", notes=""),
                Entry(key="key", user="", password="pass word", notes=""),
                Entry(key="key", user="", password="pass word", notes=""),
                Entry(key="key word", user="", password="pass word", notes=""),
                Entry(key="key word", user="", password="pass word", notes=""),
            ],
        ),
        (
            """
key user pass
key: user pass
#
"key word" "user name" "pass word"
"key word": "user name" "pass word"
        """,
            [
                Entry(key="key", user="user", password="pass", notes=""),
                Entry(key="key", user="user", password="pass", notes=""),
                Entry(key="key word", user="user name", password="pass word", notes=""),
                Entry(key="key word", user="user name", password="pass word", notes=""),
            ],
        ),
        (
            """
key user pass these are some interesting notes
key: user pass these are some interesting notes
#
"key word" "user name" "pass word" these are some interesting notes
"key word": "user name" "pass word" these are some interesting notes
        """,
            [
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="these are some interesting notes",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="these are some interesting notes",
                ),
                Entry(
                    key="key word",
                    user="user name",
                    password="pass word",
                    notes="these are some interesting notes",
                ),
                Entry(
                    key="key word",
                    user="user name",
                    password="pass word",
                    notes="these are some interesting notes",
                ),
            ],
        ),
        (
            """
key pass
    notes line 1
    notes line 2
key: pass
    notes line 1
    notes line 2
#
key "" pass notes line 0
    notes line 1
    notes line 2
key: "" pass notes line 0
    notes line 1
    notes line 2
#
key "" pass notes line 0
    # notes line 0.5
    notes line 1
    # notes line 1.5
    notes line 2
key "" pass notes line 0
    # notes line 0.5
    notes line 1
    # notes line 1.5
    notes line 2
        """,
            [
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 0\nnotes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 0\nnotes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 0\n# notes line 0.5\nnotes line 1\n# notes line 1.5\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="",
                    password="pass",
                    notes="notes line 0\n# notes line 0.5\nnotes line 1\n# notes line 1.5\nnotes line 2",
                ),
            ],
        ),
        (
            """
key user pass
    notes line 1
    notes line 2
key: user pass
    notes line 1
    notes line 2
#
key user pass notes line 0
    notes line 1
    notes line 2
key: user pass notes line 0
    notes line 1
    notes line 2
#
key user pass notes line 0
    # notes line 0.5
    notes line 1
    # notes line 1.5
    notes line 2
key user pass notes line 0
    # notes line 0.5
    notes line 1
    # notes line 1.5
    notes line 2
        """,
            [
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 0\nnotes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 0\nnotes line 1\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 0\n# notes line 0.5\nnotes line 1\n# notes line 1.5\nnotes line 2",
                ),
                Entry(
                    key="key",
                    user="user",
                    password="pass",
                    notes="notes line 0\n# notes line 0.5\nnotes line 1\n# notes line 1.5\nnotes line 2",
                ),
            ],
        ),
        (
            """
"السلام عليكم": 임요환 Нет Εις το επανιδείν
        """,
            [
                Entry(
                    key="السلام عليكم",
                    user="임요환",
                    password="Нет",
                    notes="Εις το επανιδείν",
                )
            ],
        ),
    ],
)  # yapf: disable
def test_parse_entries(src, expected):
    entries = _parse_entries(src.strip())
    assert entries == expected


@pytest.mark.parametrize(
    "src, expected_error_prefix",
    [
        (
            """
foo: bar
  note line 1

  note line 2
        """,
            "line 4: expecting entry (",
        ),
        (
            """
foo: bar
  note line 1
# non-indented comment
  note line 2
        """,
            "line 4: expecting entry (",
        ),
        (
            """
foo: bar
baz
boink: zonk
        """,
            "line 2: expecting entry or notes (",
        ),
        (
            """
foo": bar
        """,
            "line 1: No closing quotation (",
        ),
        (
            """
foo: "bar
        """,
            "line 1: No closing quotation (",
        ),
        (
            """
foo: bar "baz
        """,
            "line 1: No closing quotation (",
        ),
    ],
)  # yapf: disable
def test_parse_entries_syntax_errors(src, expected_error_prefix):
    with pytest.raises(SyntaxError) as excinfo:
        _parse_entries(src.strip())
    assert str(excinfo.value).startswith(expected_error_prefix)


@pytest.fixture(scope="module", params=["db.pw", "db.pw.gpg", "db.pw.asc"])
def store(request, dirname):
    abspath = os.path.join(dirname, request.param)
    return Store.load(abspath)


def test_store_entries(store):
    expected = [
        Entry("laptop", "alice", "4l1c3", "default user"),
        Entry("laptop", "bob", "b0b", ""),
        Entry(
            "goggles",
            "alice@gogglemail.com",
            "12345",
            "https://mail.goggles.com/\nsecond line",
        ),
        Entry("goggles", "bob+spam@gogglemail.com", "abcde", ""),
        Entry("router", "ädmin", "gamma zeta", "multiple\nlines\nof\nnotes"),
        Entry("phones.myphone", "", "0000", ""),
        Entry("phones.samson", "", "111", ""),
    ]  # yapf: disable
    expected = sorted(expected, key=lambda e: e.key)
    got = sorted(store.entries, key=lambda e: e.key)
    assert got == expected


def test_store_search(store):
    # search for key
    got = store.search(key_pattern="oggle", user_pattern="")
    expected = [
        Entry(
            "goggles",
            "alice@gogglemail.com",
            "12345",
            "https://mail.goggles.com/\nsecond line",
        ),
        Entry("goggles", "bob+spam@gogglemail.com", "abcde", ""),
    ]
    assert got == expected

    # search for user
    got = store.search(key_pattern="", user_pattern="bob")
    expected = [
        Entry("goggles", "bob+spam@gogglemail.com", "abcde", ""),
        Entry("laptop", "bob", "b0b", ""),
    ]
    assert got == expected

    # search for both
    got = store.search(key_pattern="oggle", user_pattern="spam")
    expected = [Entry("goggles", "bob+spam@gogglemail.com", "abcde", "")]
    assert got == expected
