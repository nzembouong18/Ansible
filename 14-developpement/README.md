# Module 14 — Étendre Ansible : modules, plugins et filtres personnalisés

> **Durée** : 3 h · **Niveau** : expert

## 🎯 Objectifs

* Savoir quand (et quand **ne pas**) écrire un module.
* Écrire un module Python idempotent, avec `check_mode`, `diff`, documentation et tests.
* Écrire des plugins : filtre, lookup, callback, (aperçu : inventory, connection, action, vars).
* Organiser et distribuer son code (`library/`, `*_plugins/`, rôle, collection).

---

## 1. Faut-il écrire un module ?

| Besoin | Solution |
|---|---|
| Appeler un binaire / une API ponctuellement | `command`, `uri`, rôle |
| Transformer des données | **filtre** |
| Aller chercher une donnée à l'évaluation | **lookup** |
| Piloter une API avec idempotence, check_mode, diff | **module** |
| Modifier l'affichage/les rapports | **callback** |
| Générer l'inventaire depuis un système maison | **plugin d'inventaire** |
| Exécuter côté contrôleur avant/après un module | **action plugin** |

Un module = **un programme** (Python en général, mais tout langage produisant du JSON) exécuté **sur la cible**, qui reçoit ses arguments en JSON et renvoie un JSON. Les plugins (filter, lookup, callback, inventory, action…) s'exécutent **sur le contrôleur**.

## 2. Où placer son code

| Type | Emplacement (à côté du playbook ou dans un rôle) |
|---|---|
| Module | `library/` |
| Code partagé de modules | `module_utils/` |
| Filtres | `filter_plugins/` |
| Lookups | `lookup_plugins/` |
| Callbacks | `callback_plugins/` |
| Action plugins | `action_plugins/` |
| Inventaire | `inventory_plugins/` |
| Tests Jinja | `test_plugins/` |

Pour distribuer : dans un **rôle** (mêmes dossiers) ou une **collection** (`plugins/modules/`, `plugins/filter/`…) → module 09. Les chemins globaux se règlent dans `ansible.cfg` (`library`, `filter_plugins`, …).

## 3. Anatomie d'un module Python

Voir [demos/library/file_stamp.py](demos/library/file_stamp.py) et le lab.

```python
from ansible.module_utils.basic import AnsibleModule

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            token=dict(type="str", no_log=True),            # jamais journalisé
        ),
        supports_check_mode=True,
        required_if=[("state", "present", ["name"])],
        mutually_exclusive=[("a", "b")],
    )
    result = dict(changed=False)
    # 1. lire l'état actuel
    # 2. comparer à l'état voulu
    # 3. si différent : result["changed"] = True ; (si pas check_mode) appliquer
    # 4. result["diff"] = {"before": ..., "after": ...}
    module.exit_json(**result)        # succès
    # module.fail_json(msg="...", **result)   # échec
```

### Les 7 règles d'un bon module

1. **Idempotent** : comparer avant d'agir.
2. **`supports_check_mode=True`** et ne rien modifier quand `module.check_mode`.
3. **`diff`** : `before`/`after`.
4. **`argument_spec` complet** (types, choices, defaults, `no_log`).
5. **Documentation** `DOCUMENTATION` / `EXAMPLES` / `RETURN` en YAML (visibles via `ansible-doc`).
6. **Erreurs claires** via `fail_json`, jamais de traceback brut.
7. **Séparer la logique pure** du code d'E/S pour pouvoir la tester unitairement.

### Autres langages et modules « binaires »

Un module peut être un script Bash/PowerShell (Windows: `.ps1`), ou un binaire Go : il lit le fichier d'arguments (JSON) passé en `$1` et imprime du JSON `{"changed": true, ...}`. Python reste le plus simple grâce à `AnsibleModule`.

## 4. Plugins courants

### Filtre

```python
class FilterModule:
    def filters(self):
        return {"mask_secret": mask_secret}
```

### Lookup

```python
from ansible.plugins.lookup import LookupBase
class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        return [... une valeur par terme ...]
```

