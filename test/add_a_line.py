#!/usr/bin/env python
import sys

assert len(sys.argv) == 3
open(sys.argv[2], 'w').write(sys.argv[1] + '\n')
