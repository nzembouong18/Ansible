# Module 04 — Les playbooks

> **Durée** : 3 h · **Niveau** : débutant → intermédiaire

## 🎯 Objectifs

* Maîtriser la structure d'un playbook : plays, tasks, modules, `become`.
* Utiliser `ansible-playbook` et ses options (`--check`, `--diff`, `--limit`, `--tags`, `--start-at-task`…).
* Introduire handlers, `register`, `debug`.
* Découper un playbook : `import_playbook`, `import_tasks`, `include_tasks`.
* Écrire du YAML propre et valider avec `yamllint` / `ansible-lint`.

---

## 1. Anatomie

```yaml
---                                   # (1) fichier = liste de plays
- name: Configurer les serveurs web   # (2) play : nom lisible
  hosts: webservers                   # (3) QUI : pattern d'inventaire
  become: true                        # (4) élévation de privilèges pour le play
  gather_facts: true                  # (5) collecte des facts (défaut)
  vars:                               # (6) variables du play
    http_port: 80

  pre_tasks:                          # (7) avant les rôles
    - name: Mettre à jour le cache apt
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600

  roles: []                           # (8) rôles (module 08)

  tasks:                              # (9) tâches ordonnées
    - name: Installer nginx           # nom = ce qui s'affiche
      ansible.builtin.package:        # module (FQCN)
        name: nginx                   # paramètres
        state: present
      notify: Redémarrer nginx        # déclenche un handler si "changed"

  post_tasks: []                      # (10) après les tâches

  handlers:                           # (11) exécutés en fin de play, une seule fois
    - name: Redémarrer nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

**Ordre d'exécution d'un play** : `pre_tasks` → handlers → `roles` → `tasks` → handlers → `post_tasks` → handlers.

### FQCN : toujours nommer les modules en entier

`ansible.builtin.copy` plutôt que `copy` : explicite, évite les collisions, exigé par `ansible-lint` (profil production).

### Plusieurs plays dans un fichier

```yaml
- name: Bases de données d'abord
  hosts: dbservers
  tasks: [...]

- name: Puis les serveurs web
  hosts: webservers
  tasks: [...]
```

Les plays s'exécutent **dans l'ordre**, chacun sur ses hôtes : idéal pour orchestrer (DB avant app).

## 2. `ansible-playbook` — l'outil

```bash
ansible-playbook site.yml                              # exécution
ansible-playbook site.yml --syntax-check               # syntaxe seulement
ansible-playbook site.yml --check                      # dry-run (aucune modification)
ansible-playbook site.yml --check --diff               # + diff des fichiers
ansible-playbook site.yml -l web1                      # limiter aux hôtes
ansible-playbook site.yml -t config                    # seulement les tâches taguées "config"
ansible-playbook site.yml --skip-tags slow             # tout sauf "slow"
ansible-playbook site.yml --list-tasks --list-hosts --list-tags
ansible-playbook site.yml --start-at-task "Installer nginx"
ansible-playbook site.yml --step                       # confirmer chaque tâche
ansible-playbook site.yml -e "http_port=8080" -e @vars.yml
ansible-playbook site.yml -b -K                        # become + demande mot de passe sudo
ansible-playbook site.yml -f 20                        # 20 forks
ansible-playbook site.yml -vvv                         # debug de connexion
```

⚠️ `--check` n'est pas parfait : les tâches `command`/`shell` sont sautées (sauf `check_mode: false`), et les tâches dépendant du résultat d'une précédente peuvent échouer en simulation.

### Lire le récapitulatif

```
PLAY RECAP ***************************************************
web1 : ok=6  changed=2  unreachable=0  failed=0  skipped=1  rescued=0  ignored=0
```

Un playbook idempotent relancé doit afficher `changed=0`. C'est votre **test de santé** n°1.

## 3. Ce qu'on met dans une tâche (mots-clés courants)

| Mot-clé | Rôle |
|---|---|
| `name` | description (toujours en mettre un) |
| `become` / `become_user` | sudo / devenir un autre utilisateur |
| `when` | condition (module 06) |
| `loop` | itération (module 06) |
| `register` | stocker le résultat dans une variable |
| `notify` | appeler des handlers |
| `tags` | étiquettes de sélection |
| `vars` | variables locales à la tâche |
| `environment` | variables d'environnement |
| `delegate_to` | exécuter ailleurs (module 16) |
| `ignore_errors` / `failed_when` / `changed_when` | gestion des échecs/changements |
| `no_log: true` | masquer les données sensibles |
| `check_mode`, `diff` | contrôle simulation/diff par tâche |
| `retries` / `delay` / `until` | réessayer jusqu'à réussite |
| `async` / `poll` | tâches longues (module 12) |

## 4. Handlers

Un handler est une tâche déclenchée par `notify` **si et seulement si** la tâche notifiante a produit `changed`. Il s'exécute **une fois**, **à la fin** du play (ou à `meta: flush_handlers`), même si notifié 10 fois.

```yaml
tasks:
  - name: Déployer la configuration
    ansible.builtin.template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
      validate: nginx -t -c %s        # valider avant d'écraser !
    notify: Recharger nginx

  - name: Forcer l'exécution des handlers maintenant
    ansible.builtin.meta: flush_handlers

  - name: Vérifier que le site répond
    ansible.builtin.uri:
      url: http://localhost
