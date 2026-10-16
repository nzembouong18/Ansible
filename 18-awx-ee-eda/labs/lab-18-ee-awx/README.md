# Lab 18 — Execution Environment, ansible-navigator et AWX as code

⏱️ 2 h · Parties A et B : locales (sans conteneur pour `create` et `--ee false`). Partie C : nécessite AWX (kind + AWX Operator) — optionnelle.

## 🎯 Objectif

Rendre l'exécution **reproductible** (EE), la lancer avec `ansible-navigator`, puis décrire la configuration d'AWX **en code**.

## Partie A — Construire un Execution Environment

1. Écrivez `execution-environment.yml` (version 3) incluant : `ansible-core`, `ansible-runner`, les collections `ansible.posix`, `community.general`, `kubernetes.core`, les paquets Python `jmespath`, `netaddr`, `kubernetes`, et le paquet système `rsync`.
2. Générez le contexte de build **sans construire** : `ansible-builder create --context ctx` ; inspectez le `Dockerfile`. (Avec Docker/Podman : `ansible-builder build --tag ee-formation:1.0`.)
3. Questions : pourquoi un EE plutôt qu'un `pip install` sur le poste ? (→ mêmes versions en dev, CI et AWX.)

## Partie B — ansible-navigator

1. Écrivez `ansible-navigator.yml` (mode `stdout`, artifacts activés, `execution-environment.enabled: false` pour tester sans conteneur).
2. Lancez `hello.yml` : `ansible-navigator run hello.yml -m stdout`.
3. Rejouez l'artefact : `ansible-navigator replay artifacts/<fichier>.json -m stdout`.
4. Explorez : `ansible-navigator inventory -i hosts.ini -m stdout --graph`, `ansible-navigator doc ansible.builtin.copy -m stdout`, `ansible-navigator collections -m stdout`.
5. (Conteneur) Passez `execution-environment.enabled: true` avec votre image.

## Partie C — AWX en code (optionnelle)

1. Installez AWX (voir `demos/awx-install`) ; récupérez le mot de passe admin.
2. Adaptez `demos/awx-as-code/setup-awx.yml` : organisation, projet Git, inventaire, identifiant, modèle de job avec **questionnaire**, planification.
3. Créez un **workflow** : `Déployer DB` → `Déployer web` → `Smoke tests`, avec **approbation** avant la production.
4. Configurez une **notification** (Slack/e-mail) en cas d'échec.
5. Donnez à une équipe `Dev` le droit « Execute » sur le modèle mais pas « Admin » (RBAC).

## Validation

```bash
ansible-builder create --file execution-environment.yml --context ctx && ls ctx
ansible-navigator run hello.yml -m stdout
ls artifacts/
```

👉 Corrigé : [solution/](solution/)
