#!/usr/bin/env bash
# Visite guidée des outils de qualité (lancer depuis 15-tests-qualite/demos)
cd "$(dirname "$0")"
echo "== yamllint";            yamllint -d "{extends: default, rules: {line-length: disable}}" mauvais.yml | head -8
echo "== ansible-lint (mauvais)"; ansible-lint --profile production mauvais.yml 2>&1 | grep -E "^[a-z\-]+(\[|:)" | sort | uniq -c | sort -rn | head -12
echo "== ansible-lint (corrigé)"; ansible-lint --profile production corrige.yml 2>&1 | tail -2
echo "== syntax-check";        ansible-playbook -i localhost, corrige.yml --syntax-check
echo "== liste des règles";   ansible-lint -L | head -12
