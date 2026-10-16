# Lab 03 — Dépannage et administration en ad-hoc

⏱️ 45 min · Nécessite le labo Docker (module 00).

Un collègue vous demande de réaliser, **uniquement avec des commandes ad-hoc**, les opérations suivantes :

1. Vérifier que tous les nœuds répondent (une ligne par hôte).
2. Afficher la version de l'OS de chaque nœud (facts `ansible_distribution*`).
3. Afficher l'espace libre de `/` sur chaque nœud.
4. Créer l'utilisateur `bob` (shell `/bin/bash`, groupe `sudo`) sur **webservers uniquement**.
5. Créer `/srv/data` (mode `0750`, propriétaire `bob`) sur webservers.
6. Installer `nginx` sur webservers, le démarrer et l'activer au boot. Vérifier avec `curl http://localhost` depuis les nœuds.
7. Récupérer `/etc/hostname` de chaque nœud dans `./collected/` (module `fetch`).
8. Trouver le processus le plus gourmand en mémoire de `db1` (indice : `shell` + `ps` + `sort`).
9. Supprimer `bob` et `/srv/data` (nettoyage).

**Bonus** : réexécutez l'étape 4 deux fois. Quel est le statut la 2ᵉ fois ? Pourquoi ?

👉 Corrigé : [solution/commandes.sh](solution/commandes.sh)
