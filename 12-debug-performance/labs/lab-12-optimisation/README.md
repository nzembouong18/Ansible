# Lab 12 — Réduire de moitié le temps d'un playbook lent

⏱️ 1 h · 100 % local (6 « hôtes » `ansible_connection=local`).

## 🎯 Objectif

Partir de `lent.yml`, **mesurer**, appliquer des optimisations une par une, et documenter le gain.

## Énoncé

1. Copiez `lent.yml` et `inventory.ini`, puis mesurez :
   ```bash
   ANSIBLE_CALLBACKS_ENABLED=ansible.builtin.timer,ansible.posix.profile_tasks ansible-playbook -i inventory.ini lent.yml
   ```
   Notez le temps total et les 3 tâches les plus longues.
2. Créez `rapide.yml` (même résultat fonctionnel) en appliquant :
   * désactivation des facts inutiles (`gather_facts: false`) ;
   * remplacement de la boucle de 5 `sleep 1` par des **appels asynchrones** parallèles (`async`/`poll: 0` + `async_status`) ;
   * `strategy: free` ;
   * `forks` suffisant (`-f 6`) ;
   * `run_once: true` pour la tâche qui n'a de sens qu'une fois.
3. Remesurez, calculez le gain, et expliquez quelle optimisation a le plus d'impact.

## Validation

* Temps de `rapide.yml` ≤ 1/2 de `lent.yml` (mesuré : ~41 s → ~18 s).
* Même fichier de sortie final : `/tmp/lab12-resultat.txt` contient 6 lignes (une par hôte).

👉 Corrigé : [solution/](solution/)
