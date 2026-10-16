# Module 13 — Inventaires dynamiques et plugins d'inventaire

> **Durée** : 2 h 30 · **Niveau** : avancé

## 🎯 Objectifs

* Comprendre pourquoi un inventaire statique ne suffit pas dans le cloud.
* Utiliser les plugins d'inventaire officiels (AWS, Azure, GCP, Docker, Proxmox, NetBox, Terraform).
* Écrire un **script d'inventaire** (contrat `--list` / `--host`).
* Enrichir avec `constructed` (groupes et variables calculés) et mettre en cache.

---

## 1. Du statique au dynamique

Dans le cloud, les machines apparaissent et disparaissent : maintenir `hosts.yml` à la main est source d'erreurs. Un **inventaire dynamique** interroge la source de vérité (API cloud, CMDB, hyperviseur, état Terraform) **à chaque exécution**.

| Type | Fichier | Exemple |
|---|---|---|
| Statique | INI / YAML | `hosts.yml` |
| **Plugin** (recommandé) | YAML avec clé `plugin:` | `aws_ec2.yml` |
| **Script** (hérité mais simple) | exécutable `--list`/`--host` | `inventory.py` |

Les plugins se reconnaissent à leur nom de fichier (souvent obligatoirement `*.aws_ec2.yml`, `*.azure_rm.yml` selon le plugin) et à `plugin: namespace.collection.nom`.

Activation (déjà par défaut : `host_list, script, auto, yaml, ini, toml`) :

```ini
[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml, constructed, amazon.aws.aws_ec2
```

## 2. Plugins de la vie réelle

Exemples dans [demos/cloud-examples/](demos/cloud-examples/) :

| Source | Plugin | Prérequis |
|---|---|---|
| AWS EC2 | `amazon.aws.aws_ec2` | `boto3`, identifiants AWS |
| Azure | `azure.azcollection.azure_rm` | SDK Azure |
| GCP | `google.cloud.gcp_compute` | `google-auth` |
| Docker | `community.docker.docker_containers` | accès socket |
| Proxmox | `community.proxmox.proxmox` | API token |
| NetBox (CMDB) | `netbox.netbox.nb_inventory` | token |
| VMware | `community.vmware.vmware_vm_inventory` | pyvmomi |
| Terraform | `cloud.terraform.terraform_provider` | état Terraform |
| OpenStack, Kubernetes, ServiceNow… | `openstack.cloud.openstack`, `kubernetes.core.k8s`, `servicenow.itsm.now` | |

```bash
ansible-inventory -i aws_ec2.yml --graph
ansible-inventory -i aws_ec2.yml --list --yaml
ansible-doc -t inventory amazon.aws.aws_ec2         # toutes les options
```

### Options communes à presque tous les plugins

* `keyed_groups` : crée des groupes depuis une valeur (`tags.Role` → `role_web`).
* `groups` : groupes par expression Jinja booléenne.
* `compose` : variables calculées (ex. `ansible_host: private_ip_address`).
* `hostnames` : comment nommer les hôtes (nom, tag `Name`, IP privée…).
* `filters` : filtrer côté API (moins de données, plus rapide).
* `cache`, `cache_plugin`, `cache_timeout` : éviter d'appeler l'API à chaque commande.

`ansible-inventory --flush-cache` / `meta: refresh_inventory` (dans un playbook, après avoir créé des VM).

## 3. Écrire un script d'inventaire

Contrat :

* `script --list` → JSON : groupes (`hosts`, `children`, `vars`) et `_meta.hostvars` ;
* `script --host <nom>` → JSON des variables de l'hôte (inutile si `_meta` est fourni).

```json
{
  "_meta": { "hostvars": { "web-01": { "ansible_host": "10.0.1.11" } } },
  "role_web": { "hosts": ["web-01"] },
  "production": { "children": ["role_web"], "vars": { "env": "prod" } }
}
```

Voir [demos/inventory-script.py](demos/inventory-script.py). Règles :

