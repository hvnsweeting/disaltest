#!/usr/bin/env python
# -*- coding: utf-8 -*-

unittest_tpl = '''
import cliengine
import unittest

class SaltSLSTest(unittest.TestCase):
'''

TESTS_FILENAME = 'test_salt_states.py'

test_main = '''
if __name__ == "__main__":
    unittest.main()
'''


def tests_generate():
    content = unittest_tpl
    for test in ('motd', 'vim'):
        func = '''    def test_sls_{0}(self):
        self.assertTrue(cliengine.test_state('{0}'))\n'''.format(test)
        content += func
    content += test_main

    with open(TESTS_FILENAME, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    tests_generate()
    import subprocess as spr
    spr.check_output(['python', TESTS_FILENAME])
