# Lab 01 — Premier playbook sur le labo

⏱️ 45 min · Prérequis : module 00 validé (`ansible all -m ping` OK)

## 🎯 Objectif

Écrire un playbook qui prépare les serveurs web : un répertoire applicatif, un fichier d'identité alimenté par des *facts*, et un paquet utilitaire. Puis constater l'idempotence.

## Énoncé

Créez `lab01.yml` ciblant le groupe `webservers` qui, en utilisant `become: true` :

1. crée le répertoire `/opt/formation` (propriétaire `root`, mode `0755`) ;
2. dépose `/opt/formation/identite.txt` contenant : le nom d'hôte, la distribution + version, l'adresse IPv4 par défaut et le nombre de CPU (utilisez les *facts*) ;
3. installe le paquet `tree` ;
4. affiche à la fin un message `debug` « Préparation terminée sur <hôte> ».

## Étapes de validation

```bash
ansible-playbook lab01.yml --syntax-check
ansible-playbook lab01.yml --check --diff      # simulation
ansible-playbook lab01.yml                     # 1re exécution : changed
ansible-playbook lab01.yml                     # 2e exécution : changed=0 (idempotence !)
ansible webservers -b -m command -a "cat /opt/formation/identite.txt"
```

**Critères** : 2ᵉ exécution à `changed=0` ; le fichier contient des valeurs différentes sur web1 et web2.

## Pour aller plus loin

* Lancez avec `-v`, `-vv`, `-vvv` : que voit-on de plus ?
* Utilisez `--list-tasks`, `--list-hosts`, `--step`, `--start-at-task`.
* Modifiez le fichier à la main sur web1 (`ansible web1 -b -m shell -a "echo x >> /opt/formation/identite.txt"`) puis relancez : que se passe-t-il ? (→ *drift* corrigé)

👉 Corrigé : [solution/lab01.yml](solution/lab01.yml)
