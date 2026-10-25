# Module 08 — Les rôles

> **Durée** : 3 h 30 · **Niveau** : intermédiaire → avancé

## 🎯 Objectifs

* Structurer l'automatisation en **rôles** réutilisables.
* Connaître l'arborescence standard et le rôle de chaque dossier.
* Écrire un rôle **multi-OS**, paramétrable et documenté.
* Gérer dépendances, ordre d'exécution, `import_role` / `include_role`.
* Appliquer les conventions de nommage (préfixe de variables, `defaults` vs `vars`).

---

## 1. Pourquoi des rôles ?

Un playbook de 600 lignes est illisible et non réutilisable. Un **rôle** est une brique : « installer et configurer nginx », « durcir SSH », « déployer l'appli X ». Le playbook devient une simple **composition** :

```yaml
- hosts: webservers
  roles:
    - common
    - nginx
    - app_deploy
```

## 2. Arborescence

```bash
ansible-galaxy role init --init-path roles nginx
```

```
roles/nginx/
├── defaults/main.yml     # variables par défaut — PRIORITÉ FAIBLE → l'interface publique du rôle
├── vars/main.yml         # variables internes — priorité forte (constantes, par OS)
├── tasks/main.yml        # point d'entrée des tâches (peut inclure d'autres fichiers)
├── handlers/main.yml     # handlers
├── templates/*.j2        # templates Jinja2 (référencés sans chemin)
├── files/                # fichiers statiques (copy sans chemin)
├── meta/main.yml         # métadonnées, dépendances, plateformes
├── library/              # modules custom du rôle (module 14)
├── module_utils/, filter_plugins/, lookup_plugins/  # plugins du rôle
├── tests/ ou molecule/   # tests (module 15)
└── README.md             # documentation : variables, exemples
```

Seul `tasks/main.yml` est indispensable. Ansible charge automatiquement `main.yml` de chaque dossier.

### `defaults` vs `vars` : la règle d'or

| | `defaults/main.yml` | `vars/main.yml` |
|---|---|---|
| Priorité | **la plus basse** | haute (écrase inventaire et play) |
| Rôle | paramètres que l'utilisateur **peut/doit** surcharger | constantes internes (noms de paquets par OS, chemins) |
| Exemple | `nginx_port: 80` | `nginx_service_name: nginx` |

Si l'utilisateur doit pouvoir le changer → `defaults`. Sinon `vars`.

## 3. Conventions

1. **Préfixez toutes les variables par le nom du rôle** : `nginx_port`, `nginx_user`. Sans préfixe, les variables fuient dans tout le play (portée globale !) et entrent en collision.
2. Variables internes (calculées) préfixées par `__nginx_` ou `_nginx_`.
3. Un fichier de tâches par thème : `install.yml`, `configure.yml`, `service.yml`, appelés par `main.yml` avec des **tags**.
4. Idempotent, `--check` compatible, `no_log` sur les secrets.
5. Documentez les variables dans le README du rôle (nom, défaut, rôle).
6. Validez les entrées avec `assert` (ou `argument_specs`, voir ci-dessous).

## 4. Rôle multi-OS : le patron classique

```yaml
# roles/nginx/tasks/main.yml
---
- name: Charger les variables spécifiques à l'OS
  ansible.builtin.include_vars: "{{ lookup('ansible.builtin.first_found', params) }}"
  vars:
    params:
      files:
        - "{{ ansible_facts['distribution'] }}-{{ ansible_facts['distribution_major_version'] }}.yml"
        - "{{ ansible_facts['distribution'] }}.yml"
        - "{{ ansible_facts['os_family'] }}.yml"
        - default.yml
      paths: [vars]

- name: Installer
  ansible.builtin.import_tasks: install.yml
  tags: [nginx_install]

- name: Configurer
  ansible.builtin.import_tasks: configure.yml
  tags: [nginx_configure]

- name: Service
  ansible.builtin.import_tasks: service.yml
  tags: [nginx_service]
```

```yaml
# roles/nginx/vars/Debian.yml
__nginx_package: nginx
__nginx_conf_dir: /etc/nginx
__nginx_user: www-data
```

```yaml
# roles/nginx/vars/RedHat.yml
__nginx_package: nginx
__nginx_conf_dir: /etc/nginx
__nginx_user: nginx
```

## 5. `meta/main.yml`, dépendances & `argument_specs`

