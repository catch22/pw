import sys

# this script is a faux PW_EDITOR, which simply appends the string argv[1] to
# the file argv[2]. it is called from test_cli.py:test_with_changes().
assert len(sys.argv) == 3
with open(sys.argv[2], 'a') as fp:
    fp.write('\n%s\n' % sys.argv[1])
