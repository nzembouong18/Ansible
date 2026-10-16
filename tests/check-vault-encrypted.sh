#!/usr/bin/env bash
# Échoue si un fichier passé en argument n'est pas chiffré par ansible-vault.
status=0
for f in "$@"; do
  if ! head -1 "$f" | grep -q '^\$ANSIBLE_VAULT'; then
    echo "NON CHIFFRÉ : $f"
    status=1
  fi
done
exit $status
