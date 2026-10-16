# Lab 11 — Pile 2-tiers : nginx + PostgreSQL

⏱️ 1 h 30 · Labo Docker : `web1`, `web2` (nginx), `db1` (PostgreSQL).

## 🎯 Objectif

Déployer une mini-pile et **prouver** la connectivité web → base depuis les serveurs web.

## Énoncé

Écrivez `stack.yml` avec **trois plays dans cet ordre** :

1. **`dbservers`** :
   * installer `postgresql` et `python3-psycopg2` ;
   * écouter sur toutes les interfaces (`listen_addresses = '*'`, module `community.postgresql.postgresql_alter_system`, `become_user: postgres`) ;
   * créer la base `shop` et l'utilisateur `shop_app` (mot de passe issu d'une variable `vault_shop_password` — pour le labo, mettez-la dans `group_vars/dbservers.yml` **chiffrée** avec Vault, voir module 10 ; `no_log: true`) ;
   * autoriser le sous-réseau Docker du labo dans `pg_hba.conf` (module `postgresql_pg_hba`, méthode `scram-sha-256`) ;
   * redémarrer PostgreSQL via un **handler**.
2. **`webservers`** : installer `nginx` et `postgresql-client` ; calculer l'IP de `db1` via `hostvars` (⚠️ les facts de `db1` doivent avoir été collectés : jouez d'abord `setup` sur `dbservers`, c'est le cas ici grâce au play n°1) ; déposer `/etc/app/db.env` (mode `0640`) avec `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
3. **`webservers`** (vérification) : exécuter `psql` avec `PGPASSWORD` en `environment:` (+ `no_log`) pour faire `SELECT 1;`, `changed_when: false`, `retries/until` ; échouer clairement sinon.

## Validation

```bash
ansible-playbook stack.yml --ask-vault-pass        # ou --vault-password-file
ansible-playbook stack.yml --vault-password-file .vault_pass       # 2e passage : changed=0 (hors tâche de vérification)
ansible webservers -b -m command -a "cat /etc/app/db.env"          # mot de passe présent, droits 0640
```

**Pièges attendus** : l'ordre des plays ; `become_user: postgres` nécessite `acl` (`apt install acl`) sur Debian pour le passage d'identité non-root → ajoutez le paquet `acl` ; le redémarrage doit avoir lieu **avant** le test de connexion (`meta: flush_handlers`).

👉 Corrigé : [solution/](solution/) (mot de passe Vault du labo : `.vault_pass`)
