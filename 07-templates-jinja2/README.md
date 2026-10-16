# Module 07 — Templates Jinja2, filtres et lookups

> **Durée** : 3 h · **Niveau** : intermédiaire

## 🎯 Objectifs

* Générer des fichiers de configuration dynamiques avec le module `template`.
* Maîtriser la syntaxe Jinja2 : expressions, boucles, conditions, macros, commentaires.
* Utiliser les filtres les plus utiles (`default`, `join`, `map`, `select`, `regex_replace`, `to_nice_yaml`, `ipaddr`…).
* Utiliser les *lookups* (`file`, `env`, `password`, `pipe`, `template`, `url`).

---

## 1. Le module `template`

Jinja2 est évalué **sur le contrôleur** ; le résultat est envoyé à la cible.

```yaml
- name: Générer nginx.conf
  ansible.builtin.template:
    src: nginx.conf.j2           # cherché dans templates/ (rôle) ou à côté du playbook
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: "0644"
    validate: nginx -t -c %s     # valide le fichier généré AVANT de le mettre en place
    backup: true                 # garde une copie datée de l'ancien fichier
  notify: Recharger nginx
```

`copy` = fichier tel quel ; `template` = fichier passé à Jinja2. Convention : suffixe `.j2`.

Ajoutez toujours un en-tête pour décourager l'édition manuelle :

```jinja
# {{ ansible_managed }}
# Généré pour {{ inventory_hostname }}
```

(`ansible_managed` est une variable spéciale : sa valeur par défaut est « Ansible managed ». Redéfinissez-la, par ex. dans `group_vars/all`, pour un message plus explicite : `ansible_managed: "Géré par Ansible - ne pas modifier à la main"`.)

## 2. Syntaxe Jinja2

| Syntaxe | Rôle |
|---|---|
| `{{ expression }}` | affiche une valeur |
| `{% instruction %}` | logique : `if`, `for`, `set`, `macro`… |
| `{# commentaire #}` | commentaire (non rendu) |
| `{%- … -%}` | supprime les espaces/sauts de ligne autour |

### Variables et expressions

```jinja
Serveur : {{ inventory_hostname | upper }}
Port    : {{ http_port | default(80) }}
Total   : {{ (ram_mb / 1024) | round(1) }} Go
Base    : {{ db.host }}:{{ db['port'] }}
```

### Conditions

```jinja
{% if env == 'prod' %}
log_level = warn
{% elif env == 'staging' %}
log_level = info
{% else %}
log_level = debug
{% endif %}
```

### Boucles

```jinja
{% for h in groups['webservers'] %}
server {{ hostvars[h]['ansible_facts']['default_ipv4']['address'] }}:{{ http_port }};
{% endfor %}

{% for key, value in settings.items() %}
{{ key }} = {{ value }}
{% endfor %}

{% for u in users if u.active %}      {# filtre dans la boucle #}
{{ loop.index }}. {{ u.name }}{{ "," if not loop.last }}
{% endfor %}
```

Variables de boucle : `loop.index` (1-based), `loop.index0`, `loop.first`, `loop.last`, `loop.length`.

### Macros, `set`, `include`

```jinja
{% set workers = ansible_facts['processor_vcpus'] * 2 %}
worker_processes {{ workers }};

{% macro vhost(name, port=80) %}
server { listen {{ port }}; server_name {{ name }}; }
{% endmacro %}
{{ vhost('a.example.com') }}
{{ vhost('b.example.com', 8080) }}
```

### Maîtriser les espaces

Par défaut Ansible active `trim_blocks` (le saut de ligne après un `{% %}` est supprimé) et `lstrip_blocks`. Utilisez `{%- -%}` pour affiner. Contrôlez toujours le rendu avec `--check --diff`.

## 3. Filtres essentiels

### Valeurs par défaut & types

| Filtre | Exemple → résultat |
|---|---|
| `default(x)` | `{{ port \| default(80) }}` ; `default(x, true)` aussi pour vide/faux |
| `mandatory` | échoue si non défini |
| `bool`, `int`, `float`, `string` | conversions |
| `length` / `count` | taille |

### Chaînes

`upper`, `lower`, `capitalize`, `title`, `trim`, `replace('a','b')`, `regex_replace('^v','')`, `regex_search('\d+')`, `regex_findall`, `split(',')`, `join(', ')`, `quote` (échappement shell), `b64encode`, `b64decode`, `hash('sha256')`, `password_hash('sha512')`, `comment` (commente un bloc).

### Listes

| Filtre | Exemple |
|---|---|
| `first`, `last`, `min`, `max`, `sum`, `sort`, `unique`, `reverse` | `{{ [3,1,2] \| sort }}` |
| `map(attribute='name')` | `{{ users \| map(attribute='name') \| list }}` |
| `select('match','^web')` / `reject` | filtre par test |
| `selectattr('active')` / `rejectattr` | `{{ users \| selectattr('active') \| list }}` |
| `union`, `intersect`, `difference`, `symmetric_difference` | ensembles |
| `flatten` | aplatit des listes imbriquées |
| `zip`, `product`, `combinations` | combinaisons |
| `batch(3)`, `slice(3)` | découpage |
| `groupby('os')` | regroupement |

