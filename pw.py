#!/usr/bin/env python
from collections import namedtuple
from functools import partial
import os, os.path
import optparse
import signal
import subprocess
import sys
import xerox
import yaml
import termcolor


def main():
  VERSION = '%prog 0.3.0'
  DATABASE_PATH = os.path.join('~', '.passwords.yaml.asc')
  HAVE_COLOR_TERM = os.getenv('COLORTERM') or 'color' in os.getenv('TERM', 'default')

  # install silent Ctrl-C handler
  def handle_sigint(*_):
    print
    sys.exit(1)
  signal.signal(signal.SIGINT, handle_sigint)

  # disable termcolor for terminals not supporting color
  colored = termcolor.colored if HAVE_COLOR_TERM else lambda text, *args, **kwargs: text

  # color wrappers
  color_match = partial(colored, color='yellow', attrs=['bold'])
  color_password = partial(colored, color='red', attrs=['bold'])
  color_success = partial(colored, color='green', attrs=['bold', 'reverse'])

  # parse command-line options
  parser = optparse.OptionParser(usage='Usage: %prog [options] [[userquery@]pathquery]', version=VERSION)
  parser.add_option('-E', '--echo', action='store_true', help='echo passwords on console (as opposed to copying them to the clipboard)')
  parser.add_option('-S', '--strict', action='store_true', help='fail if more than one result has been found')
  opts, args = parser.parse_args()

  # verify that database file is present
  database_path = os.path.expanduser(DATABASE_PATH)
  if not os.path.exists(database_path):
    print 'Error: Password safe not found at %s.' % database_path
    sys.exit(-1)

  # read master password and open database
  popen = subprocess.Popen(["gpg", "--use-agent", "--no-tty", "-qd", database_path], stdout=subprocess.PIPE)
  output,_ = popen.communicate()
  if popen.returncode:
    sys.exit(-1)

  # parse YAML
  root_node = yaml.load(output)

  # create list of entries
  Entry = namedtuple('Entry', ['normalized_path', 'user', 'password', 'link', 'notes'])
  entries = []

  def normalize_path(path):
    return path.replace(' ', '_').lower()

  def collect_entry(node, path):
    # expand password-only nodes
    if type(node) != dict:
      node = {'P': node}

    # add entry
    entry = Entry(
      normalized_path=normalize_path(path),
      user=unicode(node.get('U', '')),
      password=str(node.get('P', '')),   # xerox had some problems with unicode strings -> fail early
      link=node.get('L', None),
      notes=node.get('N', None)
    )
    entries.append(entry)

  def collect_entries(node, path):
    # list of accounts for the same path?
    if type(node) == list:
      for n in node:
        collect_entry(n, path)
    elif type(node) == dict:
      # account or subtree?
      if node.has_key('P'):
        collect_entry(node, path)
      else:
        for (key,value) in node.iteritems():
          collect_entries(value, path + '.' + key if path else key)
    else:
      collect_entry(node, path)

  collect_entries(root_node, '')

  # sort entries according to normalized path (stability of sorted() ensures that the order of accounts for a given path remains untouched)
  entries = sorted(entries, key=lambda e: e.normalized_path)

  # perform query
  if args:
    # split at right-most @ sign (user names are typically email addresses)
    query_user, _, query_path = args[0].rpartition('@')
    query_path = normalize_path(query_path)
  else:
    query_user, query_path = '', ''
  results = [e for e in entries if query_path in e.normalized_path and ((not query_user) or (e.user and query_user in e.user))]

  # print results
  if len(results) == 0:
    print 'no record found'
    sys.exit(-2)

  if opts.strict and len(results) > 1:
    print 'multiple records found'
    sys.exit(-3)

  for idx, entry in enumerate(results):
    # mark up result
    path = entry.normalized_path
    user = entry.user if entry.user else ''
    if query_path:
      path = color_match(query_path).join(path.split(query_path))
    if query_user:
      user = color_match(query_user).join(user.split(query_user))
    if user:
      print '%s: %s' % (path,user),
    else:
      print path,

    # only result?
    if len(results) == 1:
      # display entry in expanded mode
      print
      if opts.echo:
        print '  ', color_password(entry.password)
      else:
        xerox.copy(entry.password)
        print '  ', color_success('*** PASSWORD COPIED TO CLIPBOARD ***')
      if entry.link:
        print '  ', entry.link
      if entry.notes:
        print '  ', entry.notes
    else:
      # otherwise abbreviate results
      if opts.echo:
        print '|', color_password(entry.password),
      elif idx == 0:
        xerox.copy(entry.password)
        print color_success('*** PASSWORD COPIED TO CLIPBOARD ***'),
      if entry.link or entry.notes:
        print '[...]',
      print