===================
pw |stillmantained|
===================

Grep GPG-encrypted YAML password safes.

.. image:: https://github.com/downloads/catch22/pw/screenshot.png
   :align: center

------------
Installation
------------

To install **pw**, simply run::

  pip install pw

Make sure that ``~/.passwords.yaml.asc`` contains a valid YAML password safe (see example below for file format).

-----
Usage
-----

::

  usage: pw [-h] [-E] [-S] [-v] [[userquery@]pathquery]

  Grep GPG-encrypted YAML password safe.

  positional arguments:
    [[userquery@]pathquery]

  optional arguments:
    -h, --help            show this help message and exit
    -E, --echo            echo passwords on console (as opposed to copying them
                          to the clipboard)
    -S, --strict          fail unless precisely a single result has been found
    -v, --version         show program's version number and exit

------------------------------
Sample ``.passwords.yaml.asc``
------------------------------

::

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


.. |stillmantained| image:: http://stillmaintained.com/catch22/pw.png
  :target: http://stillmaintained.com/catch22/pw