### Callback (rapports, notifications Slack, métriques)

```python
from ansible.plugins.callback import CallbackBase
class CallbackModule(CallbackBase):
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "task_summary"
    CALLBACK_NEEDS_ENABLED = True
    def v2_runner_on_ok(self, result): ...
    def v2_playbook_on_stats(self, stats): ...
```

Activation : `callbacks_enabled = task_summary` (ou `ANSIBLE_CALLBACKS_ENABLED`).

### Inventory plugin (squelette)

```python
from ansible.plugins.inventory import BaseInventoryPlugin
class InventoryModule(BaseInventoryPlugin):
    NAME = "formation.mon_plugin"
    def verify_file(self, path):
        return super().verify_file(path) and path.endswith(("mon_plugin.yml", "mon_plugin.yaml"))
    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)
        config = self._read_config_data(path)
        self.inventory.add_group("web")
        self.inventory.add_host("web-01", group="web")
        self.inventory.set_variable("web-01", "ansible_host", "10.0.0.1")
```

### Action plugin

S'exécute sur le **contrôleur** avant d'appeler le module distant : utile pour préparer des fichiers locaux, transformer des arguments (c'est ainsi que `template` rend Jinja2 localement avant `copy`).

## 5. Tester

| Niveau | Outil |
|---|---|
| Logique pure | `pytest` (cf. lab) |
| Module via Ansible | un playbook de test + `assert` sur `changed` (idempotence) |
| Qualité | `ansible-test sanity` (dans une collection), `ansible-lint`, `pylint`, `black`, `mypy` |
| Bout en bout | Molecule (module 15) |

Astuce : exécuter un module sans playbook, avec des arguments JSON :

```bash
cat > args.json <<'JSON'
{"ANSIBLE_MODULE_ARGS": {"path": "/tmp/x.conf", "settings": {"a": 1}}}
JSON
python3 library/config_kv.py args.json
```

## 6. Documentation & distribution

* `ansible-doc -M library mon_module` ; `ansible-doc -t filter -l`.
* `ansible-doc -t lookup counter` (le lookup doit avoir `DOCUMENTATION`).
* Versionnez avec SemVer, changelog, publication dans une collection (module 09).
* Ne cassez pas l'interface : dépréciez avant de supprimer (`deprecated:` dans `meta/runtime.yml`).

## 7. 🧪 Démos

| Démo | Contenu |
|---|---|
| [demos/library/file_stamp.py](demos/library/file_stamp.py) | module idempotent avec check_mode + diff |
| [demos/filter_plugins/](demos/filter_plugins) | filtres `to_csv_line`, `mask_secret` |
| [demos/lookup_plugins/counter.py](demos/lookup_plugins/counter.py) | lookup compteur |
| [demos/callback_plugins/task_summary.py](demos/callback_plugins/task_summary.py) | callback de résumé |
| [demos/01-plugins-locaux.yml](demos/01-plugins-locaux.yml) | tout ensemble |

```bash
cd 14-developpement/demos
ANSIBLE_CALLBACKS_ENABLED=task_summary ansible-playbook -i localhost, -c local 01-plugins-locaux.yml
```

## 8. 🛠️ Labs

* [Lab 14 — Écrire le module `config_kv` + tests pytest](labs/lab-14-module-kv/README.md)

## ✅ Points clés

* Module = idempotent + check_mode + diff + doc ; plugin = côté contrôleur.
* Logique pure séparée → testable.
* `library/` et `*_plugins/` suffisent pour démarrer ; collection pour distribuer.

## ❓ Quiz

1. Où s'exécute un module ? Un filtre ? *(cible / contrôleur)*
2. Comment empêcher qu'un paramètre apparaisse dans les logs ? *(`no_log=True`)*
3. Que renvoie un module ? *(du JSON : `changed`, `failed`, `msg`…)*
4. Comment tester sans Ansible ? *(pytest sur la logique pure ; exécuter le module avec un fichier d'arguments JSON)*
