# Dépannage

## Le labo Docker

| Symptôme | Cause probable | Solution |
|---|---|---|
| `ansible all -m ping` : `UNREACHABLE` / `Permission denied (publickey)` | clé non générée ou non montée | `./lab.sh reset` ; vérifier `00-lab/keys/id_ed25519(.pub)` |
| `Connection refused` | sshd pas encore démarré | attendre 10 s ; `docker exec web1 systemctl status ssh` |
| `Failed to connect ... Host key verification failed` | clé d'hôte changée après `reset` | `rm ~/.ssh/known_hosts` dans `control` (ou `host_key_checking=False`) |
| Conteneurs ne démarrent pas (systemd) | cgroups v2 / droits | Docker ≥ 24, Linux ou Docker Desktop récent ; option `cgroup: host` du compose |
| `service`/`systemd` échouent | systemd non initialisé | `docker logs web1` ; relancer `./lab.sh reset` |
| `No space left on device` | images Docker volumineuses | `docker system prune -af` |
| Port 8080/8081 déjà pris | autre service local | modifier le mappage dans `docker-compose.yml` |
| Rocky : `python3` introuvable | image modifiée | reconstruire avec `./lab.sh rocky` |

## Erreurs Ansible fréquentes

| Message | Piste |
|---|---|
| `Syntax Error while loading YAML` | indentation / guillemets (ligne indiquée) ; valeur commençant par `{{` entre guillemets |
| `'x' is undefined` | précédence, faute de frappe, `default()` ; `ansible-inventory --host` |
| `couldn't resolve module/action` | collection absente → `ansible-galaxy collection install` ; FQCN |
| `Conditional result was derived from type 'str'` | `when` non booléen (ansible-core ≥ 2.19) → `| bool` ou comparaison explicite |
| `Missing sudo password` | `become` sans NOPASSWD → `-K` ou sudoers |
| `Could not import the python3-apt module` | mauvais interpréteur → `ansible_python_interpreter: /usr/bin/python3` |
| `Shared connection to ... closed` / `MODULE FAILURE` | `-vvv` ; Python manquant ; espace disque ; `/tmp` en `noexec` |
| `A vault password must be specified` | `--vault-password-file` / `--ask-vault-pass` / `--vault-id` |
| `Decryption failed` | mauvais mot de passe ou mauvais vault-id |
| Changed perpétuel | tâche non idempotente (`command` sans `creates`, template avec date) → `--diff` |
| `The role 'x' was not found` | `roles_path`, répertoire courant, `ansible.cfg` utilisé (`ansible --version`) |
| Handlers non exécutés | tâche notifiante échouée ou non `changed` ; `meta: flush_handlers` |
| Variable `namespace` / `environment` bizarre | nom réservé → préfixer |

## Méthode de dépannage

1. **Reproduire** sur un seul hôte : `-l web1`.
2. **Voir** : `-vvv`, `--diff`, `--check`.
3. **Isoler** : `--start-at-task`, `--step`, `--tags`.
4. **Inspecter** : `debug var=`, `ansible-inventory --host`, `setup`.
5. **Corriger** puis **rejouer deux fois** (idempotence).
6. **Capitaliser** : test Molecule ou `assert` pour ne plus régresser.
