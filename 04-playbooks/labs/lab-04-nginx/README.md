# Lab 04 — Déployer nginx et une page d'accueil

⏱️ 1 h · Labo Docker requis. Cibles : `webservers` (web1, web2).

## 🎯 Objectif

Un playbook complet, idempotent, avec handler et vérification.

## Énoncé

Écrivez `nginx.yml` pour le groupe `webservers` :

1. Mise à jour du cache apt (valide 1 h) — `when: ansible_facts['os_family'] == 'Debian'`.
2. Installation de `nginx`.
3. Déploiement de `files/index.html` dans `/var/www/html/index.html` (mode `0644`) ; la page doit être modifiable sans toucher au playbook.
4. Désactivation du site par défaut **non**, mais ajout d'une ligne dans `/etc/nginx/conf.d/server_tokens.conf` : `server_tokens off;` (via `copy` + `content`), qui **notifie** un handler `Recharger nginx` (`state: reloaded`).
5. Service `nginx` `started` + `enabled`.
6. Vérification avec le module `uri` (code 200) depuis le nœud, avec 5 essais espacés de 2 s (`retries`/`delay`/`until`).

## Validation

```bash
ansible-playbook nginx.yml --syntax-check
ansible-playbook nginx.yml --check --diff
ansible-playbook nginx.yml            # changed
ansible-playbook nginx.yml            # changed=0 !
curl -s http://localhost:8081         # depuis votre machine (port mappé web1)
curl -s http://localhost:8082         # web2
```

Modifiez `files/index.html`, relancez : seule la tâche de copie est `changed`, **pas** de redémarrage inutile.

## Pour aller plus loin

* `--list-tasks`, `--tags` : ajoutez des tags `install`, `config`, `verify` et lancez seulement `--tags config`.
* Cassez volontairement `server_tokens.conf` (syntaxe invalide) : que se passe-t-il au reload ? Ajoutez `validate:` ou une tâche `command: nginx -t`.

👉 Corrigé : [solution/nginx.yml](solution/nginx.yml)
