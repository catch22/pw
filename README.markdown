# pw

Grep Password Safe 2.0 / pwsafe / KeePass V1.x / KeePassX password safes.

## Installation

Make sure that either `.pwsafe.dat` or `.pwsafe.kdb` exist.
`pw` will look for password safes in this order.

## Usage

    Usage: pw [options] [query]

    Options:
      --version      show program's version number and exit
      -h, --help     show this help message and exit
      -d, --display  display passwords on console (as opposed to copying them to
                     the clipboard)

## Acknowledgments

`pw` uses a fork of the excellent `python-keepass` module by Brett Viren as well as a fixed version of the `pyperclip` python module by Al Sweigart.