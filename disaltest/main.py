#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Install salt at given version
Get states/pillar
Run test
Generate xml output.
'''

import json
import os
import logging

import subprocess as spr
import shlex

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


SALT_VERSION = os.environ.get('DST_SALT_VERSION', '2014.7.5')


def create_root_dir():
    try:
        os.mkdir('tmp')
    except OSError as e:
        print(e)

create_root_dir()


def run(scmd, venv='', runfunc=spr.call):
    if venv:
        scmd = '{0}/bin/{1}'.format(venv, scmd)
    logger.debug('Running %s  CWD: %s', scmd, os.getcwd())
    cmd = shlex.split(scmd)
    return runfunc(cmd)


def run_output(scmd, venv=''):
    return run(scmd, venv, runfunc=spr.check_output)


VENV = 'dst_env'


def bootstrap_salt():
    run('virtualenv {0}'.format(VENV))
    run('./{0}/bin/pip install salt=={1}'.format(VENV, SALT_VERSION))
    run('salt-call --version', venv=VENV)
    run('salt-call saltutil.sync_all', venv=VENV)


def get_states():
    if not os.path.isdir('states'):
        run('git clone git@github.com:hvnsweeting/states.git')


def get_pillar():
    if not os.path.isdir('pillar'):
        os.mkdir('pillar')
    import shutil
    shutil.copyfile('basepillar.sls', 'pillar/common.sls')

    os.chdir('pillar')

    # run('curl -Lo common.sls https://gist.githubusercontent.com/hvnsweeting/d8143b10e02fff01c434/raw/4f6497b624b43d7590131caa3ccd5660dc1dcaec/common.sls')

    with open('top.sls', 'w') as f:
        f.write('''base:\n  '*':\n    - common''')

    os.chdir('..')


def write_config():
    with open('minion.tpl') as fin, open('minion', 'w') as fout:
        fout.write(fin.read().format(os.path.abspath(os.getcwd())))


def salt_call(saltargs):
    print(os.getcwd())
    out = run_output('salt-call --out=json -c . {0}'.format(saltargs),
                     venv='dst_env')
    result = json.loads(out)['local']
    return result


def evaluate_result(result):
    res = [True, 0]
    for k, v in result.iteritems():
        if v['result'] is False:
            res[1] += 1
    if res[1] != 0:
        res[0] = False
    return res


def main():
    # get_states()
    get_pillar()
    # bootstrap_salt()
    write_config()
    for sls in ('motd', 'vim'):
        print(test_state(sls))


def test_state(slses):
    res = evaluate_result(salt_call('state.sls {0}'.format(slses)))
    logger.info('%s: Failed %d', *res)
    return res[0]


if __name__ == "__main__":
    main()
