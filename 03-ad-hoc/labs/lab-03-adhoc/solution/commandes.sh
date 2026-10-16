#!/usr/bin/env bash
# Corrigé du lab 03 — à lancer depuis le conteneur "control"
ansible all -m ping                                                                # 1
ansible all -m setup -a "filter=ansible_distribution*"                             # 2
ansible all -m command -a "df -h /"                                                # 3
ansible webservers -b -m user -a "name=bob shell=/bin/bash groups=sudo append=true"   # 4
ansible webservers -b -m file -a "path=/srv/data state=directory owner=bob mode=0750" # 5
ansible webservers -b -m apt -a "name=nginx state=present update_cache=true"          # 6
ansible webservers -b -m service -a "name=nginx state=started enabled=true"
ansible webservers -m command -a "curl -s /dev/null -w %{http_code} http://localhost"
ansible all -m fetch -a "src=/etc/hostname dest=./collected/"                         # 7
ansible db1 -m shell -a "ps aux --sort=-%mem | head -n 2"                             # 8
ansible webservers -b -m user -a "name=bob state=absent remove=true"                  # 9
ansible webservers -b -m file -a "path=/srv/data state=absent"
# Bonus : 2e exécution de l'étape 4 => SUCCESS (changed=false) : le module user est idempotent.
