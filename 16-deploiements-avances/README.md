# Module 16 — Déploiements avancés et orchestration

> **Durée** : 3 h · **Niveau** : expert

## 🎯 Objectifs

* Orchestrer des opérations multi-tiers dans le bon ordre.
* Mettre à jour **sans interruption** : `serial`, `delegate_to`, health checks, rollback.
* Connaître les stratégies de déploiement : rolling, canary, blue/green.
* Utiliser `run_once`, `delegate_facts`, `throttle`, `wait_for`, `reboot`.
* Découvrir `ansible-pull` et les patchs OS orchestrés.

---

## 1. Orchestrer plusieurs tiers

Un `site.yml` enchaîne des plays dans l'ordre métier :

```yaml
- import_playbook: db.yml          # 1. base (migration de schéma)
- import_playbook: app.yml         # 2. application
- import_playbook: web.yml         # 3. frontaux + LB
- import_playbook: smoke-tests.yml # 4. vérifications de bout en bout
```

Pour utiliser les facts d'un tier dans un autre (`hostvars[db1].ansible_facts…`), le play qui les collecte doit s'être exécuté **avant** dans la même exécution (ou cache de facts).

## 2. `serial` : déployer par lots

```yaml
- hosts: webservers
  serial: 1                       # un par un
  # serial: "25%"                 # 25 % du parc
  # serial: [1, 5, "100%"]        # canari, puis 5, puis tout le reste
  max_fail_percentage: 0          # au premier échec : on arrête TOUT le play
  any_errors_fatal: false
```

Variables utiles : `ansible_play_batch`, `ansible_play_hosts`, `ansible_play_hosts_all`.

⚠️ Avec `serial`, les **handlers** s'exécutent à la fin de **chaque lot**.

## 3. `delegate_to`, `run_once`, `delegate_facts`

```yaml
- name: Retirer le serveur du load balancer       # s'exécute SUR le LB, avec les variables du serveur courant
  community.general.haproxy:
    backend: web_pool
    host: "{{ inventory_hostname }}"
    state: disabled
    drain: true
    wait: true
  delegate_to: lb1

- name: Migrer le schéma (une seule fois)
  ansible.builtin.command: /opt/app/migrate
  run_once: true                  # exécuté sur le 1er hôte du lot… attention avec serial !
  delegate_to: "{{ groups['appservers'][0] }}"

- name: Collecter les facts d'un autre hôte
  ansible.builtin.setup:
  delegate_to: db1
  delegate_facts: true            # stocke les facts dans hostvars['db1'], pas dans l'hôte courant
```

* `delegate_to: localhost` (ou `connection: local`) = appel d'API, notification, requêtes `uri` depuis le contrôleur.
* ⚠️ `run_once` + `serial` : `run_once` s'applique **à chaque lot**. Pour « une fois pour tout le play », utilisez `when: inventory_hostname == ansible_play_hosts_all[0]`.
* ⚠️ Les tâches déléguées utilisent les variables de connexion de la **cible de délégation** (`ansible_host`…) mais les variables métier de l'hôte courant.

## 4. Stratégies de déploiement

| Stratégie | Principe | Avantage | Mise en œuvre Ansible |
|---|---|---|---|
| **Rolling** | un lot à la fois | pas d'interruption, simple | `serial`, retrait/ajout LB |
| **Canary** | un petit sous-ensemble d'abord, puis le reste | limite le risque | `serial: [1, "100%"]` + pause/validation (`pause:`) |
| **Blue/Green** | deux environnements, on bascule | retour arrière instantané | lien symbolique / LB / DNS ; voir [demos/03-blue-green.yml](demos/03-blue-green.yml) |
| **Recreate** | tout arrêter puis déployer | simple | fenêtre de maintenance |
| **Immuable** | remplacer les machines (image) | reproductible | Terraform/Packer + Ansible pour la configuration de l'image |

### Patron d'un rolling update

```
Pour chaque lot (serial) :
  1. [LB]  désactiver / drainer le serveur
  2. [SRV] arrêter le service, déployer, migrer, démarrer
  3. [SRV] health check (wait_for / uri + retries)
  4. [LB]  réactiver le serveur
  5. en cas d'échec : rescue → rollback → arrêt du play (max_fail_percentage: 0)
Fin : smoke test global.
```

Implémenté dans le [lab 16](labs/lab-16-rolling-update/README.md).