### Dictionnaires

`dict2items` / `items2dict`, `combine({...}, recursive=True)` (fusion), `dictsort`, `json_query('…')` (JMESPath), `ansible.utils.*`.

### Formats de données

`to_json`, `to_nice_json`, `to_yaml`, `to_nice_yaml(indent=2)`, `from_json`, `from_yaml`, `ansible.builtin.ini` lookup, `xml` via `community.general`.

### Réseau (collection `ansible.utils`)

`ansible.utils.ipaddr`, `ipv4`, `ipsubnet`, `network_in_usable`… → `pip install netaddr` requis.

### Fichiers/chemins

`basename`, `dirname`, `expanduser`, `realpath`, `splitext`, `win_basename`.

### Exemple récapitulatif

```yaml
vars:
  users:
    - { name: alice, active: true,  groups: [dev, ops] }
    - { name: bob,   active: false, groups: [dev] }
    - { name: carol, active: true,  groups: [ops] }
tasks:
  - ansible.builtin.debug:
      msg: "{{ users | selectattr('active') | map(attribute='name') | sort | join(', ') }}"
  # → alice, carol
  - ansible.builtin.debug:
      msg: "{{ users | map(attribute='groups') | flatten | unique | sort }}"
  # → ['dev', 'ops']
```

## 4. Tests Jinja (`is …`)

`is defined`, `is none`, `is string/number/mapping/iterable`, `is divisibleby(3)`, `is in([..])`, `is match/search(regex)`, `is version('1.2','>=')`, `is file/directory/link` (sur le contrôleur), `is subset/superset`, `is truthy/falsy` (2.10+).

## 5. Lookups

Exécutés sur le **contrôleur**, au moment de l'évaluation.

```yaml
motd:   "{{ lookup('ansible.builtin.file', 'files/motd.txt') }}"
home:   "{{ lookup('ansible.builtin.env', 'HOME') }}"
cle:    "{{ lookup('ansible.builtin.password', 'credentials/db.pwd length=24 chars=ascii_letters,digits') }}"
heure:  "{{ lookup('ansible.builtin.pipe', 'date +%F') }}"
tpl:    "{{ lookup('ansible.builtin.template', 'snippet.j2') }}"
ligne:  "{{ lookup('ansible.builtin.ini', 'port section=server file=app.ini') }}"
items:  "{{ lookup('ansible.builtin.fileglob', 'files/*.conf', wantlist=True) }}"
csv:    "{{ lookup('ansible.builtin.csvfile', 'alice file=users.csv delimiter=, col=1') }}"
```

* `lookup()` retourne une chaîne ; `query()` (ou `wantlist=True`) retourne une **liste**.
* `password` : génère *et mémorise* un mot de passe (idempotent entre exécutions) — pratique en labo, ne remplace pas un coffre (module 19).
* Autres : `url`, `dig` (DNS), `community.general.random_string`, `hashi_vault`, `aws_ssm`, `community.general.keyring`.

## 6. Bonnes pratiques

1. **Peu de logique** dans les templates : calculez dans le playbook (`set_fact`, `vars`) et laissez le template afficher.
2. Toujours `default()` pour les valeurs optionnelles.
3. Validez avec `validate:` (nginx -t, sshd -t, visudo -cf %s, apachectl…).
4. `ansible_managed` en en-tête.
5. Testez le rendu **sans cible** : `ansible localhost -m template -a "src=x.j2 dest=/tmp/x" -e @vars.yml`, ou la tâche `debug: msg: "{{ lookup('template','x.j2') }}"`.
6. Pour des formats structurés (YAML/JSON), préférez `to_nice_yaml`/`to_nice_json` à la construction à la main.

## 7. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-filtres.yml](demos/01-filtres.yml) | tour des filtres usuels |
| [demos/02-template.yml](demos/02-template.yml) + [templates/](demos/templates/) | nginx.conf, if/for/macro, rendu local |
| [demos/03-lookups.yml](demos/03-lookups.yml) | file, env, pipe, password, template |
| [demos/04-json-query.yml](demos/04-json-query.yml) | `json_query` / JMESPath |

## 8. 🛠️ Labs

* [Lab 07 — Générer la config d'un load balancer HAProxy depuis l'inventaire](labs/lab-07-templates/README.md)

## ✅ Points clés

* `template` = Jinja2 + `validate` + `backup` + handler.
* Filtres : `default`, `map/select`, `join`, `combine`, `to_nice_yaml`.
* Lookups = sur le contrôleur ; `query` pour des listes.
* Mettre la logique dans le playbook, pas dans le template.

## ❓ Quiz

1. Où le template est-il rendu ? *(sur le contrôleur)*
2. Comment obtenir les noms des utilisateurs actifs ? *(`selectattr('active') | map(attribute='name')`)*
3. À quoi sert `validate:` ? *(vérifier le fichier généré avant installation)*
4. Différence `lookup` / `query` ? *(chaîne vs liste)*
