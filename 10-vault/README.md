# Module 10 — Ansible Vault et gestion des secrets

> **Durée** : 2 h · **Niveau** : intermédiaire

## 🎯 Objectifs

* Chiffrer fichiers et valeurs avec `ansible-vault`.
* Structurer variables publiques / secrets (`vars.yml` + `vault.yml`).
* Utiliser plusieurs mots de passe (`--vault-id`) : dev / prod.
* Éviter les fuites : `no_log`, permissions, `.gitignore`.
* Connaître les alternatives (HashiCorp Vault, SOPS, gestionnaires cloud).

> ⚠️ Dans cette formation les mots de passe Vault des démos (`formation-lab-only`) sont **publics et réservés au labo**. En production, jamais dans Git.

---

## 1. Principe

Vault chiffre (AES-256) des fichiers ou des valeurs. Ansible les déchiffre **en mémoire** à l'exécution, si on lui fournit le mot de passe.

```bash
ansible-vault create group_vars/prod/vault.yml          # crée et ouvre $EDITOR
ansible-vault encrypt secrets.yml                        # chiffre un fichier existant
ansible-vault edit group_vars/prod/vault.yml             # édite (déchiffre/rechiffre)
ansible-vault view group_vars/prod/vault.yml             # lit
ansible-vault decrypt secrets.yml                        # déchiffre sur disque (à éviter)
ansible-vault rekey group_vars/prod/vault.yml            # change le mot de passe
ansible-vault encrypt_string 'S3cr3t!' --name 'db_password'   # valeur inline
```

Fournir le mot de passe :

```bash
ansible-playbook site.yml --ask-vault-pass                       # saisie interactive
ansible-playbook site.yml --vault-password-file ~/.vault_pass    # fichier (chmod 600, hors dépôt !)
ansible-playbook site.yml --vault-password-file ./vault-pass.sh  # SCRIPT exécutable (stdout = mot de passe)
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass                 # ou dans ansible.cfg : vault_password_file
```

