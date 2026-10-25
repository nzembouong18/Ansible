#!/usr/bin/env bash
# Visite guidée des commandes ad-hoc — à lancer depuis le conteneur "control"
set -u
run() { echo; echo "\$ $*"; "$@"; }

run ansible all -m ansible.builtin.ping
run ansible all -m ansible.builtin.command -a "uptime"
run ansible all -m ansible.builtin.shell -a "cat /etc/os-release | grep PRETTY"
run ansible web1 -m ansible.builtin.setup -a "filter=ansible_distribution*"
run ansible all -b -m ansible.builtin.file -a "path=/tmp/adhoc-demo state=directory mode=0755"
run ansible all -b -m ansible.builtin.copy -a "content='hello adhoc' dest=/tmp/adhoc-demo/hello.txt mode=0644"
run ansible all -m ansible.builtin.command -a "cat /tmp/adhoc-demo/hello.txt"
run ansible webservers -b -m ansible.builtin.package -a "name=tree state=present"
run ansible webservers -b -m ansible.builtin.service -a "name=cron state=started enabled=true"
run ansible 'web1,web2' -m ansible.builtin.command -a "sleep 2" -f 1    # séquentiel
run ansible 'web1,web2' -m ansible.builtin.command -a "sleep 2" -f 10   # parallèle
run ansible all -b -m ansible.builtin.file -a "path=/tmp/adhoc-demo state=absent"
