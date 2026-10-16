# Module 01 — Fondamentaux d'Ansible

> **Durée** : 2 h (cours 1 h, labo 1 h) · **Niveau** : débutant

## 🎯 Objectifs

* Expliquer ce qu'est l'*Infrastructure as Code* et pourquoi Ansible.
* Décrire l'architecture : control node, managed nodes, inventaire, modules, playbooks.
* Comprendre **idempotence**, **déclaratif vs impératif**, **agentless**.
* Installer Ansible et configurer `ansible.cfg`.
* Écrire et lancer son premier playbook.

---

## 1. Pourquoi automatiser ?

| Sans automatisation | Avec Ansible |
|---|---|
| Procédures Word + SSH à la main | Procédures **exécutables**, versionnées dans Git |
| « Ça marche sur le serveur 1 mais pas le 2 » (*snowflake servers*) | Serveurs **convergents** vers le même état |
| Déploiement = stress du vendredi soir | Déploiement **répétable**, testable, relu en *pull request* |
| Documentation périmée | Le code **est** la documentation |

**Infrastructure as Code (IaC)** : décrire l'infrastructure et sa configuration dans des fichiers texte, versionnés, relus, testés.

### Ansible vs les autres

| Outil | Modèle | Agent | Langage | Usage principal |
|---|---|---|---|---|
| **Ansible** | push (SSH/WinRM) | non | YAML + Jinja2 | configuration, orchestration, déploiement |
| Puppet / Chef | pull | oui | DSL Ruby | configuration continue |
| Salt | push/pull | optionnel | YAML + Jinja | configuration à grande échelle |
| Terraform / OpenTofu | déclaratif + état | non | HCL | **provisionnement** d'infrastructure |
| Shell | impératif | non | bash | scripts ponctuels |

> 💡 Terraform *crée* les machines, Ansible *les configure*. Les deux se complètent.

## 2. Architecture

```
                 ┌──────────────────────────────────────────────┐
                 │               CONTROL NODE                   │
                 │  ansible / ansible-playbook                  │
                 │  ├─ ansible.cfg  (configuration)             │
                 │  ├─ inventaire   (QUI ? : hôtes & groupes)   │
                 │  ├─ playbooks    (QUOI ? : tâches)           │
                 │  └─ collections / rôles / plugins            │
                 └───────────────┬──────────────────────────────┘
                                 │ SSH (Linux) / WinRM (Windows) / API
              ┌──────────────────┼───────────────────┐
              ▼                  ▼                   ▼
         managed node 1    managed node 2     managed node N
         (Python requis    (aucun agent,      (modules copiés,
          pour Linux)       aucun démon)       exécutés puis supprimés)
```

**Vocabulaire**

| Terme | Définition |
|---|---|
| **Control node** | Machine d'où l'on lance Ansible (Linux/macOS/WSL, pas Windows natif) |
| **Managed node** | Machine administrée (cible) |
| **Inventaire** | Liste des hôtes et groupes |
| **Module** | Unité de travail (`apt`, `copy`, `service`…) — ce que fait réellement Ansible |
| **Task** | Appel d'un module avec ses paramètres |
| **Play** | Association « ces hôtes » + « ces tâches » |
| **Playbook** | Fichier YAML contenant un ou plusieurs plays |
| **Role** | Ensemble réutilisable de tâches/variables/templates (module 08) |
| **Collection** | Paquet distribuable : modules, rôles, plugins (module 09) |
| **Facts** | Informations collectées sur les hôtes (OS, IP, mémoire…) |
| **Handler** | Tâche déclenchée seulement sur notification (ex. redémarrer un service) |

### Ce qui se passe quand on lance une tâche

