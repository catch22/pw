# pw [![](http://stillmaintained.com/catch22/pw.png)](http://stillmaintained.com/catch22/pw) #

Grep GPG-encrypted YAML password safes.

![](https://github.com/downloads/catch22/pw/screenshot.png)

## Installation ##

Make sure that `~/.passwords.asc` contains a valid YAML password safe (see example below for file format).

## Usage ##

    Usage: pw [options] [pathquery[:userquery]]

    Options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit
      -E, --echo  display passwords on console (as opposed to copying them to
                  the clipboard)

## Example ##

### Password Safe ###

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

### Usage ###

Display all records:

    $ pw
    mail.google: first-user@gmail.com
    mail.google: second-user@gmail.com | ...
    mobile_pin
    ssh.my_private_server: root | ssh://private-server | ...
    
Display records whose (normalised) path contains the substring "goo":

    $ pw goo
    mail.google: first-user@gmail.com
    mail.google: second-user@gmail.com | ...
    
Display records whose path contains "goo" and whose associated user name contains "sec":

    $ pw goo:sec
    mail.google: second-user@gmail.com | password copied to clipboard
      John's account

Observe that, since there is only a single match, the password is automatically copied to the clipboard.

Display records whose path contains "ssh" and display all passwords on the console:
      
    $ pw -E ssh
    ssh.my_private_server: root | *****
      ssh://private-server
      With great power comes great responsibility.

Similarly for the cell phone PIN:

    $ pw -E pin
    mobile_pin | 12345

## Acknowledgments ##

`pw` uses a fixed version of the `pyperclip` python module by Al Sweigart.