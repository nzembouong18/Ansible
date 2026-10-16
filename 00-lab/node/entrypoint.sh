#!/bin/bash
# Installe la clé publique du labo pour l'utilisateur "ansible" puis passe la main à systemd.
set -e
if [ -f /keys/id_ed25519.pub ]; then
  install -d -m 700 -o ansible -g ansible /home/ansible/.ssh
  install -m 600 -o ansible -g ansible /keys/id_ed25519.pub /home/ansible/.ssh/authorized_keys
fi
exec "$@"
