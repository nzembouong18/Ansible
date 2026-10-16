# Lab 10 — Secrets multi-environnements avec `--vault-id`

⏱️ 1 h · 100 % local.

## 🎯 Objectif

Un même playbook déploie une configuration applicative dans deux environnements (`dev`, `prod`) dont les secrets sont chiffrés avec **deux mots de passe différents**.

## Énoncé

1. Créez deux fichiers de mot de passe de labo : `.vault_dev` (`dev-lab-pass`) et `.vault_prod` (`prod-lab-pass`).
2. Arborescence :
   ```
   inventory/hosts.yml                  # groupes dev (app-dev) et prod (app-prod), connexion locale
   inventory/group_vars/dev/{vars.yml,vault.yml}
   inventory/group_vars/prod/{vars.yml,vault.yml}
   deploy.yml
   ```
3. `vars.yml` : `db_password: "{{ vault_db_password }}"`, `app_env: dev|prod`. `vault.yml` : `vault_db_password` (chiffré avec **l'ID correspondant**).
4. `deploy.yml` écrit `/tmp/lab10-<env>.conf` (mode `0600`, `no_log`) contenant `env` et `db_password`.
5. Exécutez avec les deux IDs, puis uniquement avec `dev` : que se passe-t-il pour le groupe `prod` ?
6. Faites une **rotation** : `ansible-vault rekey --vault-id prod@.vault_prod --new-vault-id prod@.vault_prod_new`.

## Validation

```bash
ansible-playbook -i inventory deploy.yml --vault-id dev@.vault_dev --vault-id prod@.vault_prod
cat /tmp/lab10-dev.conf /tmp/lab10-prod.conf
ansible-playbook -i inventory deploy.yml --vault-id dev@.vault_dev --limit dev      # OK sans mot de passe prod
ansible-playbook -i inventory deploy.yml --vault-id dev@.vault_dev                  # ÉCHEC attendu sur prod
head -1 inventory/group_vars/prod/vault.yml          # $ANSIBLE_VAULT;1.2;AES256;prod
```

👉 Corrigé : [solution/](solution/) (mots de passe de labo inclus : `.vault_dev`, `.vault_prod`)
