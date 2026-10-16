# Module 03 — Commandes ad-hoc

> **Durée** : 1 h 30 · **Niveau** : débutant

## 🎯 Objectifs

* Lancer une action unique sur N machines sans écrire de playbook.
* Connaître les modules les plus utiles en ad-hoc.
* Utiliser `become`, `--limit`, `-f`, `-o`, `-v`.
* Savoir quand passer au playbook.

## 1. Syntaxe

```
ansible <pattern> -m <module> -a "<arguments>" [options]
```

| Option | Rôle |
|---|---|
| `-i` | inventaire |
| `-m` | module (défaut : `command`) |
| `-a` | arguments « clé=valeur » ou chaîne (command/shell) |
| `-b` / `--become` | élévation (sudo) ; `-K` demande le mot de passe sudo |
| `-u`, `--private-key` | utilisateur / clé SSH |
| `-f N` | parallélisme (*forks*, défaut 5) |
| `-l` | limiter à un sous-ensemble |
| `-C` / `-D` | check / diff |
| `-e` | variables supplémentaires (`-e "x=1"` ou `-e @fichier.yml`) |
| `-v … -vvvv` | verbosité |
| `-t DIR` | sauvegarde la sortie en fichiers par hôte |

## 2. Les modules incontournables

```bash
# Connectivité (SSH + Python OK ?) — ce n'est PAS un ICMP ping
ansible all -m ansible.builtin.ping

# Exécuter une commande (sans shell : pas de pipe, pas de variable d'environnement)
ansible all -m ansible.builtin.command -a "uptime"
# Exécuter dans un shell (pipes, redirections, globs)
ansible all -m ansible.builtin.shell -a "ps aux | wc -l"

# Facts
ansible web1 -m ansible.builtin.setup
ansible web1 -m ansible.builtin.setup -a "filter=ansible_distribution*"
ansible all  -m ansible.builtin.setup -a "gather_subset=network filter=ansible_default_ipv4"

# Fichiers
ansible all -m ansible.builtin.copy  -a "src=./motd dest=/etc/motd mode=0644" -b
ansible all -m ansible.builtin.file  -a "path=/opt/x state=directory mode=0755" -b
ansible all -m ansible.builtin.fetch -a "src=/etc/hostname dest=./collected/ "

# Paquets / services
ansible webservers -b -m ansible.builtin.package -a "name=nginx state=present"
ansible webservers -b -m ansible.builtin.service -a "name=nginx state=started enabled=true"
ansible webservers -b -m ansible.builtin.apt     -a "update_cache=true upgrade=safe"   # Debian/Ubuntu
ansible rocky      -b -m ansible.builtin.dnf     -a "name=htop state=latest"           # RedHat

# Utilisateurs
ansible all -b -m ansible.builtin.user -a "name=alice groups=sudo shell=/bin/bash"

# Exécuter un script local sur les cibles
ansible all -m ansible.builtin.script -a "./check.sh"

# Redémarrage + attente
ansible all -b -m ansible.builtin.reboot

# Dépannage sans Python sur la cible
ansible newhost -m ansible.builtin.raw -a "apt-get install -y python3"
```

### `command` vs `shell` vs `raw` vs `script`

| Module | Shell ? | Python requis ? | Usage |
|---|---|---|---|
| `command` | non | oui | **défaut**, plus sûr (pas d'injection) |
| `shell` | oui (`/bin/sh`) | oui | pipes, `&&`, redirections |
| `script` | via interpréteur | non* | exécuter un script local à distance |
| `raw` | oui | **non** | bootstrap, équipements réseau |

## 3. Cas d'usage réels

| Besoin | Commande |
|---|---|
| Qui répond ? | `ansible all -m ping` |
| Espace disque partout | `ansible all -m command -a "df -h /"` |
| Version d'un paquet | `ansible all -m command -a "dpkg -s openssl"` |
| Redémarrer un service sur un seul hôte | `ansible web1 -b -m service -a "name=nginx state=restarted"` |
| Mise à jour de sécurité d'urgence | `ansible all -b -m apt -a "name=openssl state=latest update_cache=yes"` |
| Collecter un fichier | `ansible all -m fetch -a "src=/var/log/syslog dest=logs/"` |
| Inventaire matériel rapide | `ansible all -m setup -a "filter=ansible_memtotal_mb"` |

## 4. Lire la sortie

```
web1 | CHANGED => {"changed": true, "stdout": "...", "rc": 0}
web2 | FAILED  => {"msg": "...", "rc": 1}
db9  | UNREACHABLE! => {"msg": "Failed to connect to the host via ssh"}
```

* `SUCCESS` (ok) / `CHANGED` / `FAILED` / `UNREACHABLE`
* ⚠️ `-o` (sortie sur une ligne) est **déprécié** (retiré en ansible-core 2.23). Alternative : `ansible … | grep -E "SUCCESS|FAILED"` ou le callback `ansible.posix.json`/`yaml`.
* Code retour d'`ansible` : 0 OK, 2 échec(s), 4 injoignable(s).

## 5. Ad-hoc ou playbook ?

* **Ad-hoc** : diagnostic, action ponctuelle, exploration d'un module.
* **Playbook** : tout ce qui doit être **répété**, relu, versionné ou audité.
* Règle : si vous tapez la même commande ad-hoc deux fois, écrivez un playbook.

## 6. 🧪 Démo

[`demos/adhoc-tour.sh`](demos/adhoc-tour.sh) déroule une visite guidée (à lancer depuis le conteneur `control`) : ping, facts, fichiers, services, parallélisme, `--limit`.

## 7. 🛠️ Lab

* [Lab 03 — Dépannage et administration en ad-hoc](labs/lab-03-adhoc/README.md)

## ✅ Points clés

* Ad-hoc = `ansible <cible> -m <module> -a "<args>"`.
* Préférez `command` à `shell`, un vrai module à `command`.
* `-b` pour les privilèges, `-l`/pattern pour cibler, `-f` pour paralléliser.

## ❓ Quiz

1. Quel module sert à tester la connectivité Ansible ? *(`ping`)*
2. Différence `command` / `shell` ? *(shell interprète pipes/redirections)*
3. Quel module sans Python sur la cible ? *(`raw`)*
4. Que fait `-f 20` ? *(20 hôtes en parallèle)*
