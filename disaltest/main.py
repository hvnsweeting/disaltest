#!/usr/bin/env python
# -*- coding: utf-8 -*-

unittest_tpl = '''
import cliengine
import unittest

try:
    import xmlrunner
except ImportError:
    xmlrunner = None

class SaltSLSTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cliengine.write_config()
        cliengine.get_states()
        cliengine.get_pillar()
        cliengine.bootstrap_salt()
'''

TESTS_FILENAME = 'test_salt_states.py'

test_main = '''
if __name__ == "__main__":
    if xmlrunner is not None:
        unittest.main(testRunner=xmlrunner.XMLTestRunner(
            output='.', outsuffix='salt'))
    else:
        unittest.main()
'''


def tests_generate():
    content = unittest_tpl
    for test in ('motd', 'vim'):
        func = '''    def test_sls_{0}(self):
        res = cliengine.salt_call_short_result('state.sls {0}')
        self.assertEqual(res.success, True, 'states failed: %d' % res.false_count)\n'''.format(test)
        content += func
    content += test_main

    with open(TESTS_FILENAME, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    tests_generate()
    import subprocess as spr
    spr.check_output(['python', TESTS_FILENAME])
