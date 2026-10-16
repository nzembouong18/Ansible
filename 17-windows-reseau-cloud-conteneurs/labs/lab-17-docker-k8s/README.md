# Lab 17 — Générer et déployer une application sur Kubernetes

⏱️ 1 h 30 · Partie A : 100 % locale (rendu + validation des manifests). Partie B : nécessite un cluster (`kind`, `minikube` ou `k3s`) + `pip install kubernetes`.

## 🎯 Objectif

Industrialiser le déploiement d'une application sur Kubernetes : manifests générés par **templates Jinja2** à partir de variables par environnement (`dev`, `prod`), **validés** avant application, puis déployés avec `kubernetes.core.k8s`.

## Partie A — Rendu et validation (sans cluster)

1. `vars/dev.yml` et `vars/prod.yml` : `k8s_namespace`, `app_name`, `image` (avec tag **obligatoire**, pas de `latest`), `replicas` (dev 1, prod 3), `cpu_limit`, `memory_limit`, `ingress_host`.
2. Templates : `configmap.yml.j2`, `deployment.yml.j2` (requests/limits, `readinessProbe`, `livenessProbe`, `securityContext` non-root), `service.yml.j2`, `ingress.yml.j2` (uniquement si `ingress_host` défini).
3. `render.yml` (`-e env=dev|prod`) : charge `vars/<env>.yml`, **`assert`** (tag d'image ≠ latest, replicas ≥ 1, limites définies), rend les manifests dans `out/<env>/` et vérifie que chaque fichier est du YAML valide (`from_yaml`) avec `kind` attendu.

```bash
ansible-playbook render.yml -e env=dev
ansible-playbook render.yml -e env=prod
ls out/prod        # configmap.yml deployment.yml service.yml ingress.yml
ansible-playbook render.yml -e env=prod -e image=nginx:latest    # DOIT échouer (assert)
```

## Partie B — Déploiement (cluster requis)

```bash
kind create cluster --name formation
ansible-playbook deploy.yml -e env=dev
kubectl -n formation-dev get pods,svc
ansible-playbook deploy.yml -e env=dev -e replicas=2      # mise à jour déclarative
ansible-playbook deploy.yml -e env=dev -e state=absent    # nettoyage
```

`deploy.yml` : applique les manifests rendus (`kubernetes.core.k8s` avec `src:`), attend la disponibilité (`wait: true`), contrôle avec `k8s_info` que `readyReplicas == replicas`.

## Bonus

* Même exercice avec **Docker Compose** (`community.docker.docker_compose_v2`).
* Installer `ingress-nginx` avec `kubernetes.core.helm`.
* `ansible-playbook … --check --diff` sur `deploy.yml` : que montre `k8s` en mode check ?

👉 Corrigé : [solution/](solution/) — la partie A est testée en CI (`tests/run-checks.sh`).
