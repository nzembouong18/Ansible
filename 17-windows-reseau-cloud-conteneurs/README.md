# Module 17 — Windows, réseau, cloud, conteneurs et Kubernetes

> **Durée** : 3 h 30 · **Niveau** : expert

## 🎯 Objectifs

* Administrer des hôtes **Windows** (WinRM / SSH) avec `ansible.windows`.
* Configurer des **équipements réseau** (connexions `network_cli`, resource modules).
* Piloter le **cloud** (AWS/Azure/GCP) et articuler Ansible avec Terraform.
* Gérer **Docker/Compose** et **Kubernetes/Helm**.

> ℹ️ Les démos de ce module nécessitent des cibles spécifiques (Windows, routeur, compte cloud, Docker, cluster). Elles sont **vérifiées syntaxiquement et par `ansible-lint`** ; la partie A du lab 17 (rendu de manifests) s'exécute entièrement en local.

---

## 1. Windows

### Connexion

| Méthode | Port | Quand |
|---|---|---|
| **WinRM** HTTPS | 5986 | historique, très répandu ; transports `ntlm`, `kerberos` (domaine), `credssp` |
| **OpenSSH** | 22 | Windows Server 2019+/Win10+ : même modèle que Linux (`ansible_connection=ssh`, `ansible_shell_type=powershell`) |
| PSRP | 5986 | `ansible_connection=psrp` |

Prérequis contrôleur : `pip install pywinrm` (+ `requests-credssp` ou `pykerberos`/`pyspnego` pour kerberos).
Préparation de la cible : [demos/windows/winrm-setup.ps1](demos/windows/winrm-setup.ps1) (**labo uniquement**, certificat auto-signé).

Inventaire : [demos/windows/inventory.yml](demos/windows/inventory.yml). 🔒 Mot de passe dans Vault.

### Modules

| Besoin | Module |
|---|---|
| Test | `ansible.windows.win_ping` |
| Fonctionnalités / rôles | `win_feature`, `win_optional_feature` |
| Logiciels | `chocolatey.chocolatey.win_chocolatey`, `win_package` (MSI/EXE), `win_get_url` |
| Services / tâches planifiées | `win_service`, `community.windows.win_scheduled_task` |
| Fichiers | `win_file`, `win_copy`, `win_template`, `win_lineinfile`, `win_acl` |
| Registre | `win_regedit` |
| Utilisateurs / groupes | `win_user`, `win_group`, `win_domain_*` |
| Pare-feu | `community.windows.win_firewall_rule` |
| Mises à jour | `win_updates`, `win_reboot` |
| PowerShell | `win_shell`, `win_command`, `win_powershell`, `win_dsc` |

