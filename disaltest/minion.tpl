# minion configuration used during tests
master: 127.0.0.1
log_level: debug
root_dir: {workspace}/tmp
mysql.default_file: '/etc/mysql/debian.cnf'
file_client: local
file_roots:
   base:
     - {states_path}
pillar_roots:
  base:
    - {pillar_path}
state_verbose: False