1. Ansible lit l'inventaire et se connecte en SSH.
2. Il génère le code Python du module, le copie dans `~/.ansible/tmp/` (ou l'envoie via *pipelining*).
3. Il l'exécute avec l'interpréteur Python distant.
4. Le module renvoie du **JSON** (`changed`, `failed`, résultat…).
5. Ansible supprime le fichier temporaire et affiche le résultat.

## 3. Idempotence et déclaratif

Un module décrit **l'état désiré**, pas les actions :

```yaml
- ansible.builtin.package:
    name: nginx
    state: present      # « nginx doit être installé »
```

* 1ʳᵉ exécution → installe nginx → `changed`
* 2ᵉ exécution → déjà présent → `ok` (rien n'est fait)

C'est l'**idempotence** : appliquer N fois = appliquer 1 fois. Vous pouvez relancer un playbook sans peur, il ne corrige que les écarts (*drift*).

⚠️ **Piège** : `command`, `shell`, `raw` ne sont pas idempotents par nature. Utilisez `creates:`, `removes:`, `changed_when:` ou, mieux, un vrai module.

Statuts d'une tâche : `ok` (rien à faire), `changed` (modifié), `failed`, `skipped` (condition fausse), `unreachable` (SSH KO), `rescued`, `ignored`.

## 4. Installation

### Via pip (recommandé : version contrôlée, venv)

```bash
python3 -m venv ~/venv-ansible
source ~/venv-ansible/bin/activate
pip install --upgrade pip
pip install ansible-core ansible-lint yamllint     # ansible-core = moteur seul
# pip install ansible                               # = ansible-core + ~100 collections
ansible --version
```

### Via paquets

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y ansible-core
# RHEL/Rocky/Alma
sudo dnf install -y ansible-core
# macOS
brew install ansible
```

### ansible vs ansible-core

| Paquet | Contenu |
|---|---|
| `ansible-core` | moteur + modules `ansible.builtin` (minimal) |
| `ansible` | `ansible-core` + collections communautaires (`community.general`, `amazon.aws`, …) |

### Prérequis côté cibles

* Linux : SSH + **Python 3** (sinon utiliser le module `raw` pour l'installer).
* Windows : PowerShell 5.1+, WinRM ou SSH (module 17).
* Un utilisateur avec accès SSH par clé et `sudo`.

## 5. Configuration : `ansible.cfg`

Ordre de recherche (le premier trouvé gagne, **pas de fusion**) :

1. variable `ANSIBLE_CONFIG`
2. `./ansible.cfg` (répertoire courant)
3. `~/.ansible.cfg`
4. `/etc/ansible/ansible.cfg`

```ini
[defaults]
inventory          = ./inventory/hosts.yml
remote_user        = ansible
host_key_checking  = False        # labo seulement !
stdout_callback    = yaml         # sortie lisible
roles_path         = ./roles
forks              = 10

[privilege_escalation]
become = False

[ssh_connection]
pipelining = True                 # moins d'allers-retours SSH → plus rapide
```

Commandes de diagnostic :

```bash
ansible --version             # config file utilisé, version de Python, chemins
ansible-config dump --only-changed   # ce qui diffère des valeurs par défaut
ansible-config list           # toute la doc des paramètres
ansible-doc -l | head         # liste des modules
ansible-doc ansible.builtin.copy     # documentation d'un module (hors-ligne !)
```

> 💡 `ansible-doc <module>` est votre meilleur ami : exemples, paramètres, valeurs de retour — sans connexion Internet.

## 6. Premier contact : YAML en 5 minutes

```yaml
---                       # début de document (optionnel mais conventionnel)
texte: bonjour            # chaîne
nombre: 42
booleen: true             # préférez true/false à yes/no
liste:
  - pomme
  - poire
liste_inline: [a, b, c]
dictionnaire:
  cle1: valeur1
  cle2: valeur2
multiligne: |             # | conserve les retours à la ligne
  ligne 1
  ligne 2
replie: >                 # > replie en une seule ligne
  ceci est
  une seule ligne
```

Règles : **indentation = 2 espaces, jamais de tabulation** ; `:` suivi d'un espace ; les chaînes commençant par `{{` ou contenant `: ` doivent être entre guillemets.

## 7. 🧪 Démos

| Démo | Fichier | Ce qu'elle montre |
|---|---|---|
| 1 | [demos/01-premier-playbook.yml](demos/01-premier-playbook.yml) | structure minimale, `debug`, `copy`, `file` |
| 2 | [demos/02-idempotence.yml](demos/02-idempotence.yml) | `changed` puis `ok` ; `command` vs module |
| 3 | [demos/03-check-diff.yml](demos/03-check-diff.yml) | `--check` et `--diff` (mode « dry run ») |

À chaque démo : lancer **deux fois** et observer la différence de sortie.

```bash
ansible-playbook 01-fondamentaux/demos/01-premier-playbook.yml
ansible-playbook 01-fondamentaux/demos/02-idempotence.yml
ansible-playbook 01-fondamentaux/demos/03-check-diff.yml --check --diff
```

## 8. 🛠️ Labs

* [Lab 01 — Premier playbook sur le labo](labs/lab-01-premier-playbook/README.md) (corrigé inclus)

## ✅ Points clés

* Ansible = **agentless**, **push**, **YAML**, **idempotent**.
* Inventaire (quoi/qui) + module (comment) + playbook (orchestration).
* `ansible-doc`, `--check`, `--diff`, `-v` sont vos outils de base.
* Préférez toujours un module dédié à `shell`/`command`.

## ❓ Quiz

1. Quel protocole utilise Ansible pour administrer un serveur Linux ? *(SSH)*
2. Faut-il installer un agent sur les cibles ? *(Non, mais Python oui)*
3. Que signifie « idempotent » ? *(Le résultat est identique après 1 ou N exécutions)*
4. Quelle option simule sans modifier ? *(`--check`)*
5. Différence entre `ansible` et `ansible-core` ? *(core = moteur + builtin ; ansible = + collections)*
