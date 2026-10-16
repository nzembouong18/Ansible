# Module 05 — Variables, facts et précédence

> **Durée** : 3 h · **Niveau** : intermédiaire

## 🎯 Objectifs

* Définir et utiliser des variables (types simples, listes, dictionnaires).
* Connaître **où** définir une variable et **qui gagne** (précédence).
* Exploiter les *facts*, les facts personnalisés et les variables magiques.
* Utiliser `register`, `set_fact`, `vars_files`, `vars_prompt`, `-e`.

---

## 1. Syntaxe et types

```yaml
vars:
  app_name: shop                 # chaîne
  http_port: 8080                # entier
  debug: false                   # booléen
  ratio: 0.75                    # flottant
  packages:                      # liste
    - nginx
    - git
  db:                            # dictionnaire
    host: db1
    port: 5432
    users: [app, ro]
```

Utilisation (Jinja2) :

```yaml
msg: "{{ app_name }} écoute sur {{ http_port }}"
msg: "{{ packages[0] }} / {{ packages | length }}"
msg: "{{ db.host }}:{{ db['port'] }}"          # les deux notations marchent
```

⚠️ **Piège n°1** : une valeur qui **commence** par `{{` doit être entre guillemets.

```yaml
path: "{{ base_dir }}/app"      # OK
path: {{ base_dir }}/app        # ERREUR YAML
```

**Noms valides** : lettres, chiffres, `_`, ne commence pas par un chiffre. Évitez les noms réservés (`environment`, `name`, `hosts`…) et préfixez par le rôle/appli (`nginx_port` plutôt que `port`).

## 2. Où définir des variables

| Emplacement | Portée | Usage typique |
|---|---|---|
| `defaults/main.yml` d'un rôle | rôle (très faible priorité) | valeurs par défaut **surchargeables** |
| inventaire : `group_vars/`, `host_vars/` | groupe / hôte | données d'environnement |
| `vars:` d'un play / `vars_files:` | play | constantes du playbook |
| `vars/main.yml` d'un rôle | rôle (forte priorité) | constantes internes du rôle |
| `vars:` d'une tâche / `block` | tâche / bloc | cas particuliers |
| `register`, `set_fact` | hôte, dynamique | résultats calculés |
| `-e` / `--extra-vars` | global, **priorité max** | surcharges ponctuelles, CI |
| `vars_prompt` | play | saisie interactive |
| facts | hôte | découverte automatique |

## 3. Précédence (de la plus faible à la plus forte)

Version à retenir (la liste officielle compte 22 niveaux) :

```
 1. valeurs par défaut de la ligne de commande (ex. ansible_user)
 2. defaults/main.yml d'un rôle                ◄── le plus faible : "valeur par défaut"
 3. inventaire : fichier hosts, variables de groupe (all, puis groupes)
 4. inventaire : group_vars/all
 5. inventaire : group_vars/<groupe>            (parent avant enfant)
 6. inventaire : variables d'hôte (dans hosts)
 7. inventaire : host_vars/<hote>
 8. playbook : group_vars/ puis host_vars/
 9. facts de l'hôte + set_fact avec cacheable
10. vars: du play
11. vars_prompt du play
12. vars_files du play
13. vars/main.yml d'un rôle
14. vars: d'un bloc
15. vars: d'une tâche
16. include_vars
17. set_fact / variables enregistrées (register)
18. paramètres de rôle et d'include (import_role/include_role + vars:)
19. -e / --extra-vars                           ◄── le plus fort : gagne toujours
```

**Règles de survie** :

1. Les **valeurs par défaut** d'un rôle vont dans `defaults/` (faciles à surcharger), jamais dans `vars/`.
2. L'**environnement** se décrit dans `group_vars`/`host_vars`.
3. `-e` pour le ponctuel : il écrase tout.
4. Entre deux groupes de **même niveau** qui définissent la même variable : ordre alphabétique du nom de groupe (le dernier gagne) sauf `ansible_group_priority`.
5. Évitez de définir la même variable à 5 endroits : si vous devez consulter la précédence, c'est déjà trop complexe.

🧪 La démo [demos/04-precedence.yml](demos/04-precedence.yml) rend cela tangible.

## 4. Les facts

Collectés par le module `setup` au début de chaque play (`gather_facts: true`).

```bash
ansible web1 -m setup | less
ansible web1 -m setup -a "filter=ansible_default_ipv4"
```

Facts fréquents (notation recommandée : `ansible_facts['…']`) :

| Besoin | Fact |
|---|---|
| Nom d'hôte | `ansible_facts['hostname']`, `['fqdn']` |
| OS | `['distribution']`, `['distribution_version']`, `['distribution_major_version']`, `['os_family']` |
| Noyau | `['kernel']` |
| Architecture | `['architecture']` |
| CPU / RAM | `['processor_vcpus']`, `['memtotal_mb']` |
| Réseau | `['default_ipv4']['address']`, `['interfaces']` |
| Disques | `['mounts']` (liste de dictionnaires) |
| Date | `['date_time']['iso8601']` |
| Python | `['python_version']` |
| Service manager | `['service_mgr']` |