Particularités : chemins `C:\...` (attention aux `\` dans YAML : utilisez des chaînes simples ou `\\`), `become_method: runas`, fins de ligne CRLF dans les templates, `ansible_shell_type`.

Démo : [demos/windows/01-socle-windows.yml](demos/windows/01-socle-windows.yml).

## 2. Équipements réseau

Le modèle diffère : le code Python s'exécute **sur le contrôleur** (pas d'agent ni de Python sur l'équipement) qui parle en CLI/NETCONF/API.

```yaml
ansible_connection: ansible.netcommon.network_cli      # SSH + CLI
# autres : ansible.netcommon.netconf, ansible.netcommon.httpapi (eAPI Arista, REST)
ansible_network_os: cisco.ios.ios                       # arista.eos.eos, junipernetworks.junos.junos, ...
ansible_become: true
ansible_become_method: enable
```

| Famille de modules | Philosophie | Exemple |
|---|---|---|
| `*_command` | exécuter des commandes show | `ios_command` |
| `*_config` | pousser des lignes de config (impératif, diff) | `ios_config` (`lines`, `parents`, `backup`, `save_when`) |
| **Resource modules** | modèle **déclaratif** par ressource, états `merged/replaced/overridden/deleted/gathered/rendered/parsed` | `ios_interfaces`, `ios_l3_interfaces`, `ios_vlans`, `ios_bgp_global` |
| `*_facts` | collecte | `ios_facts` |

Ce qui est précieux : `state: rendered` (génère la config sans l'appliquer), `gathered` (lit l'existant), `parsed` (transforme du texte en structure), et `ansible.utils.cli_parse` (textfsm/ttp/pyats).

Démo : [demos/reseau/01-config-reseau.yml](demos/reseau/01-config-reseau.yml). Bonnes pratiques : sauvegarde (`backup`) avant, `--check --diff`, fenêtre de maintenance, `serial: 1`, vérification post-change (`ios_ping`, `ios_command` + `assert`).

## 3. Cloud

### Ansible ⟷ Terraform

| | Terraform / OpenTofu | Ansible |
|---|---|---|
| Force | cycle de vie des ressources, **état**, plan | configuration d'OS/applications, orchestration |
| Modèle | déclaratif, graphe de dépendances | procédural idempotent |
| Idéal pour | VPC, VM, bases managées, DNS | paquets, fichiers, services, déploiements |

Schéma courant : **Terraform crée** → inventaire dynamique (`cloud.terraform` ou plugin cloud) → **Ansible configure**. Ansible peut aussi provisionner (collections `amazon.aws`, `azure.azcollection`, `google.cloud`, `openstack.cloud`, `community.vmware`, `kubernetes.core`).

Démo AWS : [demos/cloud/01-aws-provision.yml](demos/cloud/01-aws-provision.yml) — groupe de sécurité, instances, `add_host`, `wait_for`, bucket S3 chiffré et verrouillé.

Bonnes pratiques cloud : identités par **rôle IAM / identité managée** (pas de clés longues durée), `tags` systématiques (inventaire dynamique), idempotence par `name`/`tags`, `no_log` sur les secrets, régions en variables.

## 4. Docker et Compose

Collection `community.docker` (+ `pip install docker`) :

| Module | Rôle |
|---|---|
| `docker_image` / `docker_image_build` | pull, build, push |
| `docker_container` / `docker_container_exec` | cycle de vie, commandes |
| `docker_network`, `docker_volume` | ressources |
| `docker_compose_v2` | piloter un `compose.yaml` |
| `docker_login`, `docker_prune`, `docker_swarm*` | registre, nettoyage, Swarm |

Démo : [demos/docker/01-docker-app.yml](demos/docker/01-docker-app.yml).

Ansible dans les conteneurs : installer Docker sur l'hôte (rôle `geerlingguy.docker`), connexion directe `ansible_connection: community.docker.docker` pour administrer un conteneur sans SSH (utile en tests).

## 5. Kubernetes

Collection `kubernetes.core` (+ `pip install kubernetes`, un kubeconfig) :

| Module | Rôle |
|---|---|
| `k8s` | appliquer/supprimer des manifests (`definition`, `src`, `template`) ; `wait`, `apply`, `server_side_apply` |
| `k8s_info` | lire des ressources (inventaire, assertions de santé) |
| `helm`, `helm_repository`, `helm_info` | charts |
| `k8s_exec`, `k8s_log`, `k8s_drain`, `k8s_scale`, `k8s_rollback` | exploitation |

Démo : [demos/kubernetes/](demos/kubernetes) (manifests Jinja2).

⚠️ **`namespace` est un nom réservé** (builtin Jinja) : n'en faites pas une variable (`ansible-lint var-naming[no-reserved]`) → `k8s_namespace`.

**Ansible vs GitOps (Argo CD/Flux)** : pour le contenu *dans* le cluster, GitOps est le standard ; Ansible reste pertinent pour : bootstrap du cluster (kubeadm/k3s, RKE2), nœuds (OS, durcissement), installation d'Argo CD/Flux, secrets initiaux, configurations hors-cluster.

## 6. Choisir ses outils (synthèse)

| Besoin | Outil |
|---|---|
| Créer l'infrastructure cloud | Terraform/OpenTofu (ou Ansible `amazon.aws`) |
| Configurer l'OS et les apps | **Ansible** |
| Image immuable | Packer + Ansible (provisioner) |
| Déployer dans Kubernetes | Helm/GitOps ; Ansible pour le bootstrap |
| Parc réseau | Ansible resource modules + NetBox |
| Windows | Ansible + WinRM/SSH, DSC si besoin |

## 7. 🧪 Démos

| Dossier | Contenu |
|---|---|
| [demos/windows/](demos/windows) | WinRM, `win_*`, Chocolatey, IIS |
| [demos/reseau/](demos/reseau) | Cisco IOS : backup, resource modules |
| [demos/cloud/](demos/cloud) | AWS : SG, EC2, S3, `add_host` |
| [demos/docker/](demos/docker) | `community.docker` |
| [demos/kubernetes/](demos/kubernetes) | `kubernetes.core.k8s`, Helm |

## 8. 🛠️ Labs

* [Lab 17 — Générer, valider et déployer une application sur Kubernetes](labs/lab-17-docker-k8s/README.md)

## ✅ Points clés

* Windows : WinRM ou SSH ; modules `win_*` ; Vault pour les mots de passe.
* Réseau : exécution côté contrôleur ; préférez les **resource modules**.
* Cloud : Terraform provisionne, Ansible configure ; identités managées.
* K8s : `kubernetes.core` ; valider les manifests avant d'appliquer ; ne pas appeler une variable `namespace`.

## ❓ Quiz

1. Quel port pour WinRM HTTPS ? *(5986)*
2. Quel état de resource module génère la config sans l'appliquer ? *(`rendered`)*
3. Pourquoi ne pas utiliser `namespace` comme nom de variable ? *(nom réservé Jinja)*
4. Complémentarité Terraform / Ansible ? *(provisionner / configurer)*
