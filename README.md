# pw [![](http://stillmaintained.com/catch22/pw.png)](http://stillmaintained.com/catch22/pw) #

Grep GPG-encrypted YAML password safes.

![](https://github.com/downloads/catch22/pw/screenshot.png)

## Installation ##

* Install dependencies:

    $ pip install pyyaml
    $ pip install xerox

* Install pw:

    TODO

Make sure that `~/.passwords.asc` contains a valid YAML password safe (see example below for file format).

## Usage ##

    Usage: pw [options] [pathquery[:userquery]]

    Options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit
      -E, --echo  display passwords on console (as opposed to copying them to
                  the clipboard)

## Sample `.passwords.asc` ##

    Mail:
      Google:
        - U: first-user@gmail.com
          P: "*****"
        - U: second-user@gmail.com
          P: "*****"
          N: John's account
    SSH:
      My Private Server:
        U: root
        P: "*****"
        L: ssh://private-server
        N: "With great power comes great responsibility."
    
    Mobile PIN: 12345   # shortcut notation (only provide password)