⚠️ L'ancienne forme `ansible_hostname` (variable « injectée ») fonctionne encore mais est **dépréciée**, et peut être désactivée (`inject_facts_as_vars = False`) ; préférez `ansible_facts[...]`.

### Performances

```yaml
- hosts: all
  gather_facts: false          # inutile ? on gagne plusieurs secondes par hôte
- hosts: all
  gather_facts: true
  gather_subset: ['!all', '!min', 'network']   # seulement le réseau
```

* **Cache de facts** (`fact_caching = jsonfile` ou `redis`) : voir module 12.
* Le module `ansible.builtin.gather_facts` ou `setup` peut être rappelé en cours de playbook.

### Facts personnalisés (`facts.d`)

Déposez sur la cible un fichier `*.fact` (INI ou JSON, ou un exécutable renvoyant du JSON) dans `/etc/ansible/facts.d/` ; il apparaît sous `ansible_facts['ansible_local']['<nom>']`.

```ini
# /etc/ansible/facts.d/app.fact
[general]
version=1.4.2
role=frontend
```

→ `{{ ansible_facts['ansible_local']['app']['general']['version'] }}`

## 5. Variables magiques (fournies par Ansible)

| Variable | Contenu |
|---|---|
| `inventory_hostname` | nom de l'hôte **dans l'inventaire** |
| `inventory_hostname_short` | idem sans domaine |
| `groups` | dictionnaire `{groupe: [hôtes]}` |
| `group_names` | groupes de l'hôte courant |
| `hostvars` | variables/facts de **tous** les hôtes : `hostvars['db1']['ansible_facts']['default_ipv4']['address']` |
| `play_hosts` / `ansible_play_hosts` | hôtes du play |
| `ansible_play_batch` | hôtes du lot courant (avec `serial`) |
| `playbook_dir`, `role_path` | chemins |
| `ansible_check_mode` | `true` en `--check` |
| `ansible_version` | version d'Ansible |
| `omit` | valeur spéciale : « ne passe pas ce paramètre » |

**Cas typique : un serveur web qui a besoin de l'IP de la base :**

```yaml
db_host: "{{ hostvars[groups['dbservers'][0]]['ansible_facts']['default_ipv4']['address'] }}"
```

(⚠️ nécessite que les facts de `dbservers` aient été collectés plus tôt dans la même exécution — ex. un play préalable sur `all`.)

## 6. `set_fact`, `register`, `vars_files`, `vars_prompt`, `include_vars`

```yaml
- hosts: all
  vars_files:
    - vars/common.yml
    - "vars/{{ ansible_facts['os_family'] }}.yml"      # fichier selon l'OS
  vars_prompt:
    - name: release
      prompt: "Version à déployer"
      default: "1.0"
      private: false
  tasks:
    - name: Calculer une variable
      ansible.builtin.set_fact:
        full_name: "{{ app_name }}-{{ release }}"
        cacheable: true                      # persiste dans le cache de facts

    - name: Charger des variables dynamiquement
      ansible.builtin.include_vars:
        file: "vars/{{ env }}.yml"

    - name: Charger tout un dossier
      ansible.builtin.include_vars:
        dir: vars/apps
        extensions: [yml]
```

`omit` pour paramètres optionnels :

```yaml
- ansible.builtin.file:
    path: /tmp/x
    state: touch
    mode: "{{ file_mode | default(omit) }}"      # si non défini : le paramètre n'est pas envoyé
```

## 7. Variables et sécurité

* Ne mettez pas de secrets en clair dans `group_vars` : **Vault** (module 10).
* `no_log: true` pour masquer une tâche manipulant des secrets.
* `-e` apparaît dans l'historique shell et `ps` : évitez-y les secrets.

## 8. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-types.yml](demos/01-types.yml) | types, accès, `default()` |
| [demos/02-facts.yml](demos/02-facts.yml) | facts, `ansible_local`, `gather_subset` |
| [demos/03-magic-vars.yml](demos/03-magic-vars.yml) | `inventory_hostname`, `groups`, `hostvars` |
| [demos/04-precedence.yml](demos/04-precedence.yml) | qui gagne ? (avec `-e`) |
| [demos/05-set-fact-prompt.yml](demos/05-set-fact-prompt.yml) | `set_fact`, `vars_files`, `include_vars`, `omit` |

## 9. 🛠️ Labs

* [Lab 05 — Rapport d'inventaire matériel avec facts & variables](labs/lab-05-variables/README.md)

## ✅ Points clés

* Variables : `defaults` (faibles) → `group_vars/host_vars` → `play/tâche` → `-e` (fort).
* `ansible_facts['…']` plutôt que `ansible_xxx`.
* `hostvars` permet de lire une valeur d'un **autre** hôte.
* `default()` et `omit` rendent les playbooks robustes.

## ❓ Quiz

1. Quelle source écrase toutes les autres ? *(`-e`)*
2. Où placer une valeur par défaut d'un rôle ? *(`defaults/main.yml`)*
3. Comment lire l'IP d'un autre hôte ? *(`hostvars['db1']['ansible_facts']['default_ipv4']['address']`)*
4. Que fait `gather_facts: false` ? *(désactive la collecte, gain de temps)*
