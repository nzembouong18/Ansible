#!/usr/bin/env bash
# Vérifications automatiques de la formation (aucun Docker requis) :
#   ./tests/run-checks.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT=$PWD
PASS=0; FAIL=0
ok()   { echo "  ✔ $1"; PASS=$((PASS+1)); }
ko()   { echo "  ✘ $1"; FAIL=$((FAIL+1)); }
run()  { local name=$1; shift; if "$@" >/tmp/check.log 2>&1; then ok "$name"; else ko "$name"; tail -5 /tmp/check.log; fi; }
LOCAL="-i $ROOT/tests/inventory-local.ini"

echo "== Lint"
run "ansible-lint (profil production)" ansible-lint

echo "== Modules 01-06 : démos exécutables en local"
for f in 01-fondamentaux/demos/01-premier-playbook.yml 04-playbooks/demos/01-multi-play.yml \
         04-playbooks/demos/02-handlers.yml 05-variables-facts/demos/01-types.yml \
         06-controle-flux/demos/03-block-rescue.yml 07-templates-jinja2/demos/02-template.yml; do
  run "$f" ansible-playbook $LOCAL "$f"
done

echo "== Module 02 : inventaires"
run "inventaire 3-tiers (web1,web2,web3 en prod)" bash -c \
  "ansible -i 02-inventaires/labs/lab-02-inventaire-3tiers/solution 'webservers:&prod' --list-hosts | grep -q web3"

echo "== Module 13 : inventaire CSV"
run "inventory_csv.py + constructed" bash -c \
  "ansible-inventory -i 13-inventaires-dynamiques/labs/lab-13-inventaire-csv/solution/inventory_csv.py \
   -i 13-inventaires-dynamiques/labs/lab-13-inventaire-csv/solution/constructed.yml --graph | grep -q big_servers"

echo "== Module 17 : rendu et validation de manifests Kubernetes"
run "render.yml dev" bash -c "cd 17-windows-reseau-cloud-conteneurs/labs/lab-17-docker-k8s/solution && ansible-playbook -i localhost, render.yml -e env=dev"
run "render.yml prod (ingress inclus)" bash -c "cd 17-windows-reseau-cloud-conteneurs/labs/lab-17-docker-k8s/solution && ansible-playbook -i localhost, render.yml -e env=prod && test -f out/prod/ingress.yml"
run "refus de l'image :latest" bash -c "cd 17-windows-reseau-cloud-conteneurs/labs/lab-17-docker-k8s/solution && ! ansible-playbook -i localhost, render.yml -e env=prod -e image=nginx:latest"

echo "== Module 20 : projet final (environnement local)"
run "site.yml (local)" bash -c "cd 20-projet-final && ansible-playbook -i inventories/local/hosts.yml playbooks/site.yml --vault-password-file .vault_pass_lab"
run "site.yml idempotent" bash -c "cd 20-projet-final && ansible-playbook -i inventories/local/hosts.yml playbooks/site.yml --vault-password-file .vault_pass_lab | grep -E '^web1' | grep -q 'changed=0'"
run "molecule webapp" bash -c "cd 20-projet-final/roles/webapp && molecule test"

echo "== Module 14 : tests unitaires du module config_kv"
run "pytest config_kv" python3 -m pytest -q 14-developpement/labs/lab-14-module-kv/solution/tests

echo "== Module 15 : Molecule (scénario local)"
run "molecule test (rôle motd)" bash -c "cd 15-tests-qualite/labs/lab-15-molecule/solution/roles/motd && molecule test"

echo
echo "Résultat : $PASS réussi(s), $FAIL échec(s)"
[ "$FAIL" -eq 0 ]
