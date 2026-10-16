# Module 12 — Débogage, performance et exécution avancée

> **Durée** : 2 h 30 · **Niveau** : avancé

## 🎯 Objectifs

* Diagnostiquer rapidement un playbook en échec (verbosité, `debug`, `debugger`, `--step`, logs).
* Mesurer (`profile_tasks`, `timer`) puis optimiser (forks, pipelining, facts, stratégies, async).
* Maîtriser `async`/`poll`, `serial`, `throttle`, `strategy`.

---

## 1. Débogage

### Niveaux de verbosité

| Option | Affiche |
|---|---|
| (aucune) | statuts |
| `-v` | résultats des modules (stdout, rc…) |
| `-vv` | + fichier/ligne de la tâche, entrées |
| `-vvv` | + commandes SSH, détail de connexion |
| `-vvvv` | + plugin de connexion, scripts exécutés |
| `-vvvvv` | + débogage SSH/WinRM complet |

### Outils

```bash
ansible-playbook site.yml --syntax-check          # YAML/structure
ansible-playbook site.yml --list-tasks --list-hosts
ansible-playbook site.yml --check --diff          # simulation
ansible-playbook site.yml --step                  # tâche par tâche
ansible-playbook site.yml --start-at-task "X"
ansible-playbook site.yml -l web1 -vvv            # un seul hôte, très verbeux
ansible-inventory --host web1                     # toutes les variables d'un hôte
ansible web1 -m debug -a "var=hostvars[inventory_hostname]"
ANSIBLE_DEBUG=1 ansible-playbook ...              # debug interne d'Ansible
ansible-config dump --only-changed                # configuration effective
```

```ini
# ansible.cfg
[defaults]
log_path = ./ansible.log
stdout_callback = default
result_format = yaml                   # (l'ancien callback 'yaml' n'existe plus)
callbacks_enabled = ansible.builtin.timer, ansible.posix.profile_tasks, ansible.posix.profile_roles
display_skipped_hosts = false
```

### Le `debugger`

```yaml
- name: Tâche à inspecter
  ansible.builtin.command: /opt/app/migrate
  debugger: on_failed        # always | never | on_failed | on_unreachable | on_skipped
```

Prompt interactif : `p task`, `p task.args`, `p task_vars`, `p result._result`, `task.args['x']='y'`, `update_task`, `redo`, `continue`, `quit`.

### Erreurs classiques

| Message | Piste |
|---|---|
| `Syntax Error while loading YAML` | indentation / `:` / guillemets (voir ligne indiquée) |
| `'x' is undefined` | variable absente → `default()`, vérifier la précédence (`-e`, `ansible-inventory --host`) |
| `Failed to connect to the host via ssh` | clé, utilisateur, `ansible_host`, pare-feu → `-vvv` |
| `Missing sudo password` | `become` sans `NOPASSWD` → `-K` ou configurer sudoers |
| `couldn't resolve module/action` | collection absente / faute de FQCN |
| `MODULE FAILURE ... python` | mauvais interpréteur → `ansible_python_interpreter` |
| `Permission denied` sur fichier | `become` manquant, ACL, SELinux |
| `changed` perpétuel | tâche non idempotente (command sans `creates`, template avec date…) |

## 2. Mesurer avant d'optimiser

```ini
callbacks_enabled = ansible.builtin.timer, ansible.posix.profile_tasks
```

`profile_tasks` classe les tâches par durée (top 20) ; `timer` donne le temps total. **Optimisez ce qui est mesuré, pas ce qu'on suppose.**

## 3. Leviers de performance

| Levier | Effet | Réglage |
|---|---|---|
| **forks** | hôtes traités en parallèle (défaut 5) | `forks = 50` / `-f 50` |
| **pipelining** | moins d'allers-retours SSH (nécessite `requiretty` désactivé) | `[ssh_connection] pipelining = True` |
| **ControlPersist** | réutilise la connexion SSH | `ssh_args = -o ControlMaster=auto -o ControlPersist=60s` |
| **gather_facts** | 1–3 s par hôte | `gather_facts: false`, `gather_subset`, cache |
| **fact caching** | évite de recollecter | `fact_caching = jsonfile / redis` + `gathering = smart` |
| **listes de paquets** | 1 appel au lieu de N | `name: [a, b, c]` |
| **strategy: free** | chaque hôte avance à son rythme | `strategy: free` |
| **async** | lancer plusieurs tâches longues en parallèle | `async` + `poll: 0` |
| **modules vs shell** | moins de processus | modules natifs |
| **moins de boucles** | chaque itération = un aller-retour | filtres Jinja / modules acceptant des listes |
| **`--limit`, `--tags`** | exécuter moins | |
| **Mitogen** | accélérateur tiers (peu maintenu) | à éviter en production récente |
| **ansible-pull / AWX** | décentraliser l'exécution | modules 16/18 |

