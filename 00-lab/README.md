# Module 00 — Mise en place du laboratoire

> **Durée** : 30 min · **Niveau** : débutant · **Prérequis** : Docker (≥ 24) + Docker Compose v2, le client OpenSSH (`ssh-keygen`) sur l'hôte, 4 Go de RAM libres.

Tous les labos de la formation s'exécutent dans un environnement **jetable et reproductible** :

```
                         réseau Docker "lab"
 ┌─────────────┐  SSH   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌──────────────┐
 │   control   │ ─────► │  lb1  │ │ web1  │ │ web2  │ │  db1  │ │ rocky1 (opt) │
 │ ansible,    │        │Ubuntu │ │Ubuntu │ │Ubuntu │ │Ubuntu │ │  Rocky 9     │
 │ lint,       │        │systemd│ │systemd│ │systemd│ │systemd│ │  systemd     │
 │ molecule    │        └───────┘ └───────┘ └───────┘ └───────┘ └──────────────┘
 └─────────────┘         :8080→80  :8081→80  :8082→80
 /workspace = ce dépôt
```

* **control** : le *control node* (là où l'on exécute `ansible-playbook`). Le dépôt est monté dans `/workspace`.
* **lb1, web1, web2, db1** : *managed nodes* Ubuntu 24.04 avec **systemd**, SSH et Python → on peut tester `service`, `systemd`, `apt`, `cron`, `user`… comme sur de vraies VM.
* **rocky1** (profil optionnel) : famille RedHat (`dnf`, `firewalld`, SELinux non actif en conteneur) pour les labos multi-OS.

> ⚠️ Les conteneurs sont `privileged` et la clé SSH est sans mot de passe : **c'est un labo, jamais un modèle de production**.

## 1. Démarrer le labo

```bash
cd 00-lab
./lab.sh up        # génère la clé SSH, construit les images, démarre 5 conteneurs
./lab.sh shell     # ouvre un shell dans le nœud de contrôle
```

Dans le conteneur `control` :

```bash
cd /workspace
ansible --version
ansible all -m ping
```

Résultat attendu :

```
lb1  | SUCCESS => { "changed": false, "ping": "pong" }
web1 | SUCCESS => { "changed": false, "ping": "pong" }
web2 | SUCCESS => { "changed": false, "ping": "pong" }
db1  | SUCCESS => { "changed": false, "ping": "pong" }
```

(`rocky1` ne répond que si vous avez lancé `./lab.sh rocky`.)

## 2. Commandes utiles

| Commande | Effet |
|---|---|
| `./lab.sh up` | démarre le labo |
| `./lab.sh rocky` | ajoute le nœud Rocky Linux |
| `./lab.sh status` | état des conteneurs |
| `./lab.sh reset` | détruit et reconstruit tout (état propre) |
| `./lab.sh down` | arrête le labo |

**Revenir à zéro entre deux labos** : `./lab.sh reset` (~1 min). C'est la vertu de l'infrastructure jetable.

## 3. Alternatives sans Docker

| Option | Comment |
|---|---|
| **VM (Vagrant/VirtualBox, Multipass, libvirt)** | Une VM de contrôle + 4 VM cibles Ubuntu (lb1, web1, web2, db1), éventuellement une Rocky. Adaptez `00-lab/inventory/hosts.yml` (IP, utilisateur). |
| **Cloud gratuit/peu cher** | 5 petites instances (AWS t3.micro, Scaleway DEV1-S, Hetzner CX11). |
| **Tout en local** | `ansible_connection=local` sur `localhost` — suffisant pour les modules 01 à 08, mais pas pour les labos multi-hôtes. |

Vérifiez simplement que vous pouvez faire `ssh ansible@<hote>` sans mot de passe et `sudo` sans mot de passe.

## 4. Conventions de la formation

```
NN-nom-du-module/
├── README.md        ← le cours (théorie + exemples commentés)
├── demos/           ← démonstrations du formateur : à exécuter, lire, modifier
└── labs/
    └── lab-NN-xxx/
        ├── README.md    ← énoncé (objectifs, étapes, critères de validation)
        └── solution/    ← corrigé complet (ne pas regarder avant d'avoir essayé !)
```

Symboles : 🎯 objectif · 🧪 démo · 🛠️ labo · ⚠️ piège classique · 💡 astuce · 🔒 sécurité.

## 5. 🛠️ Lab 00 — Validation de l'environnement

1. Lancez `./lab.sh up` puis `./lab.sh shell`.
2. Exécutez `ansible all -m ping` → 4 `pong`.
3. Exécutez `ansible all -m command -a "uname -a"` → noyau identique (conteneurs) mais **hostnames** différents.
4. Exécutez `ansible web1 -m setup -a "filter=ansible_distribution*"`.
5. Exécutez `ansible all -b -m command -a "id"` → `uid=0(root)` grâce à `become`.

**Validation** : les cinq commandes réussissent. Si `ping` échoue, voir [annexes/troubleshooting.md](../annexes/troubleshooting.md).
