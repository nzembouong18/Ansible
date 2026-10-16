# Lab 16 — Mise à jour progressive sans interruption (rolling update)

⏱️ 1 h 30 · 100 % local (le « load balancer » et les « serveurs » sont simulés par des fichiers) ; variante Docker en bonus.

## 🎯 Objectif

Mettre à jour 4 serveurs de la version `1.0` à `2.0` **un par un**, en les retirant du load balancer pendant l'opération, avec **health check** et **arrêt automatique** si un serveur échoue. Prouver qu'à aucun moment il n'y a moins de 3 serveurs actifs.

## Modèle simulé

* Serveur `webN` = dossier `/tmp/lab16/webN/` contenant `VERSION` et `health` (contenu `OK`).
* Load balancer = fichier `/tmp/lab16/lb/backends.txt` (une ligne `webN` par serveur actif).
* Historique : `/tmp/lab16/lb/history.log` (une ligne `nombre_actifs` après chaque modification du LB).

## Énoncé

Écrivez `rolling.yml` :

1. **Play 1 (`web`, `serial: 1`, `max_fail_percentage: 0`)** pour chaque serveur :
   1. *retirer du LB* : `lineinfile` `state: absent` **délégué** au `lb`, puis consigner le nombre de serveurs actifs dans `history.log` ;
   2. *mettre à jour* : écrire `VERSION` ;
   3. *health check* : commande qui échoue si `health` ne contient pas `OK` ou si `VERSION` ≠ version cible (avec `retries: 3`, `delay: 1`, `until`) ;
   4. *réintégrer au LB* : `lineinfile` `state: present` + historique ;
   5. un `block/rescue` : en cas d'échec du health check, **ne pas réintégrer** le serveur cassé… mais remettre l'ancienne version et échouer clairement (le play s'arrête grâce à `max_fail_percentage: 0`).
2. **Play 2 (`localhost`)** : vérifier avec `assert` que `min(history) >= 3` et que les 4 serveurs sont à la version cible.
3. Test d'échec : `-e broken_host=web3` fait échouer le health check de `web3` ; vérifiez que `web4` n'a **pas** été touché et que le LB contient encore `web1 web2 web4`... et que la version de `web3` est revenue à `1.0`.

## Validation

```bash
ansible-playbook -i inventory.ini init.yml                          # prépare le modèle en version 1.0
ansible-playbook -i inventory.ini rolling.yml -e target_version=2.0
cat /tmp/lab16/lb/history.log                                       # jamais < 3
ansible-playbook -i inventory.ini init.yml
ansible-playbook -i inventory.ini rolling.yml -e target_version=2.0 -e broken_host=web3   # échec contrôlé
```

## Bonus (Docker)

Remplacez le LB fichier par HAProxy (lab 07) et la désactivation du backend par le module `community.general.haproxy` (`state: disabled`, `wait: true`, `drain: true`) délégué à `lb1`.

👉 Corrigé : [solution/](solution/)
