pw |stillmantained|
===================

.. image:: http://catch22.github.com/pw/screenshot1.png
   :align: center

.. image:: http://catch22.github.com/pw/screenshot2.png
   :align: center

.. image:: http://catch22.github.com/pw/screenshot3.png
   :align: center


Usage
-----

::

  usage: pw [-h] [-D DB] [-E] [-S] [-v] [[user@]path]

  Grep GPG-encrypted YAML password database.

  positional arguments:
    [user@]path           user and path to query for

  optional arguments:
    -h, --help            show this help message and exit
    -D DB, --database DB  path to password database
    -E, --echo            echo passwords on console (as opposed to copying them
                          to the clipboard)
    -S, --strict          fail unless precisely a single result has been found
    -v, --version         show program's version number and exit

Installation
------------

To install **pw**, simply run::

  pip install pw


Password database
-----------------

By default, the password database is located at ``~/.passwords.yaml.asc``.
It uses a straighforward `YAML <http://www.yaml.org/>`_ format as in the following example, which is hopefully self-explanatory:

.. code:: yaml

  Mail:
    Google:
      - U: first-user@gmail.com
        P: "*****"
      - U: second-user@gmail.com
        P: "*****"
        N: "John's account"
  SSH:
    My Private Server:
      U: root
      P: "*****"
      L: ssh://private-server
      N: "With great power comes great responsibility."

  Mobile:
    PIN: 12345   # shortcut notation (only provide password)


.. |stillmantained| image:: http://stillmaintained.com/catch22/pw.png
  :target: http://stillmaintained.com/catch22/pw