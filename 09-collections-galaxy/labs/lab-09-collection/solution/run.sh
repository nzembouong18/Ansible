#!/usr/bin/env bash
# Corrigé du lab 09 : build -> install -> usage
set -euo pipefail
cd "$(dirname "$0")"
ansible-galaxy collection build collections-src/acme/tools --output-path . --force
ansible-galaxy collection install -r requirements.yml -p ./collections --force
export ANSIBLE_COLLECTIONS_PATH=./collections
ansible-doc -t filter acme.tools.bytes_human | head -5
ansible-playbook -i localhost, -c local use.yml
cat /tmp/banner.txt
