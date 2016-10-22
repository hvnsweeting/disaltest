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
import shlex
import shutil
import subprocess as spr

from collections import namedtuple

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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


def bootstrap_salt(salt_version):
    run('virtualenv {0}'.format(VENV))
    run('./{0}/bin/pip install salt=={1}'.format(VENV, salt_version))
    run('salt-call --version', venv=VENV)
    run('salt-call -c . saltutil.sync_all', venv=VENV)


def get_states():
    if not os.path.isdir('states'):
        run('git clone https://github.com/hvnsweeting/states.git')


def get_pillar(pillarfile='basepillar.sls'):
    # if we got a dir, use it
    if os.path.isdir(pillarfile):
        shutil.copytree(pillarfile, 'pillar')
        return

    if not os.path.isdir('pillar'):
        os.mkdir('pillar')
    import shutil
    shutil.copyfile(pillarfile, 'pillar/common.sls')

    os.chdir('pillar')

    # run('curl -Lo common.sls https://gist.githubusercontent.com/hvnsweeting/d8143b10e02fff01c434/raw/4f6497b624b43d7590131caa3ccd5660dc1dcaec/common.sls')

    with open('top.sls', 'w') as f:
        f.write('''base:\n  '*':\n    - common''')

    os.chdir('..')


def write_config(states_path, pillar_path):
    if os.path.isfile(pillar_path):
        pillar_path = os.path.dirname(pillar_path)

    with open('minion.tpl') as fin, open('minion', 'w') as fout:
        minion_conf = fin.read()
        minion_conf = minion_conf.format(
            workspace=os.getcwd(),
            states_path=states_path,
            pillar_path=pillar_path,
        )
        logger.debug("Minion config content: %s", minion_conf)
        fout.write(minion_conf)


def salt_call(saltargs, res_processor=None):
    print(os.getcwd())
    out = run_output('salt-call --out=json -c . {0}'.format(saltargs),
                     venv='dst_env')
    result = json.loads(out)['local']
    if res_processor:
        return res_processor(result)
    return result


def salt_call_short_result(saltargs):
    return salt_call(saltargs, res_processor=shortern)


def shortern(result):
    if not isinstance(result, dict):
        logger.warning(
            'Expected dict, got %s, seems state/pillar failed to render: %s',
            type(result),
            result
        )

    Result = namedtuple('Result', ['success', 'false_count'])
    success = False
    false_count = 0
    for state_id, state_data in result.iteritems():
        if state_data['result'] is False:
            false_count += 1
    if false_count == 0:
        success = True
    return Result(success, false_count)


def main():
    get_states()
    get_pillar()
    bootstrap_salt()
    write_config()
    for sls in ('motd', 'vim'):
        print(test_state(sls))


def test_state(slses):
    res = shortern(salt_call('state.sls {0}'.format(slses)))
    logger.info('%s: Failed %d', *res)
    return res.success


if __name__ == "__main__":
    main()
