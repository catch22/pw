# pw [![Build Status](https://travis-ci.org/catch22/pw.svg?branch=master)](https://travis-ci.org/catch22/pw) [![Latest Version](https://badge.fury.io/py/pw.svg)](https://pypi.python.org/pypi/pw/)

`pw` is a Python tool to search in a GPG-encrypted password database.

```
Usage: pw [OPTIONS] [USER@][KEY] [USER]

  Search for USER and KEY in GPG-encrypted password file.

Options:
  -C, --copy       Copy password to clipboard (default).
  -E, --echo       Print password to console.
  -R, --raw        Output password only.
  -S, --strict     Fail unless precisely a single result has been found.
  -U, --user       Copy or display username instead of password.
  -f, --file PATH  Path to password file.
  --edit           Launch editor to edit password database and exit.
  --gen            Generate a random password and exit.
  --version        Show the version and exit.
  --help           Show this message and exit.
```


## Installation

To install `pw`, simply run:

```bash
$ pip install pw
```
