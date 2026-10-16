#!/usr/bin/env bash
# Visite guidée — à lancer depuis 13-inventaires-dynamiques/demos
set -e
echo "== 1. Script dynamique";            ansible-inventory -i inventory-script.py --graph
echo "== 2. Variables d'un hôte";         ansible-inventory -i inventory-script.py --host web-01
echo "== 3. Plugin constructed (hosts.yml + constructed.yml)"
ansible-inventory -i constructed/hosts.yml -i constructed/constructed.yml --graph --vars | head -40
echo "== 4. Plugin generator";            ansible-inventory -i generator/generator.yml --graph | head -25
echo "== 5. Ciblage par pattern sur l'inventaire dynamique"
ansible -i inventory-script.py 'role_web:&env_prod' --list-hosts
