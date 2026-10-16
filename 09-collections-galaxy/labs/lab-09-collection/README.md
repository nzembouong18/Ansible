# Lab 09 — Créer, construire et consommer la collection `acme.tools`

⏱️ 1 h · 100 % local (aucun accès réseau nécessaire).

## 🎯 Objectif

Packager un rôle et un filtre dans une collection versionnée, la construire, l'installer dans un répertoire du projet, puis l'utiliser depuis un playbook.

## Énoncé

1. `ansible-galaxy collection init acme.tools --init-path collections-src`
2. Ajoutez :
   * un **filtre** `acme.tools.bytes_human` (octets → `"1.5 Go"`) avec `DOCUMENTATION`/`EXAMPLES` ;
   * un **rôle** `banner` (variable `banner_text`, dépose `/tmp/banner.txt` via template).
3. Complétez `galaxy.yml` (version `0.1.0`, licence, description) et `meta/runtime.yml` (`requires_ansible: ">=2.15.0"`).
4. Construisez : `ansible-galaxy collection build` → `acme-tools-0.1.0.tar.gz`.
5. Installez dans `./collections` : `ansible-galaxy collection install ... -p ./collections`.
6. Écrivez `use.yml` qui affiche `{{ 1610612736 | acme.tools.bytes_human }}` (→ `1.5 Go`) et applique le rôle.
7. Écrivez `requirements.yml` référençant l'archive locale (`type: file`) et réinstallez avec `-r`.
8. **Bonus** : ajoutez une montée de version `0.2.0` (nouveau paramètre `precision` du filtre) et vérifiez que `ansible-galaxy collection install --force` met à jour.

## Validation

```bash
ANSIBLE_COLLECTIONS_PATH=./collections ansible-doc -t filter acme.tools.bytes_human
ANSIBLE_COLLECTIONS_PATH=./collections ansible-playbook use.yml
cat /tmp/banner.txt
```

👉 Corrigé : [solution/](solution/) (script `run.sh` qui enchaîne build → install → use)
