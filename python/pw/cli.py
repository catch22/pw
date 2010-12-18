#!/usr/bin/env python
import getpass
import keepass.kpdb
import os.path
import optparse
import pyperclip
import signal
import sys

VERSION = '%prog 0.1 alpha'
DATABASE_PATH = '~/.keepass.kdb'
UUID_KPX_METAINFO = '00000000000000000000000000000000'

# install silent Ctrl-C handler
def handle_sigint(*_):
  print
  sys.exit(1)
signal.signal(signal.SIGINT, handle_sigint)

# parse command-line options
parser = optparse.OptionParser(usage='Usage: %prog [options] [query]', version=VERSION)
parser.add_option('-d', '--display', action='store_true', help='display passwords on console (as opposed to copying them to the clipboard)')
opts, args = parser.parse_args()

# verify that database file is present
database_path = os.path.expanduser(DATABASE_PATH)
if not os.path.exists(database_path):
  print 'Error: KeePass database not found at %s.' % DATABASE_PATH
  sys.exit(1)

# read master password and open database
master_password = getpass.getpass()
try:
  db = keepass.kpdb.Database(database_path, master_password)
except keepass.kpdb.DecryptionFailed, df:
  print df
  sys.exit(1)

# determine (not yet canonical) hierarchical group paths (by groupid)
def get_group_paths_and_backup_groupid(groups):
  group_paths = {}
  current_path_stack = []
  last_group_name = None
  for g in db.groups:
    if g.group_name == 'Backup' and g.level == 0:
      backup_groupid = g.groupid

    current_level = len(current_path_stack)
    if g.level < current_level:
      while g.level < len(current_path_stack):
        current_path_stack.pop()
    elif g.level == current_level + 1:
      current_path_stack += [last_group_name]
    else:
      assert g.level == current_level

    group_paths[g.groupid] = '.'.join(current_path_stack + [g.group_name])
    last_group_name = g.group_name
  return group_paths, backup_groupid

group_paths, backup_groupid = get_group_paths_and_backup_groupid(db.groups)

# create list of entries sorted by their canonical path
def make_canonical_path(path):
  return path.replace(' ', '_').lower()

for e in db.entries:
  e.canonical_path = make_canonical_path(group_paths[e.groupid] + '.' + e.title)

entries = sorted((e for e in db.entries if e.uuid != UUID_KPX_METAINFO and e.groupid != backup_groupid), key=lambda e: e.canonical_path)

# perform query
query = make_canonical_path(args[0]) if args else ''
results = [e for e in entries if e.canonical_path.find(query) != -1]

# print results
if len(results) == 0:
  print 'no record found'
  sys.exit(0)

for e in results:
  # mark up result
  title = e.canonical_path
  if query:
    title = ('\x1b[33m' + query + '\x1b[0m').join(title.split(query))
  print '%s: %s' % (title,e.username),

  # display password or copy to clipboard (if only match)
  if opts.display:
    print '| \x1b[31m%s\x1b[0m' % e.password,
  elif len(results) == 1:
    pyperclip.setcb(e.password)
    print '| \x1b[32mpassword copied to clipboard\x1b[0m',

  # display url and notes
  if e.url and len(results) > 1:
    print '| %s' % e.url,
  if e.notes and len(results) > 1:
    print '| ...',
  print

  if e.url and len(results) == 1:
    print '  %s' % e.url
  if e.notes and len(results) == 1:
    print '  %s' % e.notes