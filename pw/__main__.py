#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
from functools import partial
import os, os.path, random, signal, string
import click
from . import __version__, Store, _gpg

style_match = partial(click.style, fg='yellow', bold=True)
style_error = style_password = partial(click.style, fg='red', bold=True)
style_success = partial(click.style, fg='green', bold=True, reverse=True)


class Mode(object):
    COPY = 'Mode.COPY'
    ECHO = 'Mode.ECHO'
    RAW = 'Mode.RAW'


def default_path():
    return os.environ.get('PW_PATH') or click.get_app_dir('passwords.pw')


@click.command()
@click.argument('key_pattern', metavar='[USER@][KEY]', default='')
@click.argument('user_pattern', metavar='[USER]', default='')
@click.option('--copy',
              '-C',
              'mode',
              flag_value=Mode.COPY,
              default=True,
              help='copy password to clipboard (default)')
@click.option('--echo',
              '-E',
              'mode',
              flag_value=Mode.ECHO,
              help='print password to console')
@click.option('--raw',
              '-R',
              'mode',
              flag_value=Mode.RAW,
              help='output password only')
@click.option('--strict',
              '-S',
              'strict_flag',
              is_flag=True,
              help='fail unless precisely a single result has been found')
@click.option('--user',
              '-U',
              'user_flag',
              is_flag=True,
              help="copy or display username instead of password")
@click.option('--file',
              '-f',
              metavar='PATH',
              default=default_path(),
              help='password file')
@click.option('--edit',
              'edit_subcommand',
              is_flag=True,
              help='launch editor to edit password database')
@click.option('--gen',
              'gen_subcommand',
              is_flag=True,
              help='generate a random password')
@click.version_option(version=__version__,
                      message='%(prog)s version %(version)s')
@click.pass_context
def pw(ctx, key_pattern, user_pattern, mode, strict_flag, user_flag, file,
       edit_subcommand, gen_subcommand):
    """Search for USER and KEY in GPG-encrypted password file."""

    # install silent Ctrl-C handler
    def handle_sigint(*_):
        click.echo()
        ctx.exit(1)

    signal.signal(signal.SIGINT, handle_sigint)

    # invoke a subcommand?
    if gen_subcommand:
        length = int(key_pattern) if key_pattern else None
        generate_password(mode, length)
        return
    elif edit_subcommand:
        launch_editor(ctx, file)
        return

    # verify that database file is present
    if not os.path.exists(file):
        click.echo("error: password store not found at '%s'" % file, err=True)
        ctx.exit(1)

    # load database
    store = Store.load(file)

    # if no user query provided, split key query according to right-most "@" sign (since usernames are typically email addresses)
    if not user_pattern:
        user_pattern, _, key_pattern = key_pattern.rpartition('@')

    # search database
    results = store.search(key_pattern, user_pattern)
    results = list(results)

    # if strict flag is enabled, check that precisely a single record was found
    if strict_flag and len(results) != 1:
        click.echo(
            'error: multiple or no records found (but using --strict flag)',
            err=True)
        ctx.exit(2)

    # raw mode?
    if mode == Mode.RAW:
        for entry in results:
            click.echo(entry.user if user_flag else entry.password)
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
        if mode == Mode.ECHO and not user_flag:
            output += ' | ' + style_password(entry.password)
        elif mode == Mode.COPY and idx == 0:
            try:
                import pyperclip
                pyperclip.copy(entry.user if user_flag else entry.password)
                result = style_success('*** %s COPIED TO CLIPBOARD ***' % (
                    "USERNAME" if user_flag else "PASSWORD"))
            except ImportError:
                result = style_error(
                    '*** PYTHON PACKAGE "PYPERCLIP" NOT FOUND ***')
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
    click.echo(output.rstrip())


def launch_editor(ctx, file):
    """launch editor with decrypted password database"""
    # do not use EDITOR environment variable (rather force user to make a concious choice)
    editor = os.environ.get('PW_EDITOR')
    if not editor:
        click.echo('error: no editor set in PW_EDITOR environment variables')
        ctx.exit(1)

    # verify that database file is present
    if not os.path.exists(file):
        click.echo("error: password store not found at '%s'" % file, err=True)
        ctx.exit(1)

    # load source (decrypting if necessary)
    is_encrypted = _gpg.is_encrypted(file)
    if is_encrypted:
        original = _gpg.decrypt(file)
    else:
        original = open(file, 'rb').read()

    # if encrypted, determine recipient
    if is_encrypted:
        recipient = os.environ.get('PW_GPG_RECIPIENT')
        if not recipient:
            click.echo(
                'error: no recipient set in PW_GPG_RECIPIENT environment variables')
            ctx.exit(1)

    # launch the editor
    modified = click.edit(original.decode('utf-8'),
                          editor=editor,
                          require_save=True,
                          extension='.yaml')
    if modified is None:
        click.echo("not modified")
        return
    modified = modified.encode('utf-8')

    # not encrypted? simply overwrite file
    if not is_encrypted:
        open(file, 'wb').write(modified)
        return

    # otherwise, the process is somewhat more complicated
    _gpg.encrypt(recipient=recipient, dest_path=file, content=modified)


def generate_password(mode, length):
    """generate a random password"""
    RANDOM_ALPHABET = string.ascii_letters + string.digits
    DEFAULT_LENGTH = 32

    # generate random password
    r = random.SystemRandom()
    length = length or DEFAULT_LENGTH
    password = ''.join(r.choice(RANDOM_ALPHABET) for _ in range(length))

    # copy or echo generated password
    if mode == Mode.ECHO:
        click.echo(style_password(password))
    elif mode == Mode.COPY:
        try:
            import pyperclip
            pyperclip.copy(password)
            result = style_success('*** PASSWORD COPIED TO CLIPBOARD ***')
        except ImportError:
            result = style_error(
                '*** PYTHON PACKAGE "PYPERCLIP" NOT FOUND ***')
        click.echo(result)
    elif mode == Mode.RAW:
        click.echo(password)


if __name__ == '__main__':
    pw(prog_name='pw')
