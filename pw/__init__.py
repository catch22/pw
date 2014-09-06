from collections import namedtuple
import os.path, subprocess, sys
import click, gnupg, yaml
try:
  from yaml import CLoader as Loader
except ImportError:
  from yaml import Loader as Loader

if sys.version_info < (3, 0):
  str = unicode


__version__ = '0.7'


# GPG
GPG_EXTENSIONS = ['.gpg', '.asc']
GPG_ARMOR = {'.gpg': False, '.asc':  True}

def gpg_decrypt(path):
  gpg = gnupg.GPG(gnupghome=os.environ.get('PW_GPG_HOMEDIR'), use_agent=True)
  data = gpg.decrypt_file(open(path, "rb"))
  assert data.ok, data.status
  return data.data

def gpg_encrypt(recipient, src_path, dest_path):
  """encrypt file for given recipient"""
  _, ext = os.path.splitext(dest_path)
  gpg = gnupg.GPG(gnupghome=os.environ.get('PW_GPG_HOMEDIR'), use_agent=True)
  gpg.encrypt_file(open(src_path, "rb"), recipient, armor=GPG_ARMOR[ext], output=dest_path)


# Entry and Database
def normalize_key(key):
  return key.replace(' ', '_').lower()

Entry = namedtuple('Entry', ['key', 'user', 'password', 'link', 'notes'])

def make_entry(key, dict):
  return Entry(
    key=key,
    user=str(dict.get('U', '')),
    password=str(dict.get('P', '')),
    link=str(dict.get('L', '')),
    notes=str(dict.get('N', '')),
  )

class Database:
  """Password database"""
  def __init__(self, root_node):
    self.root_node = root_node

  def search(self, key_pattern, user_pattern):
    """search database for given substrings of key and user"""
    key_pattern = normalize_key(key_pattern)
    for entry in self._collect_entries(self.root_node, ''):
      if key_pattern in entry.key and user_pattern in entry.user:
        yield entry

  @staticmethod
  def default_path():
    return os.path.expanduser(os.path.join('~', '.passwords.yaml.asc'))

  @staticmethod
  def load_source(path):
    """return database YAML source and boolean value that indicates if the file was encrypted"""
    # verify that database file is present
    if not os.path.exists(path):
      click.echo('error: password database not found at %s' % path, file=sys.stderr)
      sys.exit(1)

    # return database source (decrypt depending on file extension)
    _, ext = os.path.splitext(path)
    if ext in GPG_EXTENSIONS:
      src = gpg_decrypt(path)
      return src, True

    src = open(path, 'rb').read()
    return src, False

  @staticmethod
  def load(path):
    """load database"""
    src, _ = Database.load_source(path)
    root_node = yaml.load(src, Loader=Loader)
    return Database(root_node)

  def _collect_entries(self, current_node, current_key):
    # list of accounts?
    if isinstance(current_node, list):
      for child_node in current_node:
        assert isinstance(child_node, dict), "expected list of accounts"
        yield make_entry(current_key, child_node)
      return

    # single acccount?
    if isinstance(current_node, dict) and 'P' in current_node:
      yield make_entry(current_key, current_node)
      return

    # single password?
    if not isinstance(current_node, dict):
      yield Entry(key=current_key, user='', password=str(current_node), link='', notes='')
      return

    # otherwise: subtree!
    for key, child_node in current_node.items():
      # ignore entries in parentheses
      if key.startswith('('):
        continue

      # recurse
      key = normalize_key(key)
      for entry in self._collect_entries(child_node, current_key + '.' + key if current_key else key):
        yield entry
