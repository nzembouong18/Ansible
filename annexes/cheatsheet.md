# Aide-mémoire Ansible

## Commandes

```bash
ansible all -m ping                                  # connectivité
ansible web -b -m apt -a "name=nginx state=present"  # ad-hoc (-b = become)
ansible-playbook site.yml -i inv -l web1 -t config   # limiter hôtes / tags
ansible-playbook site.yml --check --diff             # simulation
ansible-playbook site.yml --syntax-check | --list-tasks | --list-hosts | --list-tags
ansible-playbook site.yml --start-at-task "X" | --step
ansible-playbook site.yml -e "k=v" -e @vars.yml -vvv -f 20
ansible-inventory -i inv --graph | --list | --host web1
ansible-doc -l | ansible-doc ansible.builtin.copy | ansible-doc -t filter -l
ansible-config dump --only-changed
ansible-galaxy collection install -r requirements.yml -p ./collections
ansible-galaxy role init monrole
ansible-vault create|edit|view|encrypt|decrypt|rekey|encrypt_string
ansible-lint ; yamllint . ; molecule test
ansible-navigator run site.yml -m stdout --eei mon-ee:1.0
```

## Structure d'un playbook

```yaml
---
- name: Description du play
  hosts: webservers
  become: true
  gather_facts: true
  serial: 2
  vars: { k: v }
  vars_files: [vars/main.yml]
  pre_tasks: []
  roles: [common, { role: nginx, nginx_port: 8080 }]
  tasks:
    - name: Verbe + objet
      ansible.builtin.package: { name: nginx, state: present }
      when: ansible_facts['os_family'] == 'Debian'
      loop: "{{ liste }}"
      register: r
      notify: Recharger nginx
      tags: [web]
      no_log: false
      changed_when: false
      failed_when: r.rc > 1
      delegate_to: localhost
      run_once: true
      retries: 3
      delay: 5
      until: r is succeeded
  post_tasks: []
  handlers:
    - name: Recharger nginx
      ansible.builtin.service: { name: nginx, state: reloaded }
```

## Modules à connaître

| Domaine | Modules |
|---|---|
| Fichiers | file, copy, template, lineinfile, blockinfile, replace, stat, find, fetch, unarchive, get_url, synchronize |
| Paquets | package, apt, dnf, pip, apt_repository |
| Services | service, systemd_service, cron, reboot |
| Utilisateurs | user, group, authorized_key, sudoers via copy+validate |
| Système | hostname, timezone, sysctl, mount, ufw, firewalld, selinux |
| Réseau/Web | uri, wait_for, git |
| Commandes | command, shell, script, raw |
| Contrôle | debug, assert, fail, set_fact, include_vars, add_host, group_by, meta, pause |

## Variables : précédence (faible → fort)

`defaults` du rôle < inventaire (`group_vars/all` < groupes < `host_vars`) < facts < `vars` du play < `vars_files` < `vars` du rôle < bloc < tâche < `include_vars` < `set_fact`/`register` < paramètres de rôle < **`-e`**

## Variables magiques

`inventory_hostname`, `group_names`, `groups`, `hostvars`, `ansible_play_hosts`, `ansible_play_batch`, `playbook_dir`, `ansible_check_mode`, `omit`

## Jinja2

```jinja
{{ var | default('x') }}   {{ list | join(',') }}   {{ d | combine(e) }}   {{ l | map(attribute='n') | list }}
{{ l | selectattr('a') | list }}   {{ s | regex_replace('^v','') }}   {{ d | dict2items }}   {{ x | to_nice_yaml }}
{% if cond %}…{% elif %}…{% else %}…{% endif %}   {% for i in l %}…{% endfor %}   {# commentaire #}
```

## Patterns d'hôtes

`all` · `web1:web2` · `webservers:!web2` · `webservers:&prod` · `~web[0-9]+` · `webservers[0]`

## Bonnes pratiques en 12 lignes

1. FQCN et `name:` partout. 2. `state:` explicite. 3. Modules > command > shell.
4. Idempotence : `changed=0` au 2ᵉ passage. 5. `defaults/` pour l'interface d'un rôle, variables préfixées.
6. `validate:` sur les configs critiques. 7. Handlers pour les redémarrages.
8. Secrets : Vault/coffre + `no_log`. 9. `mode: "0644"` entre guillemets.
10. `--check --diff` avant la prod. 11. `serial` + health check + rollback.
12. lint + Molecule + CI pour tout.
