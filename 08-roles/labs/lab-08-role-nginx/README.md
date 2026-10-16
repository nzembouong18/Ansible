# Lab 08 — Écrire un rôle `nginx` multi-OS

⏱️ 1 h 30 · Labo Docker (`webservers`, + `rocky1` si `./lab.sh rocky`).

## 🎯 Objectif

Transformer le playbook du lab 04 en **rôle réutilisable**, paramétrable, multi-OS et validé.

## Cahier des charges

Créez `roles/nginx/` (utilisez `ansible-galaxy role init`) avec :

**Variables (`defaults/main.yml`)** — toutes préfixées `nginx_` :

| Variable | Défaut | Rôle |
|---|---|---|
| `nginx_port` | `80` | port d'écoute |
| `nginx_server_name` | `_` | `server_name` |
| `nginx_root` | `/var/www/html` | racine web |
| `nginx_index_content` | page HTML par défaut | contenu de `index.html` |
| `nginx_worker_connections` | `1024` | (réservé) |
| `nginx_extra_headers` | `{}` | dictionnaire d'en-têtes `add_header` |
| `nginx_enabled` | `true` | service activé au boot |

**Variables internes (`vars/`)** : `Debian.yml` et `RedHat.yml` (nom du paquet, utilisateur, répertoire de conf, chemin du site) chargées via `first_found`.

**Tâches** : `install.yml`, `configure.yml`, `service.yml` importées par `main.yml` avec tags (`nginx_install`, `nginx_configure`, `nginx_service`). La config de vhost est générée par un **template** `site.conf.j2` (boucle sur `nginx_extra_headers`), la configuration est validée avec `nginx -t`.

**Handlers** : « Nginx : recharger ».

**Contrôles** : `assert` sur `nginx_port` (entier 1–65535).

**Plus** : `meta/main.yml` (plateformes) + `meta/argument_specs.yml` + `README.md` du rôle.

## Playbook d'usage

```yaml
- hosts: webservers
  become: true
  roles:
    - role: nginx
      vars:
        nginx_port: 8080
        nginx_extra_headers:
          X-Frame-Options: DENY
          X-Content-Type-Options: nosniff
```

## Validation

```bash
ansible-playbook use-nginx.yml --syntax-check
ansible-lint roles/nginx
ansible-playbook use-nginx.yml            # changed
ansible-playbook use-nginx.yml            # changed=0
curl -si http://localhost:8081            # port mappé de web1 (adaptez si nginx_port change)
ansible-playbook use-nginx.yml --tags nginx_configure --check --diff
ansible-playbook use-nginx.yml -e nginx_port=99999     # doit échouer (assert / argument_specs)
```

**Bonus** : lancez-le sur `rocky1` (`./lab.sh rocky`) et vérifiez que l'utilisateur du processus diffère.

👉 Corrigé : [solution/](solution/)