## 5. Attentes et vérifications

```yaml
- ansible.builtin.wait_for:
    port: 8080
    host: "{{ ansible_host }}"
    delay: 2
    timeout: 60
    state: started

- ansible.builtin.uri:
    url: "http://{{ ansible_host }}:8080/health"
    status_code: 200
  register: h
  until: h.status == 200
  retries: 20
  delay: 3

- ansible.builtin.wait_for_connection:          # après un reboot
    delay: 5
    timeout: 300
```

## 6. Mises à jour de l'OS et redémarrages orchestrés

```yaml
- hosts: all
  serial: "20%"
  tasks:
    - ansible.builtin.apt:
        upgrade: dist
        update_cache: true
      become: true
      register: upgrade

    - name: Redémarrer si nécessaire
      ansible.builtin.stat:
        path: /var/run/reboot-required
      register: reboot_required

    - ansible.builtin.reboot:
        reboot_timeout: 600
        msg: "Redémarrage planifié par Ansible"
      become: true
      when: reboot_required.stat.exists
```

Famille RedHat : `needs-restarting -r` (retour 1 = reboot nécessaire). Coordonnez avec le LB et le monitoring (fenêtre de maintenance : `uri` vers Alertmanager/Nagios).

## 7. `ansible-pull` : le modèle « pull »

Au lieu de pousser depuis un contrôleur, chaque machine **tire** régulièrement sa configuration depuis Git :

```bash
ansible-pull -U https://git.example.com/infra.git -C main -i localhost, local.yml
```

| Push (ansible-playbook) | Pull (ansible-pull) |
|---|---|
| Contrôle central, immédiat | Passage à l'échelle, tolère les machines hors ligne |
| Nécessite l'accès réseau vers les cibles | Les cibles sortent vers Git (NAT, edge, postes) |
| Résultats centralisés | Résultats à collecter (logs, callback) |

Démo : [demos/04-ansible-pull.yml](demos/04-ansible-pull.yml) (cron + logrotate).

## 8. Gestion de la fenêtre de risque

* **Dry-run** : `--check --diff` avec `serial: 1` sur un hôte canari.
* **Approbation humaine** : `pause:` avec `prompt`, ou approbation dans un workflow AWX/AAP.
* **Verrouillage** : un seul déploiement à la fois (`flock` côté CI, ou file de jobs AWX).
* **Observabilité** : annotation Grafana / notification Slack au début et à la fin (`delegate_to: localhost`).
* **Retour arrière préparé** : conserver N releases, lien `current`, tag de version.

## 9. 🧪 Démos

Inventaire local : [demos/inventory.ini](demos/inventory.ini) (4 « web » + 1 « lb » simulés).

| Démo | Contenu |
|---|---|
| [demos/01-serial.yml](demos/01-serial.yml) | lots `[1, 2, 100%]`, `max_fail_percentage` |
| [demos/02-delegate.yml](demos/02-delegate.yml) | `delegate_to`, `run_once`, `throttle` |
| [demos/03-blue-green.yml](demos/03-blue-green.yml) | bascule atomique et retour arrière |
| [demos/04-ansible-pull.yml](demos/04-ansible-pull.yml) | pull planifié par cron |

```bash
cd 16-deploiements-avances/demos
ansible-playbook -i inventory.ini 01-serial.yml
ansible-playbook -i inventory.ini 01-serial.yml -e fail_web3=true     # l'échec stoppe les lots suivants
```

## 10. 🛠️ Labs

* [Lab 16 — Rolling update sans interruption avec rollback](labs/lab-16-rolling-update/README.md)

## ✅ Points clés

* `serial` + `max_fail_percentage` + `block/rescue` = déploiement prudent.
* `delegate_to` pour parler au LB / aux API depuis l'hôte courant.
* Toujours un **health check** avant de réintégrer un serveur.
* `run_once` + `serial` : attention au piège « une fois par lot ».

## ❓ Quiz

1. Que fait `serial: [1, "100%"]` ? *(un canari, puis le reste)*
2. Pourquoi `max_fail_percentage: 0` ? *(arrêter dès le premier échec)*
3. Que fait `delegate_to` ? *(exécute la tâche sur un autre hôte avec le contexte de l'hôte courant)*
4. Quand préférer `ansible-pull` ? *(parc nombreux/NAT/edge/auto-scaling)*
