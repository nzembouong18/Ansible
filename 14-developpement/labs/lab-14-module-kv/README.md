# Lab 14 — Écrire un module Ansible : `config_kv`

⏱️ 2 h · 100 % local · Python 3.

## 🎯 Objectif

Développer un vrai module **idempotent**, compatible `--check` et `--diff`, documenté, avec des **tests unitaires** de sa logique métier.

## Cahier des charges

Module `config_kv` : gère des paires `clé=valeur` dans un fichier de configuration.

| Paramètre | Type | Détails |
|---|---|---|
| `path` | path, requis | fichier (créé si absent et `create: true`) |
| `settings` | dict, requis | `{clé: valeur}` à imposer |
| `state` | str | `present` (défaut) ou `absent` (retire les clés listées) |
| `create` | bool | défaut `true` |
| `backup` | bool | sauvegarde si modification |

Comportement :

* conserve les commentaires et lignes inconnues, l'ordre existant ; ajoute les nouvelles clés à la fin ;
* ne modifie rien (donc `changed=false`) si l'état est déjà conforme ;
* en `check_mode`, calcule le `diff` sans écrire ;
* retourne `changed`, `diff`, `added`, `updated`, `removed` (listes de clés) ;
* `fail_json` avec message clair si une clé contient `=` ou un espace.

Séparez la **logique pure** (`apply_settings(lines, settings, state) -> (new_lines, added, updated, removed)`) de l'accès fichier : elle est testée par `pytest`.

## Étapes

1. `library/config_kv.py` (DOCUMENTATION / EXAMPLES / RETURN complets).
2. `tests/test_config_kv.py` (≥ 6 cas : ajout, mise à jour, idempotence, suppression, commentaires conservés, clé invalide).
3. `test.yml` (création + appel idempotent vérifié par `assert`) et `remove.yml` (mise à jour puis suppression) ; testez aussi `--check --diff`.
4. `ansible-doc -M library config_kv` doit afficher la documentation.

## Validation

```bash
pytest -q tests
ansible-doc -M library config_kv | head
ansible-playbook -i localhost, -c local test.yml
ansible-playbook -i localhost, -c local test.yml            # 2e passage : changed=0
ansible-playbook -i localhost, -c local test.yml --check --diff
```

👉 Corrigé : [solution/](solution/)