Un fichier chiffré commence par `$ANSIBLE_VAULT;1.1;AES256` ; il peut donc être **commité** sans risque (tant que le mot de passe ne l'est pas).

## 2. Fichier chiffré vs valeur inline

| | Fichier entier | `encrypt_string` inline |
|---|---|---|
| Lisibilité des diffs Git | illisible | clés visibles, seules les valeurs chiffrées |
| Granularité | tout le fichier | une valeur |
| Recommandation | **préféré** (pattern ci-dessous) | utile pour 1-2 valeurs |

### Le pattern `vars.yml` + `vault.yml`

```
group_vars/prod/
├── vars.yml      # db_password: "{{ vault_db_password }}"     ← clair, lisible, grep-able
└── vault.yml     # vault_db_password: S3cr3t!                 ← chiffré
```

Avantage : on voit **quelles variables existent** (et d'où elles viennent) sans déchiffrer. Convention : préfixe `vault_` pour les variables secrètes.

## 3. Plusieurs coffres : `--vault-id`

Un mot de passe par environnement/équipe :

```bash
ansible-vault create --vault-id dev@prompt group_vars/dev/vault.yml
ansible-vault encrypt --vault-id prod@~/.vault_prod group_vars/prod/vault.yml

ansible-playbook site.yml \
  --vault-id dev@~/.vault_dev \
  --vault-id prod@~/.vault_prod
```

L'étiquette (`dev`, `prod`) est stockée dans l'en-tête du fichier (`$ANSIBLE_VAULT;1.2;AES256;prod`) ; Ansible essaie les mots de passe fournis. Un développeur n'a ainsi que le mot de passe `dev`.

## 4. Ne pas fuiter les secrets

1. **`no_log: true`** sur toute tâche qui manipule un secret (sinon visible en `-v`, dans AWX, dans les logs).
2. Permissions des fichiers générés : `mode: "0600"`, `owner`.
3. Ne **jamais** passer un secret en `-e` (historique shell, `ps`).
4. `.gitignore` pour les fichiers de mot de passe et sorties de debug.
5. Attention à `debug: var=` d'un secret !
6. `ansible-vault decrypt` écrit en clair sur disque : préférez `view`/`edit`.
7. Hooks pre-commit : détecter les fichiers `vault.yml` **non** chiffrés (`grep -L ANSIBLE_VAULT`).
8. Rotation : `rekey` + changement effectif du secret côté service.

```yaml
- name: Créer l'utilisateur de base
  community.postgresql.postgresql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
  no_log: true
```

## 5. Intégration CI / AWX

* **CI** : le mot de passe vient d'un secret du CI (variable masquée) écrit dans un fichier temporaire ou fourni par script `vault-pass.sh` lisant l'environnement.
* **AWX/AAP** : un *Credential* de type « Vault » stocke le mot de passe, jamais dans le dépôt.

## 6. Alternatives & compléments

| Solution | Quand |
|---|---|
| **HashiCorp Vault** (`community.hashi_vault`) | secrets centralisés, dynamiques, rotation, audit |
| **AWS Secrets Manager / SSM** (`amazon.aws.aws_secret`, `ssm_parameter`) | environnements AWS |
| **Azure Key Vault**, **GCP Secret Manager** | idem Azure / GCP |
| **SOPS** + `community.sops` | secrets dans Git chiffrés avec KMS/age/PGP |
| **1Password / Bitwarden / pass** (lookups) | gestionnaires d'équipe |

Exemple de lookup externe (secret jamais stocké dans le dépôt) :

```yaml
db_password: "{{ lookup('community.hashi_vault.hashi_vault', 'secret=kv/data/app:db_password url=https://vault:8200') }}"
```

Voir aussi le module 19 (sécurité).

## 7. Dépannage

| Message | Cause |
|---|---|
| `Attempting to decrypt but no vault secrets found` | aucun mot de passe fourni |
| `Decryption failed (no vault secrets were found that could decrypt)` | mauvais mot de passe / mauvais `vault-id` |
| Variable `!vault` affichée telle quelle | oubli du `--vault-password-file` avec `-e @vault.yml` |
| Fichier devenu illisible dans Git | éditer avec `ansible-vault edit`, pas un éditeur direct |

## 8. 🧪 Démos

Dossier [demos/](demos/) — mot de passe : voir `demos/.vault_pass_lab`.

| Démo | Contenu |
|---|---|
| [group_vars/all/](demos/group_vars/all) | pattern `vars.yml` + `vault.yml` (chiffré) |
| [01-utiliser-vault.yml](demos/01-utiliser-vault.yml) | utilisation + `no_log` + permissions |
| [02-inline.yml](demos/02-inline.yml) | valeur `!vault` inline |
| [scripts/vault-pass.sh](demos/scripts/vault-pass.sh) | mot de passe fourni par script |

```bash
cd 10-vault/demos
ansible-vault view group_vars/all/vault.yml --vault-password-file .vault_pass_lab
ansible-playbook 01-utiliser-vault.yml --vault-password-file .vault_pass_lab
ANSIBLE_VAULT_LAB_PASSWORD=formation-lab-only ansible-playbook 02-inline.yml --vault-password-file scripts/vault-pass.sh
```

## 9. 🛠️ Labs

* [Lab 10 — Secrets multi-environnements (dev/prod) avec vault-id](labs/lab-10-vault/README.md)

## ✅ Points clés

* Chiffrer des **fichiers** (`vault.yml`) référencés par des variables `vault_*`.
* `--vault-id` pour séparer les environnements ; mot de passe hors dépôt.
* `no_log: true`, `mode: "0600"`, pas de secrets dans `-e`.
* Pour de la rotation/dynamique : coffre externe.

## ❓ Quiz

1. Peut-on commiter un fichier chiffré par Vault ? *(Oui, mais jamais le mot de passe)*
2. Pourquoi le pattern `vars.yml` + `vault.yml` ? *(lisibilité : on voit les noms sans déchiffrer)*
3. Comment masquer une tâche dans les logs ? *(`no_log: true`)*
4. Comment gérer dev et prod avec des mots de passe distincts ? *(`--vault-id`)*
