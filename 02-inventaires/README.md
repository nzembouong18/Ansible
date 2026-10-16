# Module 02 — Inventaires

> **Durée** : 2 h · **Niveau** : débutant

## 🎯 Objectifs

* Écrire un inventaire INI et YAML.
* Organiser hôtes, groupes, groupes de groupes.
* Utiliser `group_vars/` et `host_vars/`.
* Maîtriser les *patterns* (`-l`, `hosts:`) et les variables de connexion.
* Connaître les inventaires multiples et dynamiques (aperçu).

---

## 1. Qu'est-ce qu'un inventaire ?

La réponse à « **sur quelles machines** ? ». Deux groupes implicites existent toujours : `all` (tous) et `ungrouped`. `localhost` est implicite.

### Format INI

```ini
# inventory/hosts.ini
mail.example.com                    ; hôte sans groupe

[webservers]
web1 ansible_host=192.168.56.11
web2 ansible_host=192.168.56.12
web[3:5].example.com                ; plage : web3 à web5

[dbservers]
db1 ansible_host=192.168.56.21 ansible_port=2222

[production:children]               ; groupe de groupes
webservers
dbservers

[webservers:vars]                   ; variables du groupe
http_port=80
```

### Format YAML (recommandé : types riches, listes, dictionnaires)

```yaml
all:
  hosts:
    mail.example.com:
  children:
    webservers:
      hosts:
        web1: { ansible_host: 192.168.56.11 }
        web2: { ansible_host: 192.168.56.12 }
      vars:
        http_port: 80
    dbservers:
      hosts:
        db1:
          ansible_host: 192.168.56.21
          ansible_port: 2222
    production:
      children:
        webservers:
        dbservers:
```

### Visualiser et valider

```bash
ansible-inventory -i inventory/hosts.yml --list          # JSON complet (avec variables fusionnées)
ansible-inventory -i inventory/hosts.yml --graph         # arbre des groupes
ansible-inventory -i inventory/hosts.yml --graph --vars  # avec variables
ansible-inventory -i inventory/hosts.yml --host web1     # variables d'un hôte
ansible all --list-hosts
```

## 2. Variables de connexion (les « magiques » d'inventaire)

| Variable | Rôle | Exemple |
|---|---|---|
| `ansible_host` | adresse réelle (si ≠ nom) | `192.168.1.10` |
| `ansible_port` | port SSH | `2222` |
| `ansible_user` | utilisateur SSH | `deploy` |
| `ansible_ssh_private_key_file` | clé privée | `~/.ssh/deploy` |
| `ansible_connection` | `ssh` (défaut), `local`, `docker`, `winrm`, `network_cli`… | `local` |
| `ansible_become` / `ansible_become_user` / `ansible_become_method` | élévation de privilèges | `true` / `root` / `sudo` |
| `ansible_python_interpreter` | Python distant | `/usr/bin/python3` |
| `ansible_ssh_common_args` | options SSH, ex. rebond | `-o ProxyJump=bastion` |

🔒 N'écrivez **jamais** de mot de passe en clair (`ansible_password`, `ansible_become_password`) : utilisez Vault (module 10).

**Hôte de rebond (bastion)** :

```yaml
all:
  vars:
    ansible_ssh_common_args: "-o ProxyJump=deploy@bastion.example.com"
```

## 3. `group_vars/` et `host_vars/`

Plutôt que de tout entasser dans l'inventaire, utilisez des fichiers **à côté de l'inventaire** (ou du playbook) :

```
inventory/
├── hosts.yml
├── group_vars/
│   ├── all.yml              # pour tous
│   ├── webservers.yml       # pour le groupe webservers
│   └── production/          # un dossier : tous les fichiers sont fusionnés
│       ├── main.yml
│       └── vault.yml        # (chiffré, module 10)
└── host_vars/
    └── web1.yml             # pour un seul hôte
```

