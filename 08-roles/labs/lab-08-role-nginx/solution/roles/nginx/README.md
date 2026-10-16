# Rôle nginx

Installe et configure nginx (Debian/Ubuntu, RedHat/Rocky).

## Variables

| Variable | Défaut | Description |
|---|---|---|
| `nginx_port` | `80` | port d'écoute |
| `nginx_server_name` | `_` | server_name |
| `nginx_root` | `/var/www/html` | racine web |
| `nginx_index_content` | page HTML | contenu de index.html |
| `nginx_extra_headers` | `{}` | en-têtes HTTP (nom: valeur) |
| `nginx_enabled` | `true` | activer au boot |

## Exemple

```yaml
- hosts: webservers
  become: true
  roles:
    - role: nginx
      vars:
        nginx_port: 8080
        nginx_extra_headers: { X-Frame-Options: DENY }
```

Tags : `nginx_install`, `nginx_configure`, `nginx_service`.
