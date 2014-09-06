#!/usr/bin/env python
from functools import partial
import os, os.path, pipes, signal, subprocess, sys, tempfile, time
import click
import xerox
from . import __version__, Database, gpg_encrypt

if sys.version_info < (3, 0):
  str = unicode


style_match = partial(click.style, fg='yellow', bold=True)
style_password = partial(click.style, fg='red', bold=True)
style_success = partial(click.style, fg='green', bold=True, reverse=True)


def print_version(ctx, param, value):
  """print version information and exit"""
  if not value or ctx.resilient_parsing:
    return
  click.echo('pw %s' % __version__)
  ctx.exit()


def wait_for_editor(path):
  editor = os.environ.get('PW_EDITOR')  # do not use EDITOR environment variable (rather force user to make a concious choice)
  if not editor:
    click.echo('error: no editor set in PW_EDITOR environment variables')
    sys.exit(1)
  click.echo("waiting for editor...")
  cmd = editor + " " + pipes.quote(path)
  return subprocess.check_call(cmd, shell=True)

def edit_database(ctx, param, value):
  """edit password database and exit"""
  if not value or ctx.resilient_parsing:
    return

  # load database contents
  database_path = ctx.params.get('database_path', Database.default_path())
  source, was_encrypted = Database.load_source(database_path)

  # not encrypted? simply launch the editor with the database
  if not was_encrypted:
    wait_for_editor(database_path)
    ctx.exit()

  # otherwise the process is somewhat more complicated...
  recipient = os.environ.get('PW_GPG_RECIPIENT')
  if not recipient:
    click.echo("error: environment variable PW_GPG_RECIPIENT not set")
    sys.exit(1)

  # save decrypted database to temporary file
  temp_src_fd, temp_src_path = tempfile.mkstemp(suffix='.yaml')
  try:
    with os.fdopen(temp_src_fd, "wb") as fp:
      fp.write(source)

    # launch the editor
    wait_for_editor(temp_src_path)

    # re-encrypt password database to another temporary file
    _, ext = os.path.splitext(database_path)
    temp_dest_fd, temp_dest_path = tempfile.mkstemp(suffix=ext)
    os.close(temp_dest_fd)
    try:
      gpg_encrypt(recipient=recipient, src_path=temp_src_path, dest_path=temp_dest_path)

      # create backup and move new database over the current database
      backup_path = database_path + '.backup.' + str(time.time())
      os.rename(database_path, backup_path)
      os.rename(temp_dest_path, database_path)
    finally:
      if os.path.exists(temp_dest_path):
        os.remove(temp_dest_path)
  finally:
    os.remove(temp_src_path)
  ctx.exit()


@click.command()
@click.argument('query', metavar='[USER@][KEY]', default='')
@click.option('--copy/--no-copy', default=True, help='copy password to clipboard')
@click.option('--echo/--no-echo', '-E', help='print password to console')
@click.option('--open/--no-open', help='open link in browser')
@click.option('--strict/--no-strict', help='fail unless precisely a single result has been found')
@click.option('--database-path', metavar='PATH', is_eager=True, default=Database.default_path(), help='path to password database')
@click.option('--edit', is_flag=True, expose_value=False, is_eager=True, callback=edit_database, help='launch editor to edit password database')
@click.option('--version', '-v', is_flag=True, expose_value=False, is_eager=True, callback=print_version, help='print version information and exit')
def pw(query, database_path, copy, echo, open, strict):
  """Search for USER and KEY in GPG-encrypted password database."""
  # install silent Ctrl-C handler
  def handle_sigint(*_):
    click.echo()
    sys.exit(1)
  signal.signal(signal.SIGINT, handle_sigint)

  # load database
  db = Database.load(database_path)

  # parse query (split at right-most "@"" sign, since user names are typically email addresses)
  user_pattern, _, key_pattern = query.rpartition('@')

  # search database
  results = db.search(key_pattern, user_pattern)
  results = list(results)
  if strict and len(results) != 1:
    click.echo('error: multiple or no records found (but using --strict mode)', file=sys.stderr)
    sys.exit(1)

  # sort results according to key (stability of sorted() ensures that the order of accounts for any given key remains untouched)
  results = sorted(results, key=lambda e: e.key)

  # print results
  output = ''
  for idx, entry in enumerate(results):
    # key and user
    key = style_match(key_pattern).join(entry.key.split(key_pattern)) if key_pattern else entry.key
    user = style_match(user_pattern).join(entry.user.split(user_pattern)) if user_pattern else entry.user
    output += key
    if user:
      output += ': ' + user

    # password
    if echo:
      output += ' | ' + style_password(entry.password)
    if copy and idx == 0:
      xerox.copy(entry.password)
      output += ' | ' + style_success('*** PASSWORD COPIED TO CLIPBOARD ***')

    # other info
    if entry.link:
      if open and idx == 0:
        import webbrowser
        webbrowser.open(entry.link)
      output += ' | ' + entry.link
    if entry.notes:
      output += ' | ' + entry.notes
    output += '\n'
  click.echo(output.rstrip('\n'))   # echo_via_pager has some unicode problems & can remove the colors


if __name__ == '__main__':
  pw()