1. Toujours `_meta.hostvars` (sinon Ansible appelle le script une fois par hôte → lent).
2. Sortie JSON uniquement sur stdout ; erreurs sur stderr + code retour ≠ 0.
3. Les identifiants viennent de l'environnement, pas du code.
4. Rendez le script rapide ou ajoutez un cache.
5. Pour du code durable, préférez écrire un **plugin d'inventaire** (module 14).

## 4. Le plugin `constructed`

Il **post-traite** d'autres sources : crée groupes et variables sans modifier la source.

```yaml
plugin: ansible.builtin.constructed
strict: false
compose:
  fqdn: inventory_hostname ~ '.' ~ datacenter ~ '.example.com'
groups:
  big_servers: cpu | int >= 8
keyed_groups:
  - { key: datacenter, prefix: dc }
```

Utilisation : `ansible-inventory -i source.yml -i constructed.yml --graph` (plusieurs `-i` ou un **répertoire** d'inventaires).

## 5. Inventaires dans un répertoire / mixtes

```
inventories/prod/
├── 01-static.yml          # hôtes fixes (bastion, DB legacy)
├── 02-aws_ec2.yml         # hôtes cloud
├── 99-constructed.yml     # groupes dérivés
└── group_vars/
```

`-i inventories/prod/` fusionne tout, `group_vars/` s'applique à l'ensemble.

## 6. `add_host` et `refresh_inventory` dans un playbook

```yaml
- name: Créer une VM puis la configurer
  hosts: localhost
  tasks:
    - name: Créer l'instance
      amazon.aws.ec2_instance: { ... }
      register: vm

    - name: L'ajouter à l'inventaire en mémoire
      ansible.builtin.add_host:
        name: "{{ vm.instances[0].private_ip_address }}"
        groups: new_servers
        ansible_user: ubuntu

    - name: Attendre SSH
      ansible.builtin.wait_for:
        host: "{{ vm.instances[0].private_ip_address }}"
        port: 22

- hosts: new_servers
  roles: [common, nginx]
```

## 7. Bonnes pratiques

1. La **source de vérité** est la CMDB/le cloud ; l'inventaire n'est qu'un reflet.
2. **Étiquetez** les machines (`Role`, `Env`, `Owner`) : les `keyed_groups` en dépendent.
3. Mettez en **cache** et filtrez côté API.
4. Séparez `group_vars` (données stables) des attributs dynamiques.
5. Ne codez pas d'identifiants dans les fichiers : variables d'environnement, Vault, IAM role.
6. Testez avec `ansible-inventory --graph` avant tout playbook.

## 8. 🧪 Démos

Dossier [demos/](demos/) ; script guidé : `./01-utiliser-inventaires.sh`.

| Démo | Contenu |
|---|---|
| [inventory-script.py](demos/inventory-script.py) | script `--list`/`--host` |
| [constructed/](demos/constructed) | `hosts.yml` + `constructed.yml` |
| [generator/](demos/generator) | hôtes générés par combinaisons |
| [cloud-examples/](demos/cloud-examples) | AWS, Azure, GCP, Docker, Proxmox, NetBox, Terraform |

## 9. 🛠️ Labs

* [Lab 13 — Inventaire dynamique alimenté par un CSV (CMDB)](labs/lab-13-inventaire-csv/README.md)

## ✅ Points clés

* Plugins > scripts ; `ansible-inventory --graph` pour vérifier.
* `keyed_groups`, `compose`, `groups`, `filters`, `cache` = 90 % des besoins.
* Étiquetage cohérent côté cloud = inventaire exploitable.

## ❓ Quiz

1. Quelles options doit gérer un script d'inventaire ? *(`--list`, `--host`)*
2. Quel intérêt de `_meta.hostvars` ? *(un seul appel au lieu d'un par hôte)*
3. Quel plugin crée des groupes à partir de variables ? *(`constructed`)*
4. Comment recharger l'inventaire en cours de playbook ? *(`meta: refresh_inventory`)*
