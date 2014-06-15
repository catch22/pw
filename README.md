# pw [![Build Status](https://travis-ci.org/catch22/pw.svg?branch=master)](https://travis-ci.org/catch22/pw)

`pw` is a Python tool to search in a GPG-encrypted password database.

```
Usage: pw [OPTIONS] [USER@][KEY]

  Search for USER and KEY in GPG-encrypted password database.

Options:
  --copy / --no-copy      copy password to clipboard
  -E, --echo / --no-echo  print password to console
  --open / --no-open      open link in browser
  --strict / --no-strict  fail unless precisely a single result has been found
  --database-path PATH    path to password database
  --edit                  launch editor to edit password database
  -v, --version           print version information and exit
  --help                  Show this message and exit.
```


## Installation

To install `pw`, simply run:

```bash
$ pip install pw
```


## Password Database, File Format, and Editing

By default, the password database is located at `~/.passwords.yaml.asc` and automatically decrypted by using [GnuPG](https://www.gnupg.org) if the file extension is `.asc` or `.gpg`.
It uses a straighforward [YAML](http://www.yaml.org/) format as in the following example, which is hopefully self-explanatory:

```yaml
Mail:
  Google:
    - U: first-user@gmail.com
      P: "*****"
      L: https://mail.google.com/
    - U: second-user@gmail.com
      P: "*****"
      N: "John's account"
SSH:
  My Private Server:
    U: root
    P: "*****"
    N: "With great power comes great responsibility."
  (An Old Entry That Is Ignored):
    U: foo
    P: bar

Mobile:
  PIN: 12345   # shortcut notation (only provide password)
```

To edit the database, use `pw --edit`. This requires that the environment variable `PW_GPG_RECIPIENT` is set to the key with which the database should be encrypted and invokes the editor specified in the `PW_EDITOR` environment variable (make sure to use blocking mode, e.g., `subl --wait`).

*Warning*: This feature requires that the password database is temporarily stored in plain text in the file system, data leaks may arise. To some extend, this can be mitigated by using, e.g., `tmpfs` and by providing the editor with the adequate options that ensure that no backup copies, swap files, etc. are created.
