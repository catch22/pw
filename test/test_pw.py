#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, unicode_literals
import os
import re
import subprocess
import sys


TESTS = """
$ pw
mail.google: first-user@gmail.com *** PASSWORD COPIED TO CLIPBOARD ***
mail.google: second-user@gmail.com [...]
mobile.pin
ssh.my_private_server: root [...]
unicode.särvör

$ pw goo
mail.google: first-user@gmail.com *** PASSWORD COPIED TO CLIPBOARD ***
mail.google: second-user@gmail.com [...]

$ pw second@google
mail.google: second-user@gmail.com
  *** PASSWORD COPIED TO CLIPBOARD ***
  John's account

$ pw -E pin
mobile.pin
  12345

$ pw -S goo
pw.py: error: multiple or no records found (but using --strict mode)

$ pw -S foo
pw.py: error: multiple or no records found (but using --strict mode)

$ pw -S pin
mobile.pin
  *** PASSWORD COPIED TO CLIPBOARD ***

$ pw ssh
ssh.my_private_server: root
  *** PASSWORD COPIED TO CLIPBOARD ***
  ssh://private-server
  With great power comes great responsibility.
"""


ENV = {
  'PATH': os.environ['PATH'],
  'LC_ALL': 'en_US.UTF-8',
  'PYTHONIOENCODING': 'utf_8'
}


def test_all():
  os.chdir(os.path.dirname(__file__))
  for test in TESTS.split('\n\n'):
    input, expected_output = test.strip().split('\n', 1)
    args = re.search(r'\$ pw(.*)', input).group(1).strip().split()
    popen = subprocess.Popen([sys.executable, '../pw.py', '-D', 'passwords.yaml'] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV)
    raw_output, _ = popen.communicate()
    assert raw_output.decode('utf-8').strip() == expected_output.strip()