```

* Plusieurs handlers peuvent partager un `listen: "web config changed"`.
* ⚠️ Si une tâche échoue après le `notify`, les handlers ne tournent pas (sauf `--force-handlers` ou `force_handlers: true`).

## 5. `register` et `debug`

```yaml
- name: Lire la version
  ansible.builtin.command: nginx -v
  register: nginx_version
  changed_when: false

- name: Afficher
  ansible.builtin.debug:
    msg: "{{ nginx_version.stderr }}"        # nginx -v écrit sur stderr !

- ansible.builtin.debug:
    var: nginx_version                        # structure complète : stdout, stderr, rc, changed…
```

Champs usuels d'un `register` : `rc`, `stdout`, `stdout_lines`, `stderr`, `changed`, `failed`, `skipped`, et pour une boucle `results`.

## 6. Découper les playbooks

| Mécanisme | Quand | Traitement |
|---|---|---|
| `import_playbook: autre.yml` | assembler des playbooks (`site.yml`) | **statique** |
| `import_tasks: fichier.yml` | réutiliser une liste de tâches | statique (parse au chargement), tags/when appliqués à toutes les tâches |
| `include_tasks: fichier.yml` | tâches choisies **dynamiquement** (boucle, nom de fichier variable) | dynamique (à l'exécution) |
| `import_role` / `include_role` | idem pour les rôles | statique / dynamique |

```yaml
# site.yml — le "point d'entrée" classique
- ansible.builtin.import_playbook: common.yml
- ansible.builtin.import_playbook: db.yml
- ansible.builtin.import_playbook: web.yml
```

Règle de pouce : **import** par défaut (prévisible, `--list-tasks` fonctionne) ; **include** si le contenu dépend d'une variable ou d'une boucle.

## 7. Style & qualité

```bash
yamllint .
ansible-lint                    # profil défini dans .ansible-lint
ansible-lint --fix              # corrige ce qui est automatisable
```

Bonnes pratiques :

1. Un `name:` explicite par play et par tâche (verbe à l'infinitif, ex. « Installer nginx »).
2. FQCN partout. Booléens `true`/`false`.
3. `state:` toujours explicite.
4. Valeurs de `mode:` **entre guillemets** (`"0644"`), sinon YAML les lit en octal/décimal.
5. Pas de `shell` quand un module existe.
6. Secrets : `no_log: true` + Vault.
7. Playbooks courts qui appellent des rôles.

## 8. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-multi-play.yml](demos/01-multi-play.yml) | plusieurs plays, ordre d'exécution |
| [demos/02-handlers.yml](demos/02-handlers.yml) | notify, flush_handlers, listen |
| [demos/03-register-debug.yml](demos/03-register-debug.yml) | register, rc/stdout, changed_when |
| [demos/04-site.yml](demos/04-site.yml) + `tasks/` | import_playbook / import_tasks / include_tasks |
| [demos/05-ordre-execution.yml](demos/05-ordre-execution.yml) | pre_tasks / tasks / post_tasks / handlers |

## 9. 🛠️ Labs

* [Lab 04 — Déployer nginx et une page d'accueil](labs/lab-04-nginx/README.md)

## ✅ Points clés

* Playbook = liste de plays = hosts + tasks. Les modules portent l'idempotence.
* Handlers : une fois, en fin de play, uniquement si `changed`.
* `--check --diff`, `--limit`, `--tags`, `--list-tasks` : indispensables avant de lancer en prod.
* `import_*` = statique, `include_*` = dynamique.

## ❓ Quiz

1. Quand un handler s'exécute-t-il ? *(à la fin du play, si notifié par une tâche `changed`)*
2. Pourquoi mettre `"0644"` entre guillemets ? *(éviter la conversion YAML en nombre)*
3. Différence `import_tasks` / `include_tasks` ? *(statique vs dynamique)*
4. Que fait `--start-at-task` ? *(reprend à une tâche nommée)*
