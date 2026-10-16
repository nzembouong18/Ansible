# Quiz final (40 questions) — corrigé en bas de page

**Fondamentaux**
1. Pourquoi Ansible est-il dit « agentless » ?
2. Que signifie idempotent ? Quel module n'est pas idempotent par nature ?
3. Quel est le fichier de configuration lu en premier ?
4. Que fait `--check --diff` ?

**Inventaires et variables**
5. Comment cibler `webservers` sauf `web2` ?
6. Où placer les variables d'un seul hôte ?
7. Classez : `-e`, `defaults/main.yml`, `group_vars/all`, `vars` de tâche.
8. Pourquoi préférer `ansible_facts['x']` à `ansible_x` ?
9. Comment lire l'IP d'un autre hôte ?

**Playbooks et flux**
10. Quand un handler s'exécute-t-il ?
11. `import_tasks` vs `include_tasks` ?
12. Pourquoi `when: "{{ x }}"` est-il déconseillé ?
13. Rôle de `block/rescue/always` ?
14. Comment réessayer jusqu'à succès ?
15. Quel tag s'exécute toujours ?

**Templates et rôles**
16. Où est rendu un template ? Quel paramètre valide le résultat ?
17. Différence `defaults` / `vars` d'un rôle ?
18. Pourquoi préfixer les variables d'un rôle ?
19. À quoi sert `argument_specs.yml` ?
20. Comment charger des variables selon l'OS ?

**Collections, Vault**
21. Que signifie FQCN ?
22. Comment épingler une collection ?
23. Pattern `vars.yml` + `vault.yml` : pourquoi ?
24. Comment gérer dev/prod avec deux mots de passe ?
25. Que fait `no_log` ?

**Avancé**
26. Que fait `serial: [1, "100%"]` ?
27. Quel est le piège de `run_once` avec `serial` ?
28. À quoi sert `delegate_to` ?
29. `strategy: free` : effet ?
30. `async` + `poll: 0` : usage ?
31. Que doit renvoyer un script d'inventaire ?
32. Plugin `constructed` : rôle ?
33. Quand écrire un module plutôt qu'utiliser `command` ?
34. Cinq étapes d'un `molecule test` ?
35. Qu'est-ce qu'un Execution Environment ?
36. Qu'apporte AWX par rapport à `ansible-playbook` ?
37. Composants d'une règle EDA ?
38. Terraform vs Ansible : répartition ?
39. Comment éviter de s'enfermer dehors en durcissant SSH ?
40. Citez 3 mesures pour sécuriser le contrôleur.

---

## Corrigé

1. Pas d'agent à installer : SSH/WinRM + Python côté Linux.
2. Même résultat après 1 ou N exécutions ; `command`/`shell`/`raw`.
3. `ANSIBLE_CONFIG`, puis `./ansible.cfg`, `~/.ansible.cfg`, `/etc/ansible/ansible.cfg`.
4. Simule et montre les différences de fichiers.
5. `webservers:!web2`.
6. `host_vars/<hote>.yml`.
7. `defaults` < `group_vars/all` < `vars` de tâche < `-e`.
8. Les facts injectés comme variables sont dépréciés ; l'accès via `ansible_facts` est explicite et sûr.
9. `hostvars['db1']['ansible_facts']['default_ipv4']['address']` (facts déjà collectés).
10. En fin de play (ou `flush_handlers`), si notifié par une tâche `changed`.
11. Statique (au chargement) vs dynamique (à l'exécution).
12. `when` est déjà une expression Jinja ; et le résultat doit être booléen.
13. Gestion d'erreurs type try/catch/finally.
14. `retries`, `delay`, `until`.
15. `always`.
16. Sur le contrôleur ; `validate:`.
17. Faible priorité (interface surchargeable) vs forte (constantes internes).
18. Portée globale des variables : éviter les collisions.
19. Valider automatiquement les paramètres et documenter le rôle.
20. `include_vars` avec `first_found` sur `distribution`/`os_family`.
21. Fully Qualified Collection Name.
22. `requirements.yml` avec `version:` ou contrainte.
23. Lisibilité : on voit les noms de variables sans déchiffrer.
24. `--vault-id dev@… --vault-id prod@…`.
25. Masque arguments et résultat dans les logs.
26. Un canari, puis tout le reste.
27. `run_once` s'applique à chaque lot ; utiliser `ansible_play_hosts_all[0]`.
28. Exécuter la tâche sur un autre hôte avec le contexte de l'hôte courant (LB, API).
29. Chaque hôte avance sans attendre les autres.
30. Lancer une tâche longue sans attendre, puis `async_status`.
31. `--list` (JSON avec `_meta.hostvars`) et `--host`.
32. Crée groupes et variables calculés à partir d'une source existante.
33. Pour une API/état complexe nécessitant idempotence, check_mode, diff.
34. syntax, converge, idempotence, verify, cleanup (avec create/destroy pour les drivers conteneurs).
35. Image de conteneur avec ansible-core, collections et dépendances.
36. RBAC, secrets, audit, planification, API, workflows/approbation, EE.
37. Source, condition, action.
38. Terraform provisionne ; Ansible configure.
39. Vérifier la clé, garder une session ouverte, `validate: sshd -t`, un hôte d'abord, console de secours.
40. Clés protégées/courtes, bastion/isolation, MFA, secrets en coffre, EE jetables, revue de code, journalisation.
