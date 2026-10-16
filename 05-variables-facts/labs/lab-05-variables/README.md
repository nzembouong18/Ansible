# Lab 05 — Rapport d'inventaire matériel avec facts & variables

⏱️ 1 h · Labo Docker (ou `localhost` pour tester la logique).

## 🎯 Objectif

Produire, **sur le nœud de contrôle**, un rapport `report/inventaire.txt` qui liste pour chaque hôte : nom, OS, vCPU, RAM, IP, et deux variables métier (`owner`, `env`) issues de l'inventaire.

## Énoncé

1. Dans l'inventaire du labo, ajoutez (ou créez un dossier `group_vars`/`host_vars` à côté du playbook) :
   * `group_vars/all.yml` : `owner: equipe-infra`, `env: lab`
   * `group_vars/dbservers.yml` : `owner: equipe-dba`
   * `host_vars/web1.yml` : `env: recette`
2. Écrivez `rapport.yml` (cible `all`) :
   * une tâche `set_fact` calcule `ram_gb` (RAM en Go, arrondie à 1 décimale — filtre `round`) ;
   * une tâche **exécutée une seule fois** (`run_once`) sur le contrôleur (`delegate_to: localhost`) écrit le rapport en bouclant sur `ansible_play_hosts` et en lisant `hostvars[h]`.
3. Le rapport doit contenir une ligne par hôte, au format :
   `web1 | Ubuntu 24.04 | 4 vCPU | 15.7 Go | 172.18.0.3 | equipe-infra | recette`

## Validation

```bash
ansible-playbook rapport.yml
cat report/inventaire.txt
ansible-playbook rapport.yml -e owner=surcharge      # -e gagne partout : tous les owners changent
```

**Questions** : pourquoi `web1` a-t-il `env: recette` alors que `all` dit `lab` ? Pourquoi db1 a-t-il `equipe-dba` ? (→ précédence.)

👉 Corrigé : [solution/](solution/)
