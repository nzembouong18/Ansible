# Module 11 — Modules essentiels : le catalogue du quotidien

> **Durée** : 3 h · **Niveau** : intermédiaire

## 🎯 Objectifs

* Connaître les ~40 modules qui couvrent 90 % des besoins.
* Choisir le bon module (et éviter `shell`).
* Savoir lire `ansible-doc` et ses valeurs de retour.

> 💡 Méthode : `ansible-doc -l | grep <mot>` pour trouver, `ansible-doc <module>` pour les exemples, `ansible-doc -s <module>` pour le squelette de paramètres.

---

## 1. Fichiers et contenu

| Besoin | Module | Points d'attention |
|---|---|---|
| Fichier/dossier/lien/permissions | `ansible.builtin.file` | `state: directory\|touch\|link\|absent` ; `recurse` |
| Copier un fichier / un contenu | `ansible.builtin.copy` | `content:` pour du texte inline ; `backup`, `validate`, `remote_src` |
| Fichier dynamique | `ansible.builtin.template` | Jinja2 (module 07) |
| Une ligne dans un fichier | `ansible.builtin.lineinfile` | `regexp` + `line` ; idempotent |
| Un bloc dans un fichier | `ansible.builtin.blockinfile` | marqueurs `# BEGIN/END ANSIBLE MANAGED BLOCK` |
| Remplacer par regex | `ansible.builtin.replace` | toutes les occurrences |
| Infos fichier | `ansible.builtin.stat` | `.stat.exists`, `.mode`, `.checksum`, `.isdir` |
| Chercher | `ansible.builtin.find` | `age`, `size`, `patterns`, `recurse` |
| Récupérer vers le contrôleur | `ansible.builtin.fetch` | |
| Synchroniser (rsync) | `ansible.posix.synchronize` | efficace pour de gros volumes |
| Archives | `community.general.archive`, `ansible.builtin.unarchive` | `remote_src` |
| Télécharger | `ansible.builtin.get_url` | `checksum: sha256:…` obligatoire en prod |
| Fichiers INI/XML/JSON | `community.general.ini_file`, `xml`, `jq`-like via filtres | |
| Assembler | `ansible.builtin.assemble` | concatène `conf.d/` |

**Règle** : pour un fichier géré entièrement → `template`/`copy`. Pour *modifier une ligne* d'un fichier fourni par l'OS → `lineinfile`/`blockinfile`/`ini_file`. Éviter `sed` via `shell`.

## 2. Paquets et dépôts

| Besoin | Module |
|---|---|
| Générique (détecte le gestionnaire) | `ansible.builtin.package` |
| Debian/Ubuntu | `ansible.builtin.apt` (`update_cache`, `cache_valid_time`, `state: latest\|present\|absent`, `deb:`), `ansible.builtin.apt_repository`, `ansible.builtin.deb822_repository`, `ansible.builtin.apt_key` (déprécié → clés dans `/etc/apt/keyrings`) |
| RedHat/Rocky/Fedora | `ansible.builtin.dnf`, `ansible.builtin.yum_repository`, `ansible.builtin.rpm_key` |
| SUSE / Alpine / Arch | `community.general.zypper`, `apk`, `pacman` |
| Python | `ansible.builtin.pip` (privilégier `virtualenv`) |
| Snap / Flatpak / Homebrew | `community.general.snap`, `flatpak`, `homebrew` |
| Collecter les paquets | `ansible.builtin.package_facts` |

**Bonnes pratiques** : liste de paquets en **un seul appel** ; `state: present` plutôt que `latest` (reproductibilité) ; épingler les versions de ce qui compte (`name: nginx=1.24.*`).

## 3. Services et planification

| Besoin | Module |
|---|---|
| Démarrer/arrêter/activer | `ansible.builtin.service` (générique) ou `ansible.builtin.systemd_service` (daemon_reload, masked, scope) |
| Cron | `ansible.builtin.cron` (nommez toujours la tâche) |
| At | `ansible.posix.at` |
| Timers systemd | unité `.timer` via `copy` + `systemd_service` |
| Facts services | `ansible.builtin.service_facts` |
| Redémarrer la machine | `ansible.builtin.reboot` (attend le retour) |

## 4. Utilisateurs et sécurité

| Besoin | Module |
|---|---|
| Utilisateurs / groupes | `ansible.builtin.user` (`password: "{{ pwd \| password_hash('sha512') }}"`), `ansible.builtin.group` |
| Clés SSH | `ansible.posix.authorized_key`, `community.crypto.openssh_keypair` |
| known_hosts | `ansible.builtin.known_hosts` |
| sudoers | `copy` + `validate: visudo -cf %s` |
| Pare-feu | `community.general.ufw`, `ansible.posix.firewalld`, `ansible.builtin.iptables`, `community.general.nftables` |
| SELinux / AppArmor | `ansible.posix.selinux`, `ansible.posix.seboolean`, `community.general.sefcontext`, `apparmor` |
| Certificats | `community.crypto.openssl_privatekey`, `openssl_csr`, `x509_certificate`, `acme_certificate` |
| PAM, limits | `community.general.pam_limits` |

## 5. Système

