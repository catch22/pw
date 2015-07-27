# pw [![Build Status](https://travis-ci.org/catch22/pw.svg?branch=master)](https://travis-ci.org/catch22/pw) [![Latest Version](https://badge.fury.io/py/pw.svg)](https://pypi.python.org/pypi/pw/)

`pw` is a Python tool to search in a GPG-encrypted password database.

```
Usage: pw [OPTIONS] [USER@][KEY] [USER]

  Search for USER and KEY in GPG-encrypted password file.

Options:
  --copy / --no-copy          copy password to clipboard (default)
  -E, --echo / --no-echo      print password to console
  -S, --strict / --no-strict  fail unless precisely a single result has been found
  --raw / --no-raw            output password only
  -f, --file PATH             password file
  --edit                      launch editor to edit password database
  -v, --version               print version information and exit
  --help                      Show this message and exit.
```


## Installation

To install `pw`, simply run:

```bash
$ pip install pw
```
