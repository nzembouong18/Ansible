# Module 19 — Sécurité et durcissement

> **Durée** : 3 h · **Niveau** : expert

## 🎯 Objectifs

* Sécuriser **Ansible lui-même** (accès, secrets, chaîne d'approvisionnement).
* Appliquer et **auditer** un durcissement de base (SSH, noyau, fichiers, mots de passe).
* Gérer les secrets avec des coffres externes et `no_log`.
* Appliquer le moindre privilège (`become`, sudoers).

---

## 1. Menaces propres à Ansible

Le contrôleur est une **clé maîtresse** : il peut tout faire sur tout le parc.

| Risque | Parade |
|---|---|
| Vol de la clé SSH du contrôleur | clé protégée (passphrase + agent), clés par environnement, certificats SSH à courte durée |
| Contrôleur compromis | durcir/isoler (bastion, EE jetables dans AWX), journaliser, MFA |
| Secrets en clair (Git, logs) | Vault / coffre externe, `no_log`, `.gitignore`, détection (pre-commit, gitleaks) |
| Code malveillant (rôle/collection tiers) | épingler les versions, relire, miroir interne, `ansible-galaxy collection verify`, signatures |
| Playbook modifié sans revue | PR obligatoires, branches protégées, commits signés, CI |
| Élévation excessive | `become` ciblé, sudoers restreint, utilisateur dédié non-root |
| Traces perdues | logs AWX, `log_path`, SIEM |

## 2. Accès et privilèges

* Connexion par **clé** (jamais de mot de passe SSH), utilisateur dédié `ansible`/`deploy`.
* `become` **par tâche/play** plutôt que `become: true` global quand c'est possible.
* sudoers **restreint** par commandes (voir [demos/05-sudoers-moindre-privilege.yml](demos/05-sudoers-moindre-privilege.yml)), toujours avec `validate: visudo -cf %s`.
* `host_key_checking = True` en production (pas de désactivation par confort) ; distribuer `known_hosts` via `ansible.builtin.known_hosts`.
* Certificats SSH signés par une CA interne (validité courte) : `community.crypto.openssh_cert`.
* Bastion : `ansible_ssh_common_args: "-o ProxyJump=bastion"`.

## 3. Secrets

Hiérarchie de maturité :

1. Mots de passe en clair dans Git → **à bannir**.
2. **Ansible Vault** (module 10) : bon point de départ.
3. **Coffre externe** (HashiCorp Vault, AWS/Azure/GCP, SOPS) : rotation, audit, secrets dynamiques → [demos/04-secrets-externes.yml](demos/04-secrets-externes.yml).
4. **Identités managées** (IAM role, Workload Identity) : plus de secret du tout.

`no_log: true` + `loop_control.label` : [demos/03-no-log-secrets.yml](demos/03-no-log-secrets.yml) montre ce qui fuite avec `-v`.

Autres règles : `mode: "0600"` sur les fichiers secrets, pas de secret en `-e` ni dans `environment:` visible dans `ps`, `ANSIBLE_NO_LOG`/`display_args_to_stdout = False`, attention aux `register` contenant des secrets (ils vivent en mémoire et peuvent apparaître dans le cache de facts !).

## 4. Chaîne d'approvisionnement

* `requirements.yml` avec **versions exactes** ou plages bornées.
* Miroir/Private Automation Hub ; pas d'installation directe depuis Internet en production.
* `ansible-galaxy collection install --signature …` / `verify` avec le trousseau GPG.
* EE (module 18) **scannés** (Trivy/Grype) et reconstruits régulièrement.
* Dépendances Python : `pip-audit`, hashes (`--require-hashes`).
* Revue des `shell`/`command`/`get_url` dans les rôles tiers ; `get_url` avec `checksum`.

## 5. Durcissement des systèmes

Le rôle [demos/roles/hardening](demos/roles/hardening) implémente un socle (inspiré CIS / ANSSI BP-028, **non exhaustif**) :

| Domaine | Mesures |
|---|---|
| SSH | root interdit, mot de passe désactivé, `MaxAuthTries`, pas de forwarding, bannière, `AllowGroups`, **validation `sshd -t`** |
| Noyau / réseau | `rp_filter`, pas de redirections ICMP, SYN cookies, ASLR, `suid_dumpable` |
| Fichiers | permissions de `/etc/shadow`, `passwd`, `group` |
| Comptes | `PASS_MAX_DAYS`, `PASS_MIN_DAYS`, `UMASK 027` |
| Légal | bannière d'avertissement |

À compléter selon le référentiel visé : `auditd`, `fail2ban`, pare-feu (`ufw`/`firewalld`/`nftables`), mises à jour de sécurité automatiques, partitions (`nodev,nosuid,noexec`), SELinux/AppArmor en mode *enforcing*, désactivation des services inutiles, NTP/journald, intégrité (AIDE).

Référentiels prêts à l'emploi : rôles **DevSec** (`devsec.hardening` : os_hardening, ssh_hardening, nginx…), **ansible-lockdown** (CIS/STIG), OpenSCAP (`oscap` + remédiations Ansible).

### ⚠️ Ne pas s'enfermer dehors

Avant de désactiver l'authentification par mot de passe : vérifier la présence de la clé (lab 19), garder une **seconde session ouverte**, appliquer sur **un hôte** (`--limit`, `serial: 1`) puis étendre, valider la config **avant** rechargement (`validate:`), prévoir un accès console.

## 6. Auditer : contrôler sans modifier

[demos/02-audit.yml](demos/02-audit.yml) évalue des contrôles en `check_mode` et produit un **score** :

```
Avant durcissement : Score 1/5      Après : Score 5/5
```

Pistes : exporter en JSON (callback `json`/artefacts), envoyer vers un tableau de bord, planifier l'audit dans AWX et alerter sur la dérive. Pour un audit exhaustif : OpenSCAP, Lynis, InSpec (`ansible` pour appliquer, InSpec pour vérifier).

## 7. Sécurité des playbooks (revue)

Checklist de revue de PR :

- [ ] Aucun secret en clair ; `no_log` là où nécessaire
- [ ] Modules dédiés plutôt que `shell` ; entrées validées (`quote`, `assert`)
- [ ] Permissions explicites (`mode`, `owner`, `group`) — règle `risky-file-permissions`
- [ ] `validate:` sur sshd/sudoers/nginx
- [ ] `become` minimal ; pas de `chmod 777`
- [ ] Téléchargements avec `checksum` ; versions épinglées
- [ ] Idempotent, `--check` passe, Molecule vert
- [ ] Impact sur l'accès (SSH, firewall) pris en compte

`ansible-lint` (profil `production`) couvre une partie : `risky-file-permissions`, `no-log-password`, `risky-shell-pipe`, `command-instead-of-shell`.

## 8. Conformité et traçabilité

* Tout changement passe par Git (qui, quoi, pourquoi) et AWX (qui a lancé quoi, quand, sur quoi).
* Conserver les logs d'exécution (rétention légale), centraliser (syslog, ELK, Splunk).
* Séparer les rôles : qui écrit ≠ qui approuve ≠ qui déploie en prod (workflows avec approbation).
* Documenter les exceptions (`# noqa:` justifiés).

## 9. 🧪 Démos

| Démo | Contenu |
|---|---|
| [roles/hardening](demos/roles/hardening) | rôle de durcissement (testé réellement) |
| [01-appliquer-durcissement.yml](demos/01-appliquer-durcissement.yml) | application du rôle |
| [02-audit.yml](demos/02-audit.yml) | audit en lecture seule avec score |
| [03-no-log-secrets.yml](demos/03-no-log-secrets.yml) | fuite vs `no_log` |
| [04-secrets-externes.yml](demos/04-secrets-externes.yml) | Vault HashiCorp, AWS, Azure, SOPS |
| [05-sudoers-moindre-privilege.yml](demos/05-sudoers-moindre-privilege.yml) | sudoers restreint |

## 10. 🛠️ Labs

* [Lab 19 — Durcir les serveurs du labo et mesurer la conformité](labs/lab-19-durcissement/README.md)

## ✅ Points clés

* Le contrôleur est la cible n°1 : le protéger comme un actif critique.
* Secrets : Vault → coffre externe → identités managées ; `no_log` toujours.
* Durcir = appliquer **et** auditer, avec garde-fous anti-verrouillage.
* Chaîne d'approvisionnement : versions épinglées, miroir, signatures.

## ❓ Quiz

1. Pourquoi `validate: sshd -t` ? *(ne pas casser SSH avec une configuration invalide)*
2. Que fait `no_log: true` ? *(masque arguments et résultat de la tâche)*
3. Comment limiter ce qu'un utilisateur de déploiement peut faire ? *(sudoers par commandes, `Cmnd_Alias`)*
4. Quel est le plus haut niveau de maturité pour les secrets ? *(identités managées : aucun secret stocké)*
