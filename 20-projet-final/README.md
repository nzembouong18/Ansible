# Module 20 — Projet final : une plateforme web livrée par Ansible

> **Durée** : 6 à 8 h (en autonomie) · **Niveau** : intégration de tout le parcours

## 🎯 Objectif

Livrer, testée et documentée, l'automatisation d'une application web sur trois environnements (`local`, `dev`, `prod`) en appliquant **toutes** les compétences de la formation : inventaires, variables, rôles, templates, Vault, rolling update, tests, CI, durcissement.

## Ce qui est fourni (point de départ fonctionnel)

```
20-projet-final/
├── ansible.cfg
├── .vault_pass_lab                      # mot de passe Vault du LABO (public !)
├── inventories/
│   ├── local/  dev/  prod/              # hosts.yml + group_vars/all/{vars.yml,vault.yml chiffré}
├── playbooks/site.yml                   # socle commun puis déploiement progressif (serial: 1)
└── roles/
    ├── common/                          # paquets de base + motd
    └── webapp/                          # releases versionnées, lien current, config avec secret,
        └── molecule/default/            #  purge des anciennes releases, health check, test Molecule
```

Exécution **100 % locale** immédiate :

```bash
cd 20-projet-final
ansible-playbook -i inventories/local/hosts.yml playbooks/site.yml --vault-password-file .vault_pass_lab
ansible-playbook -i inventories/local/hosts.yml playbooks/site.yml --vault-password-file .vault_pass_lab -e webapp_version=1.3.0
ls /tmp/projet-final/web1/releases          # 1.2.0 1.3.0 (purge au-delà de webapp_keep_releases)
cd roles/webapp && molecule test            # tests du rôle
```

Sur le **labo Docker** : copier `inventories/dev/hosts.yml` (hôtes `lb1`, `web1`, `web2`) puis `ansible-playbook playbooks/site.yml --vault-password-file .vault_pass_lab` depuis le conteneur `control` (`-i inventories/dev/hosts.yml`).

## Cahier des charges à compléter

### Niveau 1 — Fondations (obligatoire)

1. Lire et **expliquer** (README personnel) chaque fichier fourni : où vit chaque variable, qui gagne (précédence).
2. Ajouter le rôle `nginx` du lab 08 devant l'application : nginx sert `current/` (alias vers `{{ webapp_root }}/current`) sur le port `webapp_port`.
3. Ajouter un play `loadbalancers` : rôle `haproxy` (lab 07, template généré **depuis l'inventaire**), avec `validate:` et handler `reload`.
4. Remplacer la tâche de health check par un vrai `uri` (HTTP 200) avec `retries/until`.
5. `ansible-lint` (profil `production`) et `yamllint` sans erreur.

### Niveau 2 — Production-ready

6. **Rolling update sans interruption** : retirer chaque web du LB (`delegate_to` + `community.general.haproxy` ou équivalent) avant mise à jour, le réintégrer après health check ; rollback automatique en `rescue` (lab 16).
7. Rôle `hardening` (module 19) appliqué à tous les hôtes + audit avant/après, avec garde-fou anti-verrouillage.
8. **Secrets** : `vault_webapp_db_password` différent par environnement (vault-id `dev`/`prod`, lab 10) ; aucun secret en clair ; `no_log` ; modes `0640/0600`.
9. `argument_specs.yml` pour `webapp` et `common`.
10. Tags (`common`, `app`, `lb`, `harden`, `verify`) et playbook `verify.yml` de smoke tests de bout en bout.

### Niveau 3 — Expert

11. **Molecule** : scénarios `default` (local) et `docker` (Ubuntu + Rocky) pour `webapp`, `nginx`, `hardening`, branchés à la CI (`.github/workflows/ci.yml`).
12. **Inventaire dynamique** : script ou plugin lisant une source (CSV/API) pour l'environnement `dev` (lab 13).
13. **Module ou filtre personnalisé** utile au projet (ex. `webapp_release_info`, lab 14) avec tests pytest.
14. **Collection** `monorg.webplatform` contenant les rôles (module 09), construite et installée via `requirements.yml`.
15. **EE + AWX as code** (module 18) : EE construit, projet/inventaire/modèle/workflow avec approbation avant la production.
16. **Observabilité** : callback ou tâche `uri` notifiant (webhook) début/fin/échec de chaque déploiement.

## Livrables

* Dépôt Git propre (historique lisible, commits atomiques).
* `README.md` du projet : architecture (schéma), prérequis, commandes, variables, procédure de **rollback**, procédure de **rotation des secrets**.
* Résultat de `./tests/run-checks.sh` (ou CI verte).
* Courte démonstration (5 min) : déploiement d'une nouvelle version avec échec simulé puis rollback.

## Grille d'évaluation (100 points)

| Critère | Points |
|---|---|
| Fonctionnement : playbooks exécutables, **idempotents** (2ᵉ passage `changed=0`) | 20 |
| Structure : rôles, variables (`defaults`/`group_vars`), inventaires multi-env, FQCN | 15 |
| Sécurité : Vault, `no_log`, moindre privilège, durcissement, pas de secret en clair | 15 |
| Fiabilité : `serial`, health checks, rollback, `validate:`, garde-fous | 15 |
| Qualité : `ansible-lint` production, `yamllint`, Molecule, CI | 15 |
| Documentation : README, schéma, procédures | 10 |
| Extensions (niveau 3 : plugin/module/collection/EE/AWX) | 10 |

Barème : < 50 insuffisant · 50-69 acquis · 70-84 solide · ≥ 85 expert.

## Pistes de correction (formateur)

* Idempotence : `webapp` ne doit pas être `changed` au 2ᵉ passage (le lien `current` n'est modifié que si la cible change).
* Piège : `become` dans `site.yml` est désactivé en local par une expression — à remplacer par `ansible_become` dans l'inventaire.
* Piège : la purge des releases se base sur `mtime` ; en production préférez un tri sémantique par version.
* Piège : `run_once` + `serial` (module 16) pour une migration de base.
* Les solutions de référence de chaque brique se trouvent dans les `labs/*/solution` des modules 07, 08, 10, 13, 14, 15, 16, 18, 19.

## ✅ Auto-évaluation finale

Avant de déclarer le projet terminé : *Puis-je détruire et reconstruire tout l'environnement avec une seule commande ? Un collègue peut-il déployer sans me demander quoi que ce soit ? Un secret a-t-il été commité ? Que se passe-t-il si le déploiement échoue au milieu ?*