| Besoin | Module |
|---|---|
| Hostname / fuseau / locale | `ansible.builtin.hostname`, `community.general.timezone`, `community.general.locale_gen` |
| Paramètres noyau | `ansible.posix.sysctl` |
| Montages / disques | `ansible.posix.mount`, `community.general.filesystem`, `lvg`, `lvol`, `parted` |
| Modules noyau | `community.general.modprobe` |
| Swap | `command: fallocate`/`mkswap` + `mount` |
| Facts | `ansible.builtin.setup`, `gather_facts`, `package_facts`, `service_facts`, `mount_facts` |
| Attendre | `wait_for`, `wait_for_connection` |

## 6. Réseau et web

| Besoin | Module |
|---|---|
| Appel HTTP/REST | `ansible.builtin.uri` (`status_code`, `body_format: json`, `return_content`, `validate_certs`) |
| Git | `ansible.builtin.git` |
| Mail / chat | `community.general.mail`, `slack`, `mattermost`, `telegram` |
| DNS | `community.general.nsupdate`, lookup `dig` |
| Équipements réseau | collections `cisco.ios`, `arista.eos`, `junipernetworks.junos`, `ansible.netcommon` (module 17) |

## 7. Exécution de commandes (dernier recours)

| Module | Quand | Idempotence |
|---|---|---|
| `command` | commande simple | `creates`, `removes`, `changed_when` |
| `shell` | pipes, redirections | idem + `set -o pipefail` + `executable: /bin/bash` |
| `script` | script local à exécuter à distance | `creates` |
| `raw` | sans Python (bootstrap, réseau) | non |
| `expect` | commande interactive | `community.general`/`ansible.builtin.expect` |

Patron propre pour une commande non idempotente :

```yaml
- name: Initialiser la base une seule fois
  ansible.builtin.command:
    cmd: /opt/app/bin/init-db
    creates: /var/lib/app/.initialized      # ne rejoue pas si le fichier existe
```

## 8. Données & bases

| Besoin | Collection / module |
|---|---|
| PostgreSQL | `community.postgresql.postgresql_db`, `postgresql_user`, `postgresql_privs`, `postgresql_pg_hba`, `postgresql_alter_system` |
| MySQL/MariaDB | `community.mysql.mysql_db`, `mysql_user` |
| MongoDB, Redis | `community.mongodb`, `community.general.redis` |
| Sauvegarde | `postgresql_db: state=dump`, `archive`, `synchronize` |

> Prérequis Python côté cible : `psycopg2` (`python3-psycopg2`), `PyMySQL`… et `become_user: postgres` pour les connexions socket.

## 9. Conteneurs, cloud, Kubernetes (aperçu, cf. module 17)

`community.docker.docker_container`, `docker_image`, `docker_compose_v2`, `kubernetes.core.k8s`, `helm`, `amazon.aws.ec2_instance`, `azure.azcollection.*`, `google.cloud.*`, `community.vmware.*`, `proxmox_kvm`.

## 10. Contrôle & débogage

| Module | Usage |
|---|---|
| `debug` | afficher (`msg`, `var`, `verbosity: 2`) |
| `assert` / `fail` | valider / échouer volontairement |
| `pause` | attente / confirmation humaine |
| `set_fact`, `include_vars`, `add_host`, `group_by` | variables et inventaire dynamique |
| `meta` | `flush_handlers`, `end_play`, `refresh_inventory`, `clear_facts` |
| `ping` | test de connexion Ansible |

## 11. Lire la valeur de retour d'un module

```yaml
- ansible.builtin.stat: { path: /etc/passwd }
  register: r
- ansible.builtin.debug: { var: r }        # cherchez les clés utiles : r.stat.exists, r.stat.mode…
```

Clés communes à tous les modules : `changed`, `failed`, `msg`, `rc`, `stdout`, `stderr`, `skipped`, `results` (boucles), `diff`, `warnings`.

## 12. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/01-fichiers.yml](demos/01-fichiers.yml) | `file`, `lineinfile`, `blockinfile`, `replace`, `stat`, `find`, `archive`, `unarchive` (exécutable en local) |
| [demos/02-utilisateurs-systeme.yml](demos/02-utilisateurs-systeme.yml) | `user`, `authorized_key`, sudoers validé, `cron`, `timezone`, `sysctl` |
| [demos/03-paquets-services.yml](demos/03-paquets-services.yml) | `package`, `apt`, `pip` venv, `service`, unité systemd |
| [demos/04-reseau-api.yml](demos/04-reseau-api.yml) | `uri`, `get_url`, `wait_for`, `command creates`, `git` |

## 13. 🛠️ Labs

* [Lab 11 — Pile 2-tiers : nginx + PostgreSQL avec contrôle de connectivité](labs/lab-11-stack-2tiers/README.md)

## ✅ Points clés

* Un module dédié > `command` > `shell` > `raw`.
* `lineinfile`/`blockinfile`/`ini_file` pour modifier ; `template` pour posséder le fichier.
* `validate:` avant d'activer une config critique (sudoers, sshd, nginx).
* `creates`/`removes`/`changed_when` quand on doit utiliser `command`.

## ❓ Quiz

1. Quel module ajoute une ligne unique à un fichier ? *(`lineinfile`)*
2. Pourquoi `validate: visudo -cf %s` ? *(ne pas casser sudo avec un fichier invalide)*
3. Comment rendre un `command` idempotent ? *(`creates`/`removes`/`changed_when`)*
4. Quel module attendre qu'un port s'ouvre ? *(`wait_for`)*