### Cache de facts

```ini
[defaults]
gathering = smart
fact_caching = ansible.builtin.jsonfile      # ou ansible.builtin.redis / memory
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
```

### Stratégies

| Stratégie | Comportement |
|---|---|
| `linear` (défaut) | tous les hôtes terminent la tâche N avant de passer à N+1 |
| `free` | chaque hôte déroule ses tâches sans attendre les autres |
| `host_pinned` | comme free mais un worker par hôte |
| `debug` | linear + debugger |

### `serial`, `throttle`, `run_once`, `max_fail_percentage`

```yaml
- hosts: webservers
  serial: [1, "25%", "100%"]      # canari (1) puis 25 % puis le reste
  max_fail_percentage: 10         # stoppe si > 10 % échouent dans un lot
  tasks:
    - ansible.builtin.command: /opt/app/restart
      throttle: 2                 # au plus 2 hôtes simultanément sur CETTE tâche
    - ansible.builtin.command: /opt/app/migrate
      run_once: true              # une fois pour tout le groupe
```

## 4. Asynchrone

```yaml
- name: Sauvegarde longue
  ansible.builtin.command: /usr/local/bin/backup.sh
  async: 3600       # durée max (s)
  poll: 30          # vérifie toutes les 30 s (évite les timeouts SSH) ; poll: 0 = ne pas attendre

- name: Lancer sans attendre puis attendre ensemble
  ansible.builtin.command: "{{ item }}"
  async: 600
  poll: 0
  register: jobs
  loop: [/opt/a.sh, /opt/b.sh]

- ansible.builtin.async_status:
    jid: "{{ item.ansible_job_id }}"
  register: res
  until: res.finished
  retries: 60
  delay: 10
  loop: "{{ jobs.results }}"
```

⚠️ `async` n'est pas compatible avec `--check` pour `command`; l'idempotence reste votre responsabilité.

## 5. Bonnes pratiques de robustesse

* `timeout:` par tâche (2.10+) pour éviter les blocages.
* `ansible_ssh_retries`, `ConnectTimeout`, `ServerAliveInterval` pour réseaux instables.
* `any_errors_fatal` pour des opérations coordonnées.
* Toujours tester sur un sous-ensemble (`--limit`, `serial`) avant « tout le parc ».

## 6. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-debug-outils.yml](demos/01-debug-outils.yml) | `debug`, verbosité, `debugger` |
| [demos/02-async.yml](demos/02-async.yml) | `async` + `async_status` |
| [demos/03-strategies.yml](demos/03-strategies.yml) + [inventory-multi.ini](demos/inventory-multi.ini) | linear/free, forks, throttle (6 workers locaux) |
| [demos/04-facts-cache.yml](demos/04-facts-cache.yml) | cache de facts jsonfile |

Mesures obtenues sur une machine de test (6 hôtes locaux) : `linear` 11 s, `free` 9 s, `-f 2` 14 s.

## 7. 🛠️ Labs

* [Lab 12 — Réduire de moitié le temps d'un playbook lent](labs/lab-12-optimisation/README.md)

## ✅ Points clés

* `-v/-vvv`, `--check --diff`, `--step`, `debugger`, `ansible-inventory --host` : trousse de dépannage.
* Mesurez (`profile_tasks`), puis `forks`/`pipelining`/facts/stratégie/async.
* `serial` + `max_fail_percentage` pour des déploiements prudents.

## ❓ Quiz

1. Que fait `poll: 0` ? *(lance la tâche sans attendre)*
2. Quel réglage évite de recollecter les facts ? *(cache de facts + `gathering = smart`)*
3. Différence `linear` / `free` ? *(synchronisation par tâche ou non)*
4. Comment limiter une tâche à 2 hôtes simultanés ? *(`throttle: 2`)*
