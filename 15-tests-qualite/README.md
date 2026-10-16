# Module 15 — Qualité, tests et intégration continue

> **Durée** : 3 h · **Niveau** : expert

## 🎯 Objectifs

* Mettre en place la **pyramide de tests** de l'automatisation.
* Utiliser `yamllint`, `ansible-lint`, `--syntax-check`, `--check --diff`.
* Tester un rôle avec **Molecule** (create → converge → idempotence → verify → destroy).
* Brancher le tout dans une **CI** (GitHub Actions) et en **pre-commit**.

---

## 1. La pyramide de tests Ansible

```
             ▲  coût / durée / réalisme
             │
   ┌───────────────────────┐
   │ Tests en pré-production│  vrai environnement, smoke tests, canari
   ├───────────────────────┤
   │ Molecule (conteneurs/VM)│ converge + idempotence + verify
   ├───────────────────────┤
   │ check mode + diff      │  simulation sur de vraies cibles
   ├───────────────────────┤
   │ syntax-check, lint     │  secondes, sans cible
   └───────────────────────┘
```

Règle d'or : **plus un test est bas dans la pyramide, plus on en écrit**, et il tourne à chaque commit.

## 2. Analyse statique

### yamllint

```bash
yamllint .                       # règles dans .yamllint
```

### ansible-lint

```bash
ansible-lint                     # profil défini dans .ansible-lint
ansible-lint --profile production playbooks/ roles/
ansible-lint --fix               # corrections automatiques sûres
ansible-lint -L                  # liste des règles
```

Profils (du plus tolérant au plus strict) : `min` → `basic` → `moderate` → `safety` → `shared` → `production`.

Règles fréquentes : `fqcn`, `name[casing]`, `no-changed-when`, `command-instead-of-module`, `risky-file-permissions`, `no-handler`, `yaml[...]`, `package-latest`, `ignore-errors`, `no-free-form`, `var-naming`.

Exceptions : `# noqa: nom-de-règle` sur la ligne, ou `skip_list`/`warn_list` dans `.ansible-lint`. Chaque exception doit être **justifiée** par un commentaire.

Voir la démo [demos/mauvais.yml](demos/mauvais.yml) → [corrige.yml](demos/corrige.yml) et `./demos/lint-tour.sh`.

### Contrôles Ansible natifs

```bash
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --list-tasks --list-hosts
ansible-inventory -i inv --graph
ansible-playbook site.yml --check --diff     # sur une vraie cible de test
```

## 3. Molecule

Molecule orchestre des environnements jetables pour tester un **rôle** (ou une collection).

```
roles/motd/molecule/
├── default/                  # un scénario
│   ├── molecule.yml          # driver, plateformes, provisioner, verifier, séquence
│   ├── converge.yml          # applique le rôle (le "play" testé)
│   ├── verify.yml            # assertions
│   ├── prepare.yml           # (optionnel) prérequis de la cible
│   └── cleanup.yml           # (optionnel)
└── docker/                   # autre scénario : conteneurs Ubuntu + Rocky
```

Séquence standard : `dependency → create → prepare → converge → idempotence → verify → cleanup → destroy`.

```bash
molecule test                 # tout le cycle
molecule converge             # applique (itération rapide)
molecule verify               # relance seulement les tests
molecule login                # shell dans l'instance
molecule destroy
molecule test -s docker       # un autre scénario
```

* **`idempotence`** : rejoue `converge` et échoue s'il y a le moindre `changed`. C'est le test le plus précieux.
* **Drivers** : `docker`/`podman` (via `molecule-plugins`), `vagrant`, `default` (machines déjà existantes, ex. local — utilisé dans ce lab).
* **Verifier** : playbook Ansible (`verify.yml`, recommandé : même langage) ou `testinfra` (pytest).
* **Matrice** : plusieurs plateformes (Ubuntu, Rocky), plusieurs versions d'Ansible, via variables d'environnement.

### Exemple de `verify.yml`

```yaml
- hosts: all
  gather_facts: false
  tasks:
    - ansible.builtin.service_facts:
    - ansible.builtin.assert:
        that: ansible_facts.services['nginx.service'].state == 'running'
    - ansible.builtin.uri:
        url: http://localhost
        status_code: 200
```

## 4. Tests pour collections

`ansible-test sanity|units|integration` (dans `ansible_collections/<ns>/<col>/`) : conformité de style, tests unitaires des plugins, tests d'intégration dans des conteneurs.

## 5. Intégration continue

Fichier fourni : [.github/workflows/ci.yml](../.github/workflows/ci.yml) — lint puis [tests/run-checks.sh](../tests/run-checks.sh).

Pipeline recommandé pour un dépôt Ansible :

| Étape | Déclencheur | Outils |
|---|---|---|
| 1. Qualité | chaque commit | yamllint, ansible-lint, syntax-check |
| 2. Tests de rôles | chaque PR | Molecule (matrice OS) |
| 3. Dry-run en préprod | merge | `--check --diff` via AWX/CI |
| 4. Déploiement préprod | merge sur main | playbook réel + smoke tests |
| 5. Promotion prod | tag / approbation manuelle | AWX workflow avec approbation |

Bonnes pratiques CI : cache pip, versions d'`ansible-core` épinglées, secrets Vault via secrets du CI, rapports JUnit (callback `junit` : `ANSIBLE_CALLBACKS_ENABLED=junit JUNIT_OUTPUT_DIR=./reports`) et conservation des artefacts.

### pre-commit

[.pre-commit-config.yaml](../.pre-commit-config.yaml) : yamllint + ansible-lint + détection de clés privées + contrôle que les `vault.yml` sont chiffrés.

```bash
pip install pre-commit && pre-commit install && pre-commit run --all-files
```

## 6. Que tester dans un rôle ?

1. Il **converge** sans erreur sur chaque OS supporté.
2. Il est **idempotent**.
3. Le **résultat** est correct (fichiers, services actifs, ports ouverts, réponses HTTP).
4. Les **variables** principales produisent l'effet attendu (scénarios dédiés).
5. Les **cas d'erreur** (paramètre invalide) échouent proprement (`assert`, `argument_specs`).

## 7. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/lint-tour.sh](demos/lint-tour.sh) | yamllint, ansible-lint avant/après |
| [labs/lab-15-molecule/solution/roles/motd/molecule/](labs/lab-15-molecule/solution/roles/motd/molecule) | 2 scénarios Molecule : `default` (local) et `docker` (Ubuntu + Rocky) |

## 8. 🛠️ Labs

* [Lab 15 — Tester le rôle `motd` avec Molecule et le brancher à la CI](labs/lab-15-molecule/README.md)

## ✅ Points clés

* Lint → syntax → check → Molecule → préprod : chaque niveau attrape des erreurs différentes.
* L'**idempotence** est un test à part entière.
* CI + pre-commit = la qualité devient automatique.

## ❓ Quiz

1. Quelle étape de Molecule vérifie l'idempotence ? *(`idempotence` : second converge sans `changed`)*
2. Qu'est-ce qu'un profil ansible-lint ? *(niveau de strictesse : min … production)*
3. Pourquoi `--check` ne suffit-il pas ? *(certains modules ne simulent pas ; dépendances entre tâches)*
4. Où lancer `ansible-test` ? *(dans une collection)*
