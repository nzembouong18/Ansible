# Module 06 — Contrôle de flux : conditions, boucles, blocs, erreurs, tags

> **Durée** : 3 h · **Niveau** : intermédiaire

## 🎯 Objectifs

* Conditionner l'exécution : `when`, `failed_when`, `changed_when`.
* Itérer : `loop`, `loop_control`, `with_*` (legacy), `until`.
* Grouper et gérer les erreurs : `block` / `rescue` / `always`, `ignore_errors`, `any_errors_fatal`, `max_fail_percentage`.
* Organiser l'exécution avec les `tags` et `meta`.

---

## 1. Conditions : `when`

`when` est une **expression Jinja2 sans accolades**.

```yaml
- name: Seulement sur Debian/Ubuntu
  ansible.builtin.apt: { name: nginx, state: present }
  when: ansible_facts['os_family'] == 'Debian'

- name: Plusieurs conditions (ET implicite)
  ansible.builtin.debug: { msg: "gros serveur Ubuntu" }
  when:
    - ansible_facts['distribution'] == 'Ubuntu'
    - ansible_facts['memtotal_mb'] > 4096

- name: OU / NON / appartenance
  ansible.builtin.debug: { msg: ok }
  when: >
    (env == 'prod' or env == 'staging')
    and not skip_task | default(false) | bool
    and 'webservers' in group_names
```

Tests Jinja utiles : `is defined`, `is not defined`, `is none`, `is string`, `is number`, `is file` (côté contrôleur), `is match('regex')`, `is search(...)`, `is version('2.0', '>=')`, `is succeeded` / `is failed` / `is changed` / `is skipped` (sur un `register`).

```yaml
- ansible.builtin.command: grep -q foo /etc/hosts
  register: r
  failed_when: false
  changed_when: false
- ansible.builtin.debug: { msg: "foo présent" }
  when: r.rc == 0           # ou : when: r is succeeded
```

⚠️ **Pièges**

* `when: var` avec une chaîne `"false"` : avant ansible-core 2.19 la condition était **vraie** (chaîne non vide) ; depuis la 2.19 c'est une **erreur** (« Conditionals must have a boolean result »). Dans les deux cas, écrivez `when: var | bool`.
* Dans `when`, pas de `{{ }}`.
* `when` appliqué à un `include_tasks` conditionne l'**include**, pas son contenu (avec `import_tasks`, il est copié sur chaque tâche).

### `changed_when` / `failed_when`

```yaml
- name: Migrations de base
  ansible.builtin.command: /opt/app/migrate
  register: mig
  changed_when: "'Applied' in mig.stdout"
  failed_when:
    - mig.rc != 0
    - "'already up to date' not in mig.stdout"
```

## 2. Boucles

```yaml
# loop : la forme moderne
- name: Installer plusieurs paquets
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop: [git, curl, htop]

# MIEUX : beaucoup de modules acceptent une liste (1 appel au lieu de 3)
- ansible.builtin.package:
    name: [git, curl, htop]
    state: present

# Liste de dictionnaires
- ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups | default(omit) }}"
    state: present
  loop:
    - { name: alice, groups: sudo }
    - { name: bob }

# Dictionnaire -> liste
- ansible.builtin.debug:
    msg: "{{ item.key }} = {{ item.value }}"
  loop: "{{ db | dict2items }}"

# Contrôle de la boucle
  loop_control:
    label: "{{ item.name }}"      # sortie plus lisible (et masque les secrets)
    loop_var: u                   # renomme 'item' (obligatoire dans les boucles imbriquées / includes)
    index_var: idx                # compteur 0..n
    pause: 2                      # pause entre itérations
    extended: true                # ansible_loop.first / .last / .index / .length
```

**Autres sources de boucle**

| Besoin | Syntaxe |
|---|---|
| Plage | `loop: "{{ range(1, 6) \| list }}"` |
| Produit cartésien | `loop: "{{ ['a','b'] \| product([1,2]) \| list }}"` |
| Fichiers | `loop: "{{ lookup('fileglob', 'files/*.conf', wantlist=True) }}"` |
| Sous-éléments | `loop: "{{ users \| subelements('keys') }}"` |
| Résultats d'une boucle précédente | `loop: "{{ resultat.results }}"` |

**Réessayer jusqu'au succès** (attente d'un service) :

```yaml
- ansible.builtin.uri: { url: "http://localhost:8080/health" }
  register: health
  until: health.status == 200
  retries: 12
  delay: 5
```

`with_items`, `with_dict`, `with_fileglob`… sont l'ancienne syntaxe : encore valide mais **préférez `loop`**.

## 3. Blocs : `block` / `rescue` / `always`

Un `block` groupe des tâches pour leur appliquer ensemble `when`, `become`, `tags`, `vars`… et pour gérer les erreurs (équivalent *try/catch/finally*).

