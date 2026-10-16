#!/bin/bash
set -e
mkdir -p ~/.ssh && chmod 700 ~/.ssh
if [ -f /keys/id_ed25519 ]; then
  install -m 600 /keys/id_ed25519 ~/.ssh/id_ed25519
  install -m 644 /keys/id_ed25519.pub ~/.ssh/id_ed25519.pub
fi
printf 'Host *\n  StrictHostKeyChecking accept-new\n  UserKnownHostsFile ~/.ssh/known_hosts\n' > ~/.ssh/config
chmod 600 ~/.ssh/config
exec "$@"
