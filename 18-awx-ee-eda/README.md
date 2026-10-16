# Module 18 — Plateforme d'automatisation : AWX / AAP, Execution Environments, navigator, EDA

> **Durée** : 3 h · **Niveau** : expert

## 🎯 Objectifs

* Comprendre pourquoi passer de la ligne de commande à une **plateforme** (AWX / Red Hat AAP).
* Maîtriser les objets : organisation, projet, inventaire, identifiant, modèle de job, workflow, questionnaire, planification, RBAC.
* Construire des **Execution Environments** avec `ansible-builder` et les exécuter avec `ansible-navigator`.
* Découvrir **Event-Driven Ansible** (EDA) et les alternatives (Semaphore, Jenkins/GitLab CI).
* Gérer la plateforme **as code** (`awx.awx`).

---

## 1. Pourquoi une plateforme ?

Limites de `ansible-playbook` lancé depuis un poste : pas de contrôle d'accès fin, secrets sur les postes, pas d'historique centralisé, pas de planification, pas d'API, pas d'approbation, environnements d'exécution disparates.

| Besoin | Réponse AWX / AAP |
|---|---|
| Qui peut lancer quoi, sur quoi ? | **RBAC** (rôles par objet) |
| Secrets hors des postes | **Credentials** chiffrés (SSH, Vault, cloud, Git…) |
| Traçabilité / audit | **Historique des jobs**, logs, activity stream |
| Automatisation planifiée | **Schedules** |
| Intégration CI/CD, ITSM | **API REST**, webhooks, CLI `awx` |
| Approbation avant la prod | **Workflows** avec nœuds d'approbation |
| Même environnement partout | **Execution Environments** (conteneurs) |
| Self-service | **Surveys** (questionnaires) |
| Observabilité | Notifications (Slack, mail, webhook), métriques |

**AWX** = projet amont communautaire (Operator Kubernetes). **AAP** (Ansible Automation Platform) = produit Red Hat supporté (controller, automation hub, EDA controller, mesh). **Alternatives** : Semaphore UI (léger), Rundeck, Jenkins/GitLab CI avec runners Ansible, Ansible Semaphore + Vault.

## 2. Modèle d'objets

```
Organisation
 ├─ Équipes / Utilisateurs  ── RBAC (Admin, Execute, Use, Read, Update…)
 ├─ Credentials (Machine, Vault, Source Control, Cloud, Custom)
 ├─ Projects (dépôt Git + branche + synchronisation)
 ├─ Inventories (statiques, sources dynamiques: cloud, SCM, script)
 │    └─ Hôtes, Groupes, Variables, Smart inventories
 ├─ Execution Environments (images)
 ├─ Job Templates ── projet + playbook + inventaire + credentials + EE + options
 │    └─ Survey, Limit, Tags, Verbosity, Fork, Job slicing, Concurrent jobs, Webhooks
 ├─ Workflow Job Templates ── graphe: succès / échec / toujours + approbations
 ├─ Schedules (rrule)
 └─ Notification templates
```

**Cycle** : commit Git → sync du projet → lancement (UI/API/schedule/webhook) → job dans un EE → logs et statut → notification.

### Notions importantes

* **Job slicing** : découpe un job en N sous-jobs parallèles sur des tranches d'inventaire.
* **Instance groups / mesh** : exécution dans des réseaux distants (receptor), capacité par nœud.
* **Isolation** : chaque job tourne dans un conteneur éphémère (EE).
* **Variables** : inventaire < groupe < hôte < template (extra vars) < survey ; `Prompt on launch` autorise la surcharge.
* **Credentials custom** : injectent variables d'environnement, extra vars ou fichiers (ex. token d'un outil interne).

## 3. Execution Environments (EE)

Un **EE** est une image de conteneur contenant `ansible-core`, `ansible-runner`, les **collections**, les dépendances **Python** et **système**. Il remplace le « ça marche chez moi » : même image pour le développeur, la CI et AWX.

`ansible-builder` (fichier [demos/execution-environment/execution-environment.yml](demos/execution-environment/execution-environment.yml)) :

```bash
pip install ansible-builder
ansible-builder create --file execution-environment.yml --context ctx   # génère seulement le Containerfile
ansible-builder build  --file execution-environment.yml --tag quay.io/org/ee-formation:1.0
podman push quay.io/org/ee-formation:1.0
```

Fichiers : `requirements.yml` (collections), `requirements.txt` (Python), `bindep.txt` (système).
Images de base : EE minimaux Red Hat, `quay.io/ansible/community-ee-minimal`, Fedora/UBI.

Bonnes pratiques : **épingler** versions/tags, un EE par usage (réseau, cloud, K8s), rebuild automatisé (CI) + scan de vulnérabilités, registre privé.

## 4. ansible-navigator

Interface unifiée (TUI ou `-m stdout`) qui exécute playbooks **dans un EE** et garde des **artefacts** rejouables :

```bash
ansible-navigator run site.yml -i inventory --eei ee-formation:1.0 -m stdout
ansible-navigator run site.yml --ee false            # sans conteneur (comme ansible-playbook)
ansible-navigator replay artifacts/site-....json     # rejouer/inspecter un run passé
ansible-navigator inventory -i hosts.ini --graph -m stdout
ansible-navigator doc ansible.builtin.copy -m stdout
ansible-navigator collections                        # collections de l'EE
ansible-navigator images                             # images disponibles
```

