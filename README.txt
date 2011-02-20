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

  Usage: pw [options] [pathquery[:userquery]]

  Options:
    --version   show program's version number and exit
    -h, --help  show this help message and exit
    -E, --echo  display passwords on console (as opposed to copying them to
                the clipboard)

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
