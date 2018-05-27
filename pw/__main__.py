#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
from functools import partial
import os, os.path, random, signal, string, sys
import click
from . import __version__, Store, _gpg


class Mode(object):
    COPY = "Mode.COPY"
    ECHO = "Mode.ECHO"
    RAW = "Mode.RAW"


def default_path():
    return os.environ.get("PW_PATH") or click.get_app_dir("passwords.pw.asc")


style_match = partial(click.style, fg="yellow", bold=True)
style_error = style_password = partial(click.style, fg="red", bold=True)
style_success = partial(click.style, fg="green", bold=True, reverse=True)


def highlight_match(pattern, str):
    return style_match(pattern).join(str.split(pattern)) if pattern else str


RANDOM_PASSWORD_DEFAULT_LENGTH = 32
RANDOM_PASSWORD_ALPHABET = string.ascii_letters + string.digits


@click.command()
@click.argument("key_pattern", metavar="[USER@][KEY]", default="")
@click.argument("user_pattern", metavar="[USER]", default="")
@click.option(
    "--copy",
    "-C",
    "mode",
    flag_value=Mode.COPY,
    default=True,
    help="Display account information, but copy password to clipboard (default mode).",
)
@click.option(
    "--echo",
    "-E",
    "mode",
    flag_value=Mode.ECHO,
    help="Display account information as well as password in plaintext (alternative mode).",
)
@click.option(
    "--raw",
    "-R",
    "mode",
    flag_value=Mode.RAW,
    help="Only display password in plaintext (alternative mode).",
)
@click.option(
    "--strict",
    "-S",
    "strict_flag",
    is_flag=True,
    help="Fail unless precisely a single result has been found.",
)
@click.option(
    "--user",
    "-U",
    "user_flag",
    is_flag=True,
    help="Copy or display username instead of password.",
)
@click.option(
    "--file",
    "-f",
    metavar="PATH",
    default=default_path(),
    help="Path to password file.",
)
@click.option(
    "--edit",
    "edit_subcommand",
    is_flag=True,
    help="Launch editor to edit password database and exit.",
)
@click.option(
    "--gen", "gen_subcommand", is_flag=True, help="Generate a random password and exit."
)
@click.version_option(
    version=__version__, message="pw version %(version)s\npython " + sys.version
)
@click.pass_context
def pw(
    ctx,
    key_pattern,
    user_pattern,
    mode,
    strict_flag,
    user_flag,
    file,
    edit_subcommand,
    gen_subcommand,
):
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
        user_pattern, _, key_pattern = key_pattern.rpartition("@")

    # search database
    results = store.search(key_pattern, user_pattern)
    results = list(results)

    # if strict flag is enabled, check that precisely a single record was found
    if strict_flag and len(results) != 1:
        click.echo(
            "error: multiple or no records found (but using --strict flag)", err=True
        )
        ctx.exit(2)

    # raw mode?
    if mode == Mode.RAW:
        for entry in results:
            click.echo(entry.user if user_flag else entry.password)
        return

    # print results
    for idx, entry in enumerate(results):
        # start with key and user
        line = highlight_match(key_pattern, entry.key)
        if entry.user:
            line += ": " + highlight_match(user_pattern, entry.user)

        # add password or copy&paste sucess message
        if mode == Mode.ECHO and not user_flag:
            line += " | " + style_password(entry.password)
        elif mode == Mode.COPY and idx == 0:
            try:
                import pyperclip

                pyperclip.copy(entry.user if user_flag else entry.password)
                result = style_success(
                    "*** %s COPIED TO CLIPBOARD ***"
                    % ("USERNAME" if user_flag else "PASSWORD")
                )
            except ImportError:
                result = style_error('*** PYTHON PACKAGE "PYPERCLIP" NOT FOUND ***')
            line += " | " + result

        # add notes
        if entry.notes:
            if idx == 0:
                line += "\n"
                line += "\n".join("   " + line for line in entry.notes.splitlines())
            else:
                lines = entry.notes.splitlines()
                line += " | " + lines[0]
                if len(lines) > 1:
                    line += " (...)"
        click.echo(line)


def launch_editor(ctx, file):
    """launch editor with decrypted password database"""
    # do not use EDITOR environment variable (rather force user to make a concious choice)
    editor = os.environ.get("PW_EDITOR")
    if not editor:
        click.echo("error: no editor set in PW_EDITOR environment variables")
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
        original = open(file, "rb").read()

    # if encrypted, determine recipient
    if is_encrypted:
        recipient = os.environ.get("PW_GPG_RECIPIENT")
        if not recipient:
            click.echo(
                "error: no recipient set in PW_GPG_RECIPIENT environment variables"
            )
            ctx.exit(1)

    # launch the editor
    ext = _gpg.unencrypted_ext(file)
    modified = click.edit(
        original.decode("utf-8"), editor=editor, require_save=True, extension=ext
    )
    if modified is None:
        click.echo("not modified")
        return
    modified = modified.encode("utf-8")

    # not encrypted? simply overwrite file
    if not is_encrypted:
        with open(file, "wb") as fp:
            fp.write(modified)
        return

    # otherwise, the process is somewhat more complicated
    _gpg.encrypt(recipient=recipient, dest_path=file, content=modified)


def generate_password(mode, length):
    """generate a random password"""
    # generate random password
    r = random.SystemRandom()
    length = length or RANDOM_PASSWORD_DEFAULT_LENGTH
    password = "".join(r.choice(RANDOM_PASSWORD_ALPHABET) for _ in range(length))

    # copy or echo generated password
    if mode == Mode.ECHO:
        click.echo(style_password(password))
    elif mode == Mode.COPY:
        try:
            import pyperclip

            pyperclip.copy(password)
            result = style_success("*** PASSWORD COPIED TO CLIPBOARD ***")
        except ImportError:
            result = style_error('*** PYTHON PACKAGE "PYPERCLIP" NOT FOUND ***')
        click.echo(result)
    elif mode == Mode.RAW:
        click.echo(password)


if __name__ == "__main__":
    pw(prog_name="pw")
