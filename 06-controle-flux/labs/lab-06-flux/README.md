# Lab 06 — Déploiement résilient avec rollback

⏱️ 1 h 15 · Fonctionne sur `localhost` **ou** sur le labo (`webservers`).

## 🎯 Objectif

Simuler le déploiement d'une « release » (un fichier `/tmp/app/release.txt` + lien symbolique `current`) avec **prérequis, boucle, rollback et nettoyage**.

## Énoncé

Écrivez `deploy.yml` :

1. **Prérequis** (`assert`) : `release` est défini et correspond à `^v[0-9]+\.[0-9]+$` ; au moins 512 Mo de RAM.
2. **Préparation** : crée `/tmp/app/releases/<release>/` ; pour chaque fichier de la liste `app_files` (`loop`, avec `loop_control.label`), crée un fichier contenant son nom et la release.
3. **Bloc de déploiement** (`block`) :
   * sauvegarde l'ancienne cible du lien `current` (`stat` + `register`) ;
   * bascule le lien `/tmp/app/current` vers la nouvelle release ;
   * « health check » : `command: grep -q {{ release }} /tmp/app/current/app.txt` ; **échoue si** `release == 'v9.9'` (pour simuler un incident, utilisez `failed_when`).
4. **`rescue`** : remet le lien sur l'ancienne release (si elle existait) et échoue avec un message clair (`fail`).
5. **`always`** : écrit une ligne dans `/tmp/app/deploy.log` (`lineinfile`, `create: true`) avec le résultat.
6. Une tâche `tags: [never, purge]` supprime `/tmp/app` (à lancer avec `--tags purge`).

## Validation

```bash
ansible-playbook deploy.yml -e release=v1.0           # OK
ansible-playbook deploy.yml -e release=v1.1           # OK
ansible-playbook deploy.yml -e release=v9.9           # rescue : le lien reste sur v1.1
readlink /tmp/app/current                             # → .../releases/v1.1
ansible-playbook deploy.yml -e release=abc            # assert échoue
cat /tmp/app/deploy.log
ansible-playbook deploy.yml --tags purge
```

👉 Corrigé : [solution/deploy.yml](solution/deploy.yml)
