# Module 09 — Collections, Galaxy et gestion des dépendances

> **Durée** : 2 h 30 · **Niveau** : intermédiaire

## 🎯 Objectifs

* Comprendre ce qu'est une **collection** et le **FQCN** (`namespace.collection.plugin`).
* Installer rôles et collections avec `ansible-galaxy` et `requirements.yml`.
* Épingler les versions pour des exécutions reproductibles.
* Créer, construire, tester et publier sa propre collection.
* Connaître Galaxy, Automation Hub et les dépôts privés.

---

## 1. Collection : le format de distribution moderne

Depuis Ansible 2.10, le contenu est découpé :

```
ansible-core           ← moteur + ansible.builtin (≈70 modules)
ansible (paquet)       ← ansible-core + ~100 collections communautaires
collections à la carte ← community.general, amazon.aws, kubernetes.core, ...
```

Une collection regroupe **modules, plugins (filter, lookup, inventory, callback, connection…), rôles, playbooks, documentation**.

**FQCN** = `namespace.collection.nom` :

```yaml
- community.general.ini_file:        # module
- ansible.posix.firewalld:           # module
- "{{ x | ansible.utils.ipaddr }}"   # filtre
- "{{ lookup('community.general.random_string') }}"
- ansible.builtin.include_role: { name: acme.web.nginx }   # rôle dans une collection
```

Pourquoi toujours utiliser le FQCN ? Lisibilité, absence d'ambiguïté, exigé par `ansible-lint`, compatible avec les `redirects` lors des renommages.

### Arborescence d'une collection

```
ansible_collections/acme/web/
├── galaxy.yml              # métadonnées (namespace, name, version, dépendances)
├── README.md
├── meta/runtime.yml        # requires_ansible, redirections, groupes d'actions
├── plugins/
│   ├── modules/  filter/  lookup/  inventory/  callback/  module_utils/  ...
├── roles/<nom>/            # rôles
├── playbooks/
├── docs/
└── tests/                  # sanity, unit, integration
```

## 2. `ansible-galaxy`

```bash
# --- Collections ---
ansible-galaxy collection install community.general
ansible-galaxy collection install community.general:==9.5.0          # version exacte
ansible-galaxy collection install 'community.general:>=9,<10'
ansible-galaxy collection install -r requirements.yml -p ./collections
ansible-galaxy collection install ./acme-web-1.0.0.tar.gz            # depuis une archive
ansible-galaxy collection install git+https://github.com/org/col.git,main
ansible-galaxy collection list
ansible-galaxy collection verify community.general
ansible-doc -l community.general | head                               # modules d'une collection

# --- Rôles ---
ansible-galaxy role install geerlingguy.docker
ansible-galaxy role install -r roles/requirements.yml -p ./roles
ansible-galaxy role list
ansible-galaxy role init monrole
ansible-galaxy role remove geerlingguy.docker
```

### `requirements.yml` (rôles + collections, une seule source de vérité)

Voir [demos/requirements.yml](demos/requirements.yml).

* `ansible-galaxy install -r requirements.yml` installe rôles **et** collections (selon les clés présentes).
* `--force` pour réinstaller, `--upgrade` pour monter de version.
* Emplacement : `collections_path` dans `ansible.cfg` (par défaut `~/.ansible/collections`), ou `-p ./collections` pour **vendoriser dans le projet** (conseillé pour la reproductibilité).

## 3. Reproductibilité : épingler les versions

