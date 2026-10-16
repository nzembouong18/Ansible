#!/usr/bin/env bash
# Script de mot de passe Vault : il écrit le mot de passe sur stdout.
# En vrai : récupérez-le depuis un gestionnaire de secrets (pass, 1Password CLI, Vault, AWS SSM...).
# Ici (labo) : variable d'environnement.
echo "${ANSIBLE_VAULT_LAB_PASSWORD:?définissez ANSIBLE_VAULT_LAB_PASSWORD}"
