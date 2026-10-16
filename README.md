# 🎓 Formation Ansible — du débutant à l'expert

Une formation **complète, pratique et testée** : 21 modules (00 → 20), des **démos exécutables**, des **labos corrigés** et un **projet final**. Tout s'exécute dans un labo Docker jetable (ou en local pour la plupart des exercices).

```
 Débutant ──► Intermédiaire ──► Avancé ──► Expert
 01 02 03 04     05 06 07 08     09 10 11 12 13     14 15 16 17 18 19 20
```

## 🚀 Démarrage rapide

```bash
git clone https://github.com/nzembouong18/Ansible.git && cd Ansible
cd 00-lab && ./lab.sh up && ./lab.sh shell        # labo : control + lb1 + web1 + web2 + db1
# dans le conteneur :
cd /workspace && ansible all -m ping
```

Pas de Docker ? La plupart des démos tournent en local :
`pip install ansible ansible-lint molecule pytest && ./tests/run-checks.sh`

## 📚 Programme

| # | Module | Niveau | Durée | Lab |
|---|---|---|---|---|
| 00 | [Laboratoire](00-lab/README.md) | 🟢 | 0,5 h | validation de l'environnement |
| 01 | [Fondamentaux](01-fondamentaux/README.md) | 🟢 | 2 h | premier playbook |
| 02 | [Inventaires](02-inventaires/README.md) | 🟢 | 2 h | inventaire 3-tiers |
| 03 | [Commandes ad-hoc](03-ad-hoc/README.md) | 🟢 | 1,5 h | administration en ad-hoc |
| 04 | [Playbooks](04-playbooks/README.md) | 🟢 | 3 h | déployer nginx |
| 05 | [Variables, facts, précédence](05-variables-facts/README.md) | 🟡 | 3 h | rapport matériel |
| 06 | [Contrôle de flux](06-controle-flux/README.md) | 🟡 | 3 h | déploiement avec rollback |
| 07 | [Templates Jinja2](07-templates-jinja2/README.md) | 🟡 | 3 h | config HAProxy depuis l'inventaire |
| 08 | [Rôles](08-roles/README.md) | 🟡 | 3,5 h | rôle nginx multi-OS |
| 09 | [Collections & Galaxy](09-collections-galaxy/README.md) | 🟡 | 2,5 h | collection `acme.tools` |
| 10 | [Vault & secrets](10-vault/README.md) | 🟡 | 2 h | secrets multi-environnements |
| 11 | [Modules essentiels](11-modules-essentiels/README.md) | 🟡 | 3 h | pile nginx + PostgreSQL |
| 12 | [Débogage & performance](12-debug-performance/README.md) | 🟠 | 2,5 h | optimiser un playbook lent |
| 13 | [Inventaires dynamiques](13-inventaires-dynamiques/README.md) | 🟠 | 2,5 h | inventaire depuis un CSV |
| 14 | [Modules & plugins custom](14-developpement/README.md) | 🔴 | 3 h | module `config_kv` + pytest |
| 15 | [Tests, Molecule, CI](15-tests-qualite/README.md) | 🔴 | 3 h | tester un rôle avec Molecule |
| 16 | [Déploiements avancés](16-deploiements-avances/README.md) | 🔴 | 3 h | rolling update sans coupure |
| 17 | [Windows, réseau, cloud, K8s](17-windows-reseau-cloud-conteneurs/README.md) | 🔴 | 3,5 h | manifests Kubernetes |
| 18 | [AWX, EE, navigator, EDA](18-awx-ee-eda/README.md) | 🔴 | 3 h | EE + navigator + AWX as code |
| 19 | [Sécurité & durcissement](19-securite/README.md) | 🔴 | 3 h | durcir et auditer |
| 20 | [**Projet final**](20-projet-final/README.md) | 🔴 | 6-8 h | plateforme web complète |

🟢 débutant · 🟡 intermédiaire · 🟠 avancé · 🔴 expert — **≈ 60 h** au total (cours + démos + labos).

## 🗓️ Parcours proposés

| Format | Planning |
|---|---|
| **Intensif 5 jours** (débutant → intermédiaire) | J1 : 00-03 · J2 : 04-05 · J3 : 06-07 · J4 : 08-10 · J5 : 11 + mini-projet |
| **Expert 3 jours** (prérequis : modules 01-11) | J1 : 12-14 · J2 : 15-17 · J3 : 18-19 + démonstration du projet final |
| **Autonomie 8 semaines** | 2-3 modules / semaine, lab obligatoire, quiz en fin de module |
| **Préparation RHCE (EX294)** | [annexes/certification.md](annexes/certification.md) |

## 🧭 Chaque module contient

```
NN-module/
├── README.md     cours : objectifs, théorie, schémas, exemples, points clés, quiz
├── demos/        démonstrations exécutables (à lancer, lire, modifier)
└── labs/lab-NN-*/  README.md (énoncé + critères de validation) + solution/ (corrigé testé)
```

## ✅ Qualité : tout est vérifié

* `ansible-lint` profil **production** : 0 erreur (voir [.ansible-lint](.ansible-lint)).
* [`tests/run-checks.sh`](tests/run-checks.sh) rejoue démos et solutions exécutables localement (lint, playbooks, inventaires, pytest, Molecule, projet final) — branché à la CI : [.github/workflows/ci.yml](.github/workflows/ci.yml).
* Versions de référence : ansible-core 2.21 (paquet `ansible` 14), Python 3.12+, Molecule 26.

**Ce qui n'est pas exécutable sans infrastructure dédiée** (validé syntaxiquement + lint seulement) : labo Docker lui-même, Windows/WinRM, équipements réseau, comptes cloud, AWX, cluster Kubernetes (la génération de manifests est testée), pile PostgreSQL du lab 11, scénarios Molecule `docker`.

## 📎 Annexes

[Aide-mémoire](annexes/cheatsheet.md) · [Glossaire](annexes/glossaire.md) · [Dépannage](annexes/troubleshooting.md) · [Quiz final + corrigé](annexes/quiz-final.md) · [Certification EX294](annexes/certification.md) · [Ressources](annexes/ressources.md)

## 🔐 Avertissement sécurité

Les mots de passe Vault (`formation-lab-only`, `dev-lab-pass`…), les conteneurs `privileged` et les clés SSH du labo sont **réservés à l'apprentissage**. Ne les réutilisez jamais en production.
