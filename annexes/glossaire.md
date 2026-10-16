# Glossaire

| Terme | Définition |
|---|---|
| **Ad-hoc** | Commande Ansible unique, sans playbook |
| **AAP** | Ansible Automation Platform (produit Red Hat) |
| **AWX** | Projet amont communautaire d'AAP (interface web, API, RBAC) |
| **become** | Élévation de privilèges (sudo, su, runas…) |
| **Callback** | Plugin réagissant aux événements d'exécution (affichage, rapports) |
| **Check mode** | `--check` : simulation sans modification |
| **Collection** | Paquet distribuant modules, plugins, rôles (`namespace.nom`) |
| **Control node** | Machine qui exécute Ansible |
| **EDA** | Event-Driven Ansible : règles réagissant à des événements |
| **EE** | Execution Environment : image conteneur d'exécution |
| **Facts** | Informations collectées sur les hôtes (`setup`) |
| **FQCN** | Fully Qualified Collection Name |
| **Galaxy** | Dépôt public de rôles et collections |
| **Handler** | Tâche déclenchée par `notify` si `changed` |
| **Idempotence** | Appliquer N fois = appliquer 1 fois |
| **Inventaire** | Liste des hôtes et groupes (statique ou dynamique) |
| **Jinja2** | Moteur de templates utilisé par Ansible |
| **Lookup** | Plugin lisant une donnée externe côté contrôleur |
| **Managed node** | Hôte administré |
| **Module** | Unité de travail exécutée sur la cible |
| **Molecule** | Framework de test de rôles |
| **Play / Playbook** | Hôtes + tâches / fichier de plays |
| **Role** | Ensemble réutilisable de tâches, variables, templates |
| **Runner** | `ansible-runner` : exécute playbooks de façon programmable |
| **Task** | Appel d'un module avec ses paramètres |
| **Vault** | Chiffrement de fichiers/valeurs sensibles |
