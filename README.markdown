# pw [![](http://stillmaintained.com/catch22/pw.png)](http://stillmaintained.com/catch22/pw)

Grep GPG-encrypted YAML password safes.

## Installation

Make sure that `.passwords.asc` exists.

## Usage

    Usage: pw [options] [pathquery[:userquery]]

    Options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit
      -E, --echo  display passwords on console (as opposed to copying them to
                  the clipboard)

## Acknowledgments

`pw` uses a fixed version of the `pyperclip` python module by Al Sweigart.