```yaml
# meta/main.yml
galaxy_info:
  author: moi
  description: nginx
  license: MIT
  min_ansible_version: "2.14"
  platforms:
    - { name: Ubuntu, versions: [jammy, noble] }
    - { name: EL, versions: ["8", "9"] }
dependencies:
  - role: common                 # exécuté avant ce rôle
  - role: firewall
    vars: { firewall_open_ports: [80, 443] }
```

⚠️ Une dépendance n'est exécutée qu'**une fois** par play (même rôle + mêmes paramètres), sauf `allow_duplicates: true`. Préférez souvent composer dans le playbook plutôt que d'empiler des dépendances implicites.

**`meta/argument_specs.yml`** (ansible-core ≥ 2.11) : valide automatiquement les paramètres avant l'exécution et alimente `ansible-doc -t role` :

```yaml
argument_specs:
  main:
    short_description: Installe nginx
    options:
      nginx_port:
        type: int
        default: 80
        description: Port d'écoute
      nginx_sites:
        type: list
        elements: dict
        required: false
        options:
          name: { type: str, required: true }
          root: { type: str, default: /var/www/html }
```

## 6. Appeler un rôle

a) Section `roles:` du play — exécutée **avant** `tasks:` :

```yaml
roles:
  - nginx
  - { role: nginx, nginx_port: 8080, tags: [web] }
```

b) `import_role` — statique (analysé au chargement) :

```yaml
- ansible.builtin.import_role:
    name: nginx
```

c) `include_role` — dynamique (boucle, `when`, nom variable) :

```yaml
- ansible.builtin.include_role:
    name: "{{ item }}"
    apply:
      tags: [web]
  loop: "{{ roles_to_apply }}"
```

d) Un sous-ensemble : un autre fichier de tâches du rôle :

```yaml
- ansible.builtin.include_role:
    name: nginx
    tasks_from: vhost.yml
```

**Recherche des rôles** : `roles/` à côté du playbook, `roles_path` d'`ansible.cfg`, `~/.ansible/roles`, `/usr/share/ansible/roles`, collections.

Un rôle peut être appelé **plusieurs fois** avec des paramètres différents (avec `allow_duplicates: true` dans `meta/main.yml`).

## 7. Rôles et handlers/tags/variables : points d'attention

* Les handlers d'un rôle sont dans l'espace de noms **global du play** : donnez-leur des noms préfixés (« Nginx : recharger »).
* Les tags d'un rôle (`roles: [{role: x, tags: t}]`) s'appliquent à toutes ses tâches.
* `defaults` surchargés par `group_vars` : c'est le mécanisme normal de configuration d'un rôle.
* Les variables `register` et `set_fact` d'un rôle **fuitent** dans le reste du play : préfixez-les.

## 8. Organisation d'un dépôt à l'échelle

```
.
├── ansible.cfg
├── requirements.yml          # rôles/collections externes
├── site.yml                  # import_playbook de tout
├── inventories/{dev,prod}/{hosts.yml,group_vars/,host_vars/}
├── playbooks/{web.yml,db.yml,...}
├── roles/                    # vos rôles
│   └── requirements.yml
└── collections/              # (optionnel) collections vendorisées
```

Le module 09 couvre le partage via Galaxy/collections, le module 20 une organisation complète.

## 9. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/roles/motd](demos/roles/motd) | un rôle minimal complet (defaults, tasks, handlers, templates, meta) |
| [demos/01-utiliser-un-role.yml](demos/01-utiliser-un-role.yml) | appel avec surcharge de variables |
| [demos/02-roles-modes.yml](demos/02-roles-modes.yml) | `roles:`, `import_role`, `include_role` en boucle |

## 10. 🛠️ Labs

* [Lab 08 — Écrire un rôle nginx multi-OS](labs/lab-08-role-nginx/README.md) (rôle complet en corrigé)

## ✅ Points clés

* Rôle = dossier standardisé ; `defaults` = interface, `vars` = interne.
* Préfixez toutes les variables par le nom du rôle.
* Multi-OS : `include_vars` + `first_found` ou `when` par `os_family`.
* `argument_specs` valide les entrées ; README documente.
* Compose dans le playbook, limite les dépendances implicites.

## ❓ Quiz

1. Où mettre une valeur que l'utilisateur doit pouvoir surcharger facilement ? *(`defaults/main.yml`)*
2. Pourquoi préfixer les variables ? *(portée globale → collisions)*
3. Différence `import_role` / `include_role` ? *(statique / dynamique)*
4. Comment valider les paramètres d'un rôle ? *(`meta/argument_specs.yml`)*