| Pratique | Pourquoi |
|---|---|
| Contraintes de version dans `requirements.yml` | une mise à jour amont ne casse pas votre CI |
| `ansible-core` épinglé (`requirements.txt` / image d'EE) | comportement stable |
| Collections vendorisées ou miroir interne | pas de dépendance à Internet en production |
| Mise à jour planifiée (Renovate/Dependabot) + CI | montée de version testée |
| `ansible-galaxy collection verify` | intégrité |

Python côté contrôleur : `pip install -r requirements.txt` (jmespath, netaddr, boto3, kubernetes…). Chaque collection documente ses dépendances Python (`requirements.txt` dans la collection, ou `ansible-builder` pour des *Execution Environments*, module 18).

## 4. Où trouver / publier

| Source | Description |
|---|---|
| **Ansible Galaxy** (galaxy.ansible.com) | hub communautaire public |
| **Red Hat Automation Hub** | collections certifiées/supportées (abonnement AAP) |
| **Private Automation Hub / galaxy_ng** | dépôt privé d'entreprise |
| **Git** | `git+https://…` dans requirements.yml |
| **Artifactory / Nexus / S3** | miroirs d'archives `.tar.gz` |

Configuration des serveurs (ansible.cfg) :

```ini
[galaxy]
server_list = private_hub, galaxy

[galaxy_server.private_hub]
url = https://hub.example.com/api/galaxy/content/published/
token = <token>        # utilisez une variable d'environnement ANSIBLE_GALAXY_SERVER_PRIVATE_HUB_TOKEN

[galaxy_server.galaxy]
url = https://galaxy.ansible.com/
```

🔒 Ne commitez jamais de token ; utilisez les variables d'environnement.

## 5. Créer sa collection

```bash
ansible-galaxy collection init acme.web --init-path ./collections/ansible_collections
cd collections/ansible_collections/acme/web
# ajoutez rôles, plugins, docs...  puis :
ansible-galaxy collection build                 # → acme-web-1.0.0.tar.gz
ansible-galaxy collection install acme-web-1.0.0.tar.gz -p /tmp/test
ansible-galaxy collection publish acme-web-1.0.0.tar.gz --token $TOKEN   # Galaxy ou hub privé
```

`galaxy.yml` essentiel : `namespace`, `name`, `version` (**SemVer**), `authors`, `readme`, `license`, `dependencies`, `build_ignore`.

**Bonnes pratiques de collection**

1. SemVer strict : `MAJOR` = rupture, `MINOR` = fonctionnalité, `PATCH` = correctif.
2. `meta/runtime.yml` : `requires_ansible: ">=2.15.0"`.
3. Documenter chaque plugin (`DOCUMENTATION`, `EXAMPLES`, `RETURN`) → visible dans `ansible-doc`.
4. Tests : `ansible-test sanity`, `units`, `integration`.
5. Changelog (antsibull-changelog), CI de publication sur tag.

Dans une collection, on référence ses propres plugins par FQCN complet ou via `collections:` (déprécié pour les nouveaux contenus : préférez le FQCN).

## 6. Résolution de noms et `collections:`

```yaml
- hosts: all
  collections:                   # liste de recherche (hérité mais courant)
    - community.general
  tasks:
    - ini_file: …                # résolu via la liste, FQCN préférable !
```

`ansible-lint` signale les noms courts. Utilisez le FQCN, cela évite aussi les surprises lorsque deux collections définissent un module du même nom.

## 7. Dépanner

| Symptôme | Cause / remède |
|---|---|
| `couldn't resolve module/action 'x'` | collection non installée ou mauvais `collections_path` → `ansible-galaxy collection list` |
| Mauvaise version utilisée | plusieurs chemins : `ansible-config dump \| grep COLLECTIONS_PATHS` |
| `ModuleNotFoundError` (boto3, kubernetes…) | dépendance Python manquante côté contrôleur |
| Échec d'installation hors-ligne | utiliser un miroir ou installer depuis `.tar.gz` |

## 8. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/requirements.yml](demos/requirements.yml) | rôles + collections, versions, git, fichier |
| [demos/formation/utils](demos/formation/utils) | une vraie collection : filtre `slugify` + rôle `hello` |
| [demos/01-utiliser-collection.yml](demos/01-utiliser-collection.yml) | utilisation après build/install |

```bash
cd 09-collections-galaxy/demos
ansible-galaxy collection build formation/utils --output-path /tmp/col-out
ansible-galaxy collection install /tmp/col-out/formation-utils-1.0.0.tar.gz -p ./collections
ANSIBLE_COLLECTIONS_PATH=./collections ansible-playbook 01-utiliser-collection.yml
ANSIBLE_COLLECTIONS_PATH=./collections ansible-doc -t filter formation.utils.slugify
```

## 9. 🛠️ Labs

* [Lab 09 — Créer, construire et consommer la collection `acme.tools`](labs/lab-09-collection/README.md)

## ✅ Points clés

* Collection = unité de distribution ; FQCN partout.
* `requirements.yml` + versions épinglées = reproductibilité.
* `ansible-galaxy collection build/install/publish` ; SemVer ; docs dans les plugins.
* Dépôt privé pour l'entreprise ; tokens en variables d'environnement.

## ❓ Quiz

1. Que signifie FQCN ? *(Fully Qualified Collection Name)*
2. Comment installer depuis un fichier ? *(`ansible-galaxy collection install fichier.tar.gz`)*
3. Pourquoi vendoriser les collections dans le projet ? *(reproductibilité, hors-ligne)*
4. Quel fichier décrit la collection ? *(`galaxy.yml`)*