Priorité (de la plus faible à la plus forte) : `all` < groupe parent < groupe enfant < hôte. Détails de la précédence complète au module 05.

## 4. Patterns : choisir ses cibles

Utilisables dans `hosts:` d'un play, avec `ansible <pattern>` ou avec `--limit` / `-l`.

| Pattern | Signification |
|---|---|
| `all` ou `*` | tous les hôtes |
| `web1` | un hôte |
| `web1:web2` ou `web1,web2` | union |
| `webservers:dbservers` | union de groupes |
| `webservers:!web2` | webservers **sauf** web2 |
| `webservers:&production` | **intersection** |
| `~web[0-9]+` | expression régulière |
| `webservers[0]`, `webservers[0:1]` | indexation |

```bash
ansible 'webservers:!web2' --list-hosts
ansible-playbook site.yml --limit 'production:&webservers'
ansible-playbook site.yml --limit @failed_hosts.txt     # relancer sur les hôtes en échec
```

## 5. Inventaires multiples & environnements

Convention classique : **un inventaire par environnement**, le même code de playbook.

```
inventories/
├── dev/
│   ├── hosts.yml
│   └── group_vars/all.yml
├── staging/…
└── prod/
    ├── hosts.yml
    └── group_vars/all.yml
```

```bash
ansible-playbook -i inventories/dev/hosts.yml site.yml
ansible-playbook -i inventories/prod/hosts.yml site.yml
```

On peut aussi passer **plusieurs** `-i` (ou un répertoire) : Ansible fusionne.

## 6. Inventaires dynamiques (aperçu — module 13)

Au lieu d'un fichier statique, un *plugin d'inventaire* interroge une source : AWS EC2, Azure, GCP, VMware, Terraform, Proxmox, NetBox… :

```yaml
# aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [eu-west-3]
keyed_groups:
  - key: tags.Role
    prefix: role
```

## 7. Ajouter des hôtes à la volée

* `add_host` (module) : crée un hôte pendant l'exécution (ex. VM tout juste créée).
* `group_by` : crée des groupes selon des facts (ex. `os_Ubuntu`).

```yaml
- hosts: all
  tasks:
    - ansible.builtin.group_by:
        key: "os_{{ ansible_facts['distribution'] }}"
- hosts: os_Ubuntu
  tasks:
    - ansible.builtin.debug: msg="Ubuntu uniquement"
```

## 8. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/inventaire-ini/hosts.ini](demos/inventaire-ini/hosts.ini) | format INI complet |
| [demos/inventaire-yaml/](demos/inventaire-yaml/) | format YAML + group_vars/host_vars |
| [demos/group_by.yml](demos/group_by.yml) | groupes dynamiques |

```bash
cd 02-inventaires/demos
ansible-inventory -i inventaire-yaml/hosts.yml --graph --vars
ansible-inventory -i inventaire-yaml/hosts.yml --host web1
ansible -i inventaire-yaml/hosts.yml 'webservers:!web2' --list-hosts
ansible -i inventaire-yaml/hosts.yml 'production:&webservers' --list-hosts
```

## 9. 🛠️ Labs

* [Lab 02 — Construire l'inventaire d'une application 3-tiers](labs/lab-02-inventaire-3tiers/README.md)

## ✅ Points clés

* Inventaire = hôtes + groupes + variables ; YAML préféré.
* `group_vars/` et `host_vars/` à côté de l'inventaire pour séparer données et structure.
* Les patterns (`:`, `!`, `&`) + `--limit` donnent un contrôle fin.
* Un inventaire par environnement, un seul code.

## ❓ Quiz

1. Quel groupe contient tous les hôtes ? *(`all`)*
2. Comment cibler `webservers` sauf `web2` ? *(`webservers:!web2`)*
3. Où mettre les variables d'un seul serveur ? *(`host_vars/<hote>.yml`)*
4. Quelle commande affiche l'arbre des groupes ? *(`ansible-inventory --graph`)*