Configuration : [demos/navigator/ansible-navigator.yml](demos/navigator/ansible-navigator.yml). `ansible-runner` est le moteur sous-jacent (AWX l'utilise aussi).

## 5. Installer AWX (labo)

Via l'**AWX Operator** sur Kubernetes (kind/minikube/k3s) : [demos/awx-install/](demos/awx-install).

```bash
kind create cluster --name awx
cd demos/awx-install && kubectl apply -k .
kubectl -n awx get pods -w
kubectl -n awx get secret awx-demo-admin-password -o jsonpath='{.data.password}' | base64 -d; echo
# UI : http://localhost:30080 (NodePort, selon votre config kind/minikube)
```

⚠️ AWX n'est pas "prêt pour la prod" sans travail (sauvegardes, HA, versions). En entreprise : AAP, ou AWX avec procédures d'exploitation maîtrisées.

## 6. AWX as code

Tout ce qui est cliqué dans l'UI doit finir **dans Git** : collection `awx.awx` (ou `ansible.controller` pour AAP) — [demos/awx-as-code/setup-awx.yml](demos/awx-as-code/setup-awx.yml) crée organisation, credentials, projet, inventaire, modèle avec questionnaire, planning.

```bash
export CONTROLLER_HOST=https://awx.example.com
export CONTROLLER_OAUTH_TOKEN=...              # jamais dans Git
ansible-playbook setup-awx.yml
```

Variantes : `awx export/import` (CLI), `infra.aap_configuration` (collection de référence pour AAP), Terraform provider `AWX`.

## 7. Workflows et approbation

```
 [Sync projet] ─► [Déployer DB] ─► [Déployer web] ─► [Smoke tests] ─┬─ succès ─► [Approbation prod] ─► [Déployer prod]
                       │ échec                          │ échec        └─ échec  ─► [Rollback + notification]
                       └────────► [Notifier l'équipe] ◄─┘
```

Chaque nœud : succès / échec / toujours. **Approval node** : un humain valide dans l'UI avec délai d'expiration.

## 8. Event-Driven Ansible (EDA)

Réagir à des **événements** plutôt qu'à des humains : alertes Prometheus/Alertmanager, webhooks, Kafka, journaux, ServiceNow…

```yaml
- name: Réagir
  hosts: all
  sources:
    - ansible.eda.alertmanager: { host: 0.0.0.0, port: 5001 }
  rules:
    - name: Redémarrer nginx
      condition: event.alert.labels.alertname == "NginxDown" and event.alert.status == "firing"
      action:
        run_playbook:
          name: remediate_nginx.yml
```

Concepts : **sources** (plugins qui émettent des événements), **rules** (condition → action), **actions** (`run_playbook`, `run_job_template`, `run_workflow_template`, `set_fact`, `post_event`, `debug`…). Lancement : `ansible-rulebook --rulebook rulebook.yml -i inventory.yml --verbose`.

Garde-fous : limiter les actions automatiques (boucles d'alertes !), `throttle` des règles, journaliser, commencer en lecture seule (notification) avant d'automatiser la remédiation. Démo : [demos/eda/](demos/eda).

## 9. Intégrer la CI/CD

| Étape | Outil |
|---|---|
| Lint, Molecule | CI (GitHub Actions / GitLab CI) |
| Build EE | CI → registre |
| Déclenchement de l'exécution | CI appelle l'API AWX (`awx job_templates launch` ou module `awx.awx.job_launch`) |
| Promotion | workflows AWX avec approbation |
| Retour | statut renvoyé à la CI / ticket |

## 10. 🧪 Démos

| Dossier | Contenu |
|---|---|
| [demos/execution-environment/](demos/execution-environment) | définition d'EE (`ansible-builder create` fonctionne sans conteneur) |
| [demos/navigator/](demos/navigator) | configuration `ansible-navigator` |
| [demos/awx-as-code/](demos/awx-as-code) | AWX configuré par playbook |
| [demos/awx-install/](demos/awx-install) | AWX Operator (kustomize) |
| [demos/eda/](demos/eda) | rulebook Alertmanager/webhook |

## 11. 🛠️ Labs

* [Lab 18 — EE, ansible-navigator et AWX as code](labs/lab-18-ee-awx/README.md)

## ✅ Points clés

* Une plateforme apporte RBAC, secrets, audit, planification, API, approbation.
* EE = environnement d'exécution reproductible (builder → registre → AWX/navigator).
* Tout configurer **as code** ; tokens hors Git.
* EDA : événements → règles → actions ; commencer prudemment.

## ❓ Quiz

1. Qu'est-ce qu'un EE ? *(image de conteneur avec ansible-core, collections, dépendances)*
2. Quel outil exécute un playbook dans un EE en local ? *(`ansible-navigator`)*
3. Comment automatiser la configuration d'AWX ? *(collection `awx.awx`)*
4. Composants d'une règle EDA ? *(source, condition, action)*
