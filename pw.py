#!/usr/bin/env python
from collections import namedtuple
from functools import partial
import argparse
import os, os.path
import signal
import subprocess
import sys
import xerox
import yaml
import termcolor


def main():
  VERSION = '%(prog)s 0.3.1'
  DEFAULT_DATABASE_PATH = os.path.join('~', '.passwords.yaml.asc')
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
  parser = argparse.ArgumentParser(description='Grep GPG-encrypted YAML password database.')
  parser.add_argument('query', metavar='[user@]path', nargs='?', default='', help='user and path to query for')
  parser.add_argument('-D', '--database', metavar='DB', default=DEFAULT_DATABASE_PATH, help='path to password database')
  parser.add_argument('-E', '--echo', action='store_true', help='echo passwords on console (as opposed to copying them to the clipboard)')
  parser.add_argument('-S', '--strict', action='store_true', help='fail unless precisely a single result has been found')
  parser.add_argument('-v', '--version', action='version', version=VERSION)
  args = parser.parse_args()

  # verify that database file is present
  database_path = os.path.expanduser(args.database)
  if not os.path.exists(database_path):
    print >> sys.stderr, '%s: error: password database not found at %s' % (parser.prog, database_path)
    sys.exit(-1)

  # read master password and open database
  popen = subprocess.Popen(["gpg", "--use-agent", "--no-tty", "-qd", database_path], stdout=subprocess.PIPE)
  output,_ = popen.communicate()
  if popen.returncode:
    sys.exit(-1)

  # parse YAML
  root_node = yaml.load(output)

  # create list of entries
  Entry = namedtuple('Entry', ['path', 'user', 'password', 'link', 'notes'])
  entries = []

  def normalize_path(path):
    return path.replace(' ', '_').lower()

  def collect_entry(node, path):
    # expand password-only nodes
    if type(node) != dict:
      node = {'P': node}

    # add entry
    entry = Entry(
      path=normalize_path(path),
      user=unicode(node['U']) if 'U' in node else None,
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
  entries = sorted(entries, key=lambda e: e.path)

  # parse query (split at right-most "@"" sign, since user names are typically email addresses)
  query_user, _, query_path = args.query.rpartition('@')
  query_path = normalize_path(query_path)

  # query database
  results = [e for e in entries if query_path in e.path and ((not query_user) or (e.user and query_user in e.user))]

  # perform strict mode checks
  if args.strict and len(results) != 1:
      print >> sys.stderr, '%s: error: multiple or no records found (but using --strict mode)' % parser.prog
      sys.exit(1)

  # print results
  for idx, entry in enumerate(results):
    # mark up result
    path = entry.path
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
      if args.echo:
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
      if args.echo:
        print '|', color_password(entry.password),
      elif idx == 0:
        xerox.copy(entry.password)
        print color_success('*** PASSWORD COPIED TO CLIPBOARD ***'),
      if entry.link or entry.notes:
        print '[...]',
      print