#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import cliengine
unittest_tpl = '''
import cliengine
import unittest

try:
    import xmlrunner
except ImportError:
    xmlrunner = None

class SaltSLSTest(unittest.TestCase):
'''

SALT_VERSION = os.environ.get('DST_SALT_VERSION', '2014.7.5')


TESTS_FILENAME = 'test_salt_states.py'

test_main = '''
if __name__ == "__main__":
    if xmlrunner is not None:
        unittest.main(testRunner=xmlrunner.XMLTestRunner(
            output='.', outsuffix='salt'))
    else:
        unittest.main()
'''


def tests_generate(slses):
    if slses is None:
        slses = ['motd', ]
    content = unittest_tpl
    for test in slses:
        func = '''    def test_sls_{0}(self):
        res = cliengine.salt_call_short_result('state.sls {0}')
        self.assertEqual(res.success, True, 'states failed: %d' % res.false_count)\n'''.format(test)
        content += func
    content += test_main

    with open(TESTS_FILENAME, 'w') as f:
        f.write(content)


def prepare_salt(states_dir, pillar_dir, salt_version=SALT_VERSION):
    # cliengine.get_states()
    cliengine.get_pillar()

    cliengine.write_config(states_dir, pillar_dir)
    cliengine.bootstrap_salt(salt_version)


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('slses', default='motd', nargs='+')
    argp.add_argument('--states', default='states')
    argp.add_argument('--pillar', default='pillar')
    args = argp.parse_args()
    prepare_salt(args.states, args.pillar)
    tests_generate(args.slses)
    import subprocess as spr
    spr.check_output(['python', TESTS_FILENAME])

if __name__ == "__main__":
    main()
