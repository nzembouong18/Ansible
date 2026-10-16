# Lab 07 — Configuration HAProxy générée depuis l'inventaire

⏱️ 1 h 15 · Labo Docker (cible `lb1`) — le rendu peut aussi se tester en local (`render.yml`).

## 🎯 Objectif

Générer `haproxy.cfg` **à partir de l'inventaire** : ajouter un serveur dans le groupe `webservers` doit suffire à l'inscrire dans le load balancer, sans toucher au template.

## Énoncé

1. Écrivez `templates/haproxy.cfg.j2` avec :
   * en-tête `{{ ansible_managed }}` ;
   * `frontend http_in` écoutant sur `{{ lb_port }}` (défaut 80) ;
   * `backend web_pool`, `balance {{ lb_algo | default('roundrobin') }}` ;
   * **une ligne `server` par hôte de `webservers`** : `server <nom> <ip>:<port> check` (IP = `ansible_host` si défini, sinon `inventory_hostname`) ;
   * un bloc `listen stats` seulement si `lb_stats_enabled` est vrai (port 8404, `stats uri /stats`).
2. Écrivez `lb.yml` (cible `loadbalancers`) : installe `haproxy`, déploie la config avec `validate: haproxy -c -f %s`, notifie un handler qui **recharge** le service, démarre/active le service.
3. Écrivez `render.yml` (cible `localhost`) qui rend le même template dans `/tmp/haproxy.cfg` avec un jeu de variables factices — utile pour itérer rapidement.

## Validation

```bash
ansible-playbook render.yml && cat /tmp/haproxy.cfg
ansible-playbook lb.yml --check --diff
ansible-playbook lb.yml
curl -s http://localhost:8080         # alterne web1 / web2 (si nginx déployé au lab 04)
ansible-playbook lb.yml -e lb_algo=leastconn -e lb_stats_enabled=true --diff
```

Ajoutez un `web3` dans l'inventaire : relancez → la config contient 3 serveurs.

👉 Corrigé : [solution/](solution/)
