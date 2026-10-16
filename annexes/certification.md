# Préparation à la certification Red Hat EX294 (RHCE)

> L'examen est **pratique** (4 h sur machines RHEL). Les objectifs évoluent : consultez la page officielle de l'examen. Correspondance indicative avec cette formation :

| Objectif EX294 (résumé) | Modules |
|---|---|
| Installer et configurer un nœud de contrôle (`ansible.cfg`, inventaire, utilisateur distant) | 01, 02 |
| Commandes ad-hoc | 03 |
| Playbooks : plays, tâches, handlers, tags | 04, 06 |
| Variables, facts, facts personnalisés, `register` | 05 |
| Boucles, conditions, blocs, gestion d'erreurs | 06 |
| Templates Jinja2 | 07 |
| Rôles, `ansible-galaxy`, rôles système RHEL (`rhel-system-roles`) | 08, 09 |
| Collections et dépôts | 09 |
| Ansible Vault | 10 |
| Modules : paquets, dépôts, services, firewalld, SELinux, stockage (lvg/lvol/filesystem), utilisateurs, cron, fichiers, archives | 11 |
| Navigator / EE (selon version de l'examen) | 18 |

## Plan d'entraînement (4 semaines)

| Semaine | Contenu | Exercices chronométrés |
|---|---|---|
| 1 | Modules 01-05 | Écrire un inventaire, configurer un nœud en 20 min |
| 2 | Modules 06-08, 11 | Déployer un serveur web complet via rôle en 45 min |
| 3 | Modules 09-10, 11 (stockage, SELinux, firewalld) | Playbook de stockage LVM + montage en 30 min |
| 4 | Examens blancs sur le labo (`./lab.sh rocky`) | 4 h en conditions réelles |

## Conseils pratiques

* Maîtrisez `ansible-doc` : **c'est la seule documentation disponible** à l'examen.
* Apprenez les arguments de `firewalld`, `selinux`, `seboolean`, `lvg`, `lvol`, `filesystem`, `mount`, `user`, `cron`.
* Testez avec `--syntax-check` et `--check`, puis exécutez deux fois (idempotence).
* Respectez à la lettre les noms, chemins, permissions demandés.
* Gérez le temps : ne restez pas bloqué plus de 10 min sur une tâche.
* Entraînez-vous avec Rocky/Alma (`./lab.sh rocky`) pour les spécificités RedHat (dnf, SELinux, firewalld).
