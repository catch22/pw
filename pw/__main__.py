#!/usr/bin/env python
from functools import partial
import os, os.path, pipes, signal, subprocess, sys, tempfile, time
import click
from . import __version__, Store, _gpg

style_match = partial(click.style, fg='yellow', bold=True)
style_error = style_password = partial(click.style, fg='red', bold=True)
style_success = partial(click.style, fg='green', bold=True, reverse=True)


def default_path():
    return os.environ.get('PW_PATH') or click.get_app_dir('passwords.pw')


def print_version(ctx, param, value):
    """print version information and exit"""
    if not value or ctx.resilient_parsing:
        return
    click.echo('pw version %s' % __version__)
    ctx.exit()


def edit_database(ctx, param, value):
    """edit password database and exit"""
    if not value or ctx.resilient_parsing:
        return

    # do not use EDITOR environment variable (rather force user to make a concious choice)
    editor = os.environ.get('PW_EDITOR')
    if not editor:
        click.echo('error: no editor set in PW_EDITOR environment variables')
        sys.exit(1)

    # verify that database file is present
    file = ctx.params.get('file', default_path())
    if not os.path.exists(file):
        click.echo("error: password store not found at '%s'" % file,
                   file=sys.stderr)
        sys.exit(1)

    # load database
    original = Store._load_source(file)
    is_encrypted = _gpg.is_encrypted(file)

    # if encrypted, determine recipient
    if is_encrypted:
        recipient = os.environ.get('PW_GPG_RECIPIENT')
        if not recipient:
            click.echo(
                'error: no recipient set in PW_GPG_RECIPIENT environment variables')
            sys.exit(1)

    # launch the editor
    modified = click.edit(original.decode('utf-8'),
                          editor=editor,
                          require_save=True,
                          extension='.yaml')
    if modified is None:
        click.echo("not modified")
        sys.exit(0)
    modified = modified.encode('utf-8')

    # not encrypted? simply overwrite file
    if not is_encrypted:
        open(file, 'wb').write(modified)
        sys.exit(0)

    # otherwise, the process is somewhat more complicated
    _gpg.encrypt(recipient=recipient, dest_path=file, content=modified)
    sys.exit(0)


@click.command()
@click.argument('key_pattern', metavar='[USER@][KEY]', default='')
@click.argument('user_pattern', metavar='[USER]', default='')
@click.option('--copy/--no-copy',
              default=True,
              help='copy password to clipboard (default)')
@click.option('--echo/--no-echo', '-E', help='print password to console')
@click.option('--strict/--no-strict', '-S',
              help='fail unless precisely a single result has been found')
@click.option('--raw/--no-raw', help='output password only')
@click.option('--file', '-f',
              metavar='PATH',
              is_eager=True,
              default=default_path(),
              help='password file')
@click.option('--edit',
              is_flag=True,
              expose_value=False,
              is_eager=True,
              callback=edit_database,
              help='launch editor to edit password database')
@click.option('--version', '-v',
              is_flag=True,
              expose_value=False,
              is_eager=True,
              callback=print_version,
              help='print version information and exit')
def pw(key_pattern, user_pattern, file, copy, echo, strict, raw):
    """Search for USER and KEY in GPG-encrypted password file."""

    # install silent Ctrl-C handler
    def handle_sigint(*_):
        click.echo()
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_sigint)

    # verify that database file is present
    if not os.path.exists(file):
        click.echo("error: password store not found at '%s'" % file,
                   file=sys.stderr)
        sys.exit(1)

    # load database
    store = Store.load(file)

    # if no user query provided, split key query according to right-most "@" sign (since usernames are typically email addresses)
    if not user_pattern:
        user_pattern, _, key_pattern = key_pattern.rpartition('@')

    # search database
    results = store.search(key_pattern, user_pattern)
    results = list(results)
    if strict and len(results) != 1:
        click.echo(
            'error: multiple or no records found (but using --strict mode)',
            file=sys.stderr)
        sys.exit(2)

    # sort results according to key (stability of sorted() ensures that the order of accounts for any given key remains untouched)
    results = sorted(results, key=lambda e: e.key)

    # raw mode?
    if raw:
        for entry in results:
            click.echo(entry.password)
        return

    # print results
    output = ''
    for idx, entry in enumerate(results):
        # key and user
        key = style_match(key_pattern).join(
            entry.key.split(key_pattern)) if key_pattern else entry.key
        user = style_match(user_pattern).join(
            entry.user.split(user_pattern)) if user_pattern else entry.user
        output += key
        if user:
            output += ': ' + user

        # password
        if echo:
            output += ' | ' + style_password(entry.password)
        if copy and idx == 0:
            try:
                import xerox
                xerox.copy(entry.password)
                result = style_success('*** PASSWORD COPIED TO CLIPBOARD ***')
            except ImportError:
                result = style_error('*** PYTHON XEROX PACKAGE NOT FOUND ***')
            output += ' | ' + result

        # other info
        if entry.notes:
            if idx == 0:
                output += '\n'
                output += "\n".join("   " + line
                                    for line in entry.notes.splitlines())
            else:
                lines = entry.notes.splitlines()
                output += ' | ' + lines[0]
                if len(lines) > 1:
                    output += " (...)"
        output += '\n'
    click.echo_via_pager(output.rstrip())


if __name__ == '__main__':
    pw()
