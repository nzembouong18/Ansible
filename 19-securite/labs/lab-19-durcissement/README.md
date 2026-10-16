# Lab 19 — Durcir les serveurs du labo et mesurer la conformité

⏱️ 1 h 30 · Labo Docker (ou `localhost`, voir ci-dessous).

## 🎯 Objectif

Passer d'un score de conformité **faible** à **maximal**, de façon reproductible et mesurable, puis ajouter des protections complémentaires.

## Énoncé

1. **Avant** : lancez l'audit en lecture seule `demos/02-audit.yml` sur `all` et notez le score.
2. Écrivez `durcissement.yml` qui :
   * applique le rôle `hardening` (`demos/roles/hardening`, via `roles_path`) ;
   * **conserve l'accès** : avant de désactiver `PasswordAuthentication`, vérifiez avec `assert`/`authorized_key` que la clé du labo est présente (sinon vous vous enfermez dehors !) ;
   * installe et active `fail2ban` (jail `sshd` : `maxretry = 3`, `bantime = 1h`) via un template ;
   * active les mises à jour de sécurité automatiques (`unattended-upgrades` sur Debian, `dnf-automatic` sur RedHat) ;
   * crée un utilisateur `deploy` avec un sudoers à **privilèges minimaux** (voir `demos/05-sudoers-moindre-privilege.yml`).
3. **Après** : relancez l'audit : le score doit atteindre 5/5.
4. Prouvez l'**idempotence** (2ᵉ passage `changed=0`) et testez `--check --diff`.
5. Ajoutez un contrôle **négatif** : modifiez `PermitRootLogin yes` dans `/etc/ssh/sshd_config.d/10-hardening.conf` à la main puis relancez : le playbook doit le corriger (dérive).

## Test local (sans labo)

```bash
cd solution
ansible-playbook -i localhost, -c local ../../demos/02-audit.yml
ansible-playbook -i localhost, -c local durcissement.yml -e hardening_manage_service=false -e lab_local=true
ansible-playbook -i localhost, -c local ../../demos/02-audit.yml
```

👉 Corrigé : [solution/](solution/)
