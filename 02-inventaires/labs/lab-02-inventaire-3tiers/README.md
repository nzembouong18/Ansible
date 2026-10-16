# Lab 02 — Inventaire d'une application 3-tiers

⏱️ 45 min · Fonctionne sans le labo Docker (inventaire statique + `ansible-inventory`).

## 🎯 Objectif

Modéliser l'infrastructure suivante dans un inventaire YAML propre avec `group_vars`/`host_vars` :

| Hôte | Rôle | Environnement | Particularité |
|---|---|---|---|
| lb1 | load balancer | prod | |
| web1, web2, web3 | serveurs web | prod | web3 : port SSH 2222 |
| db1 | base primaire | prod | `db_role: primary` |
| db2 | base réplica | prod | `db_role: replica` |
| web-stg1 | serveur web | staging | |
| db-stg1 | base | staging | |

## Énoncé

Créez un répertoire `inventory/` contenant :

1. `hosts.yml` avec les groupes `loadbalancers`, `webservers`, `dbservers`, `prod`, `staging` (prod et staging sont des **groupes de groupes** ; un hôte peut appartenir à un groupe de rôle **et** à un groupe d'environnement).
2. `group_vars/all.yml` : `ntp_server`, `app_name: shop`.
3. `group_vars/webservers.yml` : `http_port: 8080`.
4. `group_vars/prod.yml` : `env: prod`, `log_level: warn` ; `group_vars/staging.yml` : `env: staging`, `log_level: debug`.
5. `host_vars/db1.yml` et `host_vars/db2.yml` : `db_role`.

## Validation

```bash
ansible-inventory -i inventory --graph
ansible-inventory -i inventory --host web-stg1     # env: staging, log_level: debug, http_port: 8080
ansible -i inventory 'webservers:&prod' --list-hosts      # web1 web2 web3
ansible -i inventory 'dbservers:!db2' --list-hosts        # db1 + db-stg1
ansible -i inventory 'prod:&dbservers' --list-hosts       # db1 db2
```

**Question de réflexion** : quelle valeur de `log_level` a `web1` ? Et si vous ajoutez `log_level` dans `group_vars/webservers.yml` ? (→ précédence entre groupes de même niveau : ordre alphabétique, voir module 05.)

👉 Corrigé : [solution/](solution/)
