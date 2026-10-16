# Lab 13 — Inventaire dynamique à partir d'un CSV (CMDB)

⏱️ 1 h 15 · 100 % local.

## 🎯 Objectif

Votre « CMDB » est un fichier `serveurs.csv`. Écrivez un **script d'inventaire** qui le convertit en inventaire Ansible, puis enrichissez-le avec le plugin `constructed`.

## Données (`serveurs.csv`)

```csv
name,ip,role,env,datacenter,cpu
web-01,10.0.1.11,web,prod,par,4
web-02,10.0.1.12,web,prod,lon,8
db-01,10.0.2.21,db,prod,par,16
web-stg,10.0.9.11,web,staging,par,2
cache-01,10.0.3.31,cache,prod,lon,4
```

## Énoncé

1. `inventory_csv.py` (exécutable) : respecte `--list` et `--host` ; groupes `role_<role>` et `env_<env>` ; `ansible_host` = ip ; `cpu`, `datacenter` en variables d'hôte ; section `_meta.hostvars` ; le chemin du CSV est lu depuis la variable d'environnement `CMDB_CSV` (défaut : `serveurs.csv` à côté du script) ; message d'erreur clair (code retour ≠ 0) si le fichier est absent.
2. `constructed.yml` (plugin `constructed`, utilisé **avec** le script en passant deux `-i`) : crée le groupe `big_servers` (`cpu | int >= 8`), le groupe `dc_<datacenter>` via `keyed_groups`, et la variable `fqdn` = `<name>.<datacenter>.example.com`.
3. Un playbook `affiche.yml` qui, pour le groupe `big_servers`, affiche `fqdn` et `ansible_host` (`connection: local`, `gather_facts: false`, pas de connexion réelle : utilisez `ansible_connection=local` via `compose`).

## Validation

```bash
./inventory_csv.py --list | python3 -m json.tool | head
ansible-inventory -i inventory_csv.py -i constructed.yml --graph
ansible-playbook -i inventory_csv.py -i constructed.yml affiche.yml
CMDB_CSV=/nope.csv ansible-inventory -i inventory_csv.py --list   # erreur claire attendue
```

Ajoutez une ligne au CSV : sans toucher au reste, le nouvel hôte apparaît.

👉 Corrigé : [solution/](solution/)
