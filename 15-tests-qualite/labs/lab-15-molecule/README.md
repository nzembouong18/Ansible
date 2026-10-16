# Lab 15 — Tester un rôle avec Molecule et le brancher à la CI

⏱️ 1 h 30 · Scénario `default` : 100 % local. Scénario `docker` : nécessite Docker (optionnel).

## 🎯 Objectif

Prendre le rôle `motd` (module 08), écrire sa suite de tests Molecule, constater qu'elle détecte un défaut d'idempotence, puis la brancher à la CI.

## Énoncé

1. Dans `roles/motd/`, créez le scénario `molecule/default` (driver `default`, `managed: false`, inventaire local) avec `converge.yml`, `verify.yml` (contenu du fichier + mode `0644`) et `cleanup.yml`.
2. Lancez `molecule test`. Tout doit passer.
3. **Cassez volontairement** l'idempotence : dans `templates/motd.j2`, ajoutez `{{ ansible_date_time.epoch }}` (valeur différente à chaque exécution). Relancez : l'étape `idempotence` doit **échouer**. Corrigez.
4. Ajoutez un test de variable : un second converge avec `motd_show_facts: false` et un `verify` qui contrôle l'absence de la ligne `OS`.
5. (Docker) Créez le scénario `docker` avec Ubuntu 24.04 et Rocky 9 ; `molecule test -s docker`.
6. Reprenez `.github/workflows/ci.yml` du dépôt : ajoutez une étape `molecule test` pour ce rôle.

## Validation

```bash
cd roles/motd
molecule test                 # 5 étapes vertes : syntax, converge, idempotence, verify, cleanup
molecule test -s docker       # (optionnel)
```

👉 Corrigé : [solution/roles/motd](solution/roles/motd) (scénarios `default` et `docker`).
