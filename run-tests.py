#!/usr/bin/env python3

"""Run the tests with https://pytest.org."""

from __future__ import print_function

import os
import platform
import sys

import pytest

ARGS = [#'--skip-exe',
        #'--only-exe',
        #'--collect-only',
        #'--verbose',
        #'--pdb',
        #'--exitfirst',  # a.k.a. -x
        #'-W', 'error',
       ]

if platform.system() == 'Windows':
    if 'idlelib' in sys.modules:
        ARGS += ['--capture=sys', '--color=no']
    elif sys.version_info.major == 2 and 'win_unicode_console' in sys.modules:
        ARGS.append('--capture=sys')

print('run', [os.path.basename(__file__)] + sys.argv[1:])
args = ARGS + sys.argv[1:]

print('pytest.main({!r})'.format(args))
sys.exit(pytest.main(args))