```yaml
- name: Déploiement avec retour arrière
  block:
    - name: Déployer la nouvelle version
      ansible.builtin.copy: { src: app-v2.jar, dest: /opt/app/app.jar }
    - name: Redémarrer
      ansible.builtin.service: { name: app, state: restarted }
    - name: Vérifier la santé
      ansible.builtin.uri: { url: "http://localhost:8080/health" }
      retries: 5
      delay: 3
      register: h
      until: h.status == 200
  rescue:                               # exécuté si une tâche du block échoue
    - name: Restaurer l'ancienne version
      ansible.builtin.copy: { src: app-v1.jar, dest: /opt/app/app.jar }
    - ansible.builtin.service: { name: app, state: restarted }
    - ansible.builtin.fail: { msg: "Déploiement échoué, rollback effectué" }
  always:                               # toujours exécuté
    - ansible.builtin.debug: { msg: "Fin de la tentative de déploiement" }
  when: deploy_enabled | bool
  become: true
```

Variables spéciales dans `rescue` : `ansible_failed_task`, `ansible_failed_result`.

## 4. Gestion des erreurs

| Mécanisme | Effet |
|---|---|
| `ignore_errors: true` | l'échec est affiché mais n'arrête pas (les erreurs « unreachable » ne sont pas ignorées → `ignore_unreachable: true`) |
| `failed_when:` | redéfinit ce qu'est un échec |
| `any_errors_fatal: true` (play) | si un hôte échoue, **tous** s'arrêtent |
| `max_fail_percentage: 20` (play) | abandonne si > 20 % des hôtes échouent |
| `force_handlers: true` | exécute les handlers même après un échec |
| `ansible.builtin.fail` / `assert` | échouer volontairement avec un message |
| `meta: end_play`, `end_host`, `clear_host_errors` | contrôle manuel |

`assert` pour valider les prérequis **avant** d'agir :

```yaml
- ansible.builtin.assert:
    that:
      - ansible_facts['memtotal_mb'] >= 2048
      - app_version is defined
      - http_port | int > 1024
    fail_msg: "Prérequis non satisfaits"
    success_msg: "Prérequis OK"
```

## 5. Tags

```yaml
- name: Installer nginx
  ansible.builtin.package: { name: nginx }
  tags: [install, web]

- name: Config
  ansible.builtin.template: { src: a.j2, dest: /etc/a }
  tags: config
```

```bash
ansible-playbook site.yml --tags config,web
ansible-playbook site.yml --skip-tags install
ansible-playbook site.yml --list-tags
```

Tags spéciaux : `always` (toujours exécuté sauf `--skip-tags always`), `never` (seulement si demandé explicitement), `tagged`, `untagged`, `all`.
Un tag posé sur un `play`/`block`/`import_*`/rôle s'applique à tout son contenu.

## 6. Autres outils de flux

| Outil | Usage |
|---|---|
| `ansible.builtin.pause` | pause / confirmation humaine (`prompt:`) |
| `ansible.builtin.wait_for` | attendre un port, un fichier, un texte |
| `ansible.builtin.wait_for_connection` | attendre le retour SSH (après reboot) |
| `ansible.builtin.meta: flush_handlers` | exécuter les handlers maintenant |
| `ansible.builtin.meta: end_play` | arrêter proprement le play |
| `run_once: true` | une seule exécution pour tout le groupe |
| `delegate_to` | exécuter sur un autre hôte (module 16) |
| `check_mode: false` | exécuter la tâche même en `--check` |

## 7. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-when.yml](demos/01-when.yml) | conditions simples, combinées, pièges bool |
| [demos/02-loops.yml](demos/02-loops.yml) | loop, dict2items, loop_control, until |
| [demos/03-block-rescue.yml](demos/03-block-rescue.yml) | try/catch/finally |
| [demos/04-errors.yml](demos/04-errors.yml) | failed_when, assert, ignore_errors |
| [demos/05-tags.yml](demos/05-tags.yml) | tags, always, never |

## 8. 🛠️ Labs

* [Lab 06 — Playbook résilient multi-OS avec rollback](labs/lab-06-flux/README.md)

## ✅ Points clés

* `when` sans `{{ }}` ; `| bool` pour les chaînes.
* Préférez passer une **liste** au module plutôt que boucler.
* `block/rescue/always` pour des rollbacks propres ; `assert` pour les prérequis.
* `tags` pour exécuter une partie ; `never` pour les tâches dangereuses.

## ❓ Quiz

1. `when: "{{ x }} == 1"` est-il correct ? *(Non, pas d'accolades)*
2. Quand `always` s'exécute-t-il ? *(Toujours, succès ou échec du block)*
3. Comment renommer la variable `item` ? *(`loop_control.loop_var`)*
4. Quel tag force l'exécution même avec `--tags autre` ? *(`always`)*
