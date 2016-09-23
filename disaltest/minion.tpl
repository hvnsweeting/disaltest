# minion configuration used during tests
master: 127.0.0.1
log_level: debug
root_dir: {0}/tmp
mysql.default_file: '/etc/mysql/debian.cnf'
file_client: local
file_roots:
   base:
     - {0}/states
pillar_roots:
  base:
    - {0}/pillar
state_verbose: False
