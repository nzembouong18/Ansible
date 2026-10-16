#!/usr/bin/env bash
# Pilotage du labo Ansible.  ./lab.sh {up|down|reset|shell|status|rocky}
set -euo pipefail
cd "$(dirname "$0")"
DC="docker compose"

gen_keys() {
  if [ ! -f keys/id_ed25519 ]; then
    ssh-keygen -t ed25519 -N '' -C 'ansible-lab' -f keys/id_ed25519 >/dev/null
    echo "[+] Clé SSH du labo générée dans 00-lab/keys/ (ne JAMAIS la réutiliser en production)"
  fi
}

case "${1:-help}" in
  up)     gen_keys; $DC up -d --build; $DC ps ;;
  rocky)  gen_keys; $DC --profile rocky up -d --build rocky1 ;;
  down)   $DC --profile rocky down ;;
  reset)  $DC --profile rocky down -v; $DC up -d --build ;;
  shell)  exec docker exec -it control bash ;;
  status) $DC --profile rocky ps ;;
  *)      echo "Usage: $0 {up|rocky|down|reset|shell|status}" ;;
esac
