#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module config_kv : gère des paires clé=valeur dans un fichier de configuration."""
from __future__ import annotations

DOCUMENTATION = r"""
---
module: config_kv
short_description: Gère des paires clé=valeur dans un fichier de configuration
description:
  - Impose des paires C(clé=valeur) dans un fichier, en conservant commentaires et lignes inconnues.
  - Idempotent, compatible C(check_mode) et C(diff).
version_added: "1.0.0"
author: Formation Ansible (@formation)
options:
  path:
    description: Chemin du fichier de configuration.
    type: path
    required: true
  settings:
    description: Dictionnaire des paires à imposer (ou à retirer si I(state=absent)).
    type: dict
    required: true
  state:
    description: C(present) impose les paires ; C(absent) retire les clés listées.
    type: str
    choices: [present, absent]
    default: present
  create:
    description: Créer le fichier s'il n'existe pas.
    type: bool
    default: true
  backup:
    description: Sauvegarder le fichier avant modification.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Imposer deux paramètres
  config_kv:
    path: /etc/app/app.conf
    settings:
      max_connections: 200
      log_level: warn

- name: Retirer une clé
  config_kv:
    path: /etc/app/app.conf
    settings: { debug: "" }
    state: absent
"""

RETURN = r"""
added:
  description: Clés ajoutées.
  type: list
  returned: always
updated:
  description: Clés dont la valeur a changé.
  type: list
  returned: always
removed:
  description: Clés retirées.
  type: list
  returned: always
"""

import re

from ansible.module_utils.basic import AnsibleModule

KEY_RE = re.compile(r"^\s*([^#=\s][^=\s]*)\s*=\s*(.*)$")
INVALID_KEY_RE = re.compile(r"[=\s]")


def validate_keys(settings):
    """Retourne la liste des clés invalides."""
    return [key for key in settings if INVALID_KEY_RE.search(str(key)) or not str(key)]


def apply_settings(lines, settings, state="present"):
    """Logique pure : applique `settings` à `lines`.

    Retourne (nouvelles_lignes, ajoutées, mises_à_jour, retirées).
    """
    wanted = {str(k): "" if v is None else str(v) for k, v in settings.items()}
    new_lines, seen = [], set()
    added, updated, removed = [], [], []

    for line in lines:
        match = KEY_RE.match(line)
        if not match:
            new_lines.append(line)
            continue
        key, value = match.group(1), match.group(2).strip()
        if key not in wanted:
            new_lines.append(line)
        elif state == "absent":
            removed.append(key)          # la ligne est supprimée
        elif key in seen:
            continue                     # doublon : on ne garde que la première occurrence
        else:
            seen.add(key)
            if value != wanted[key]:
                updated.append(key)
                new_lines.append(f"{key}={wanted[key]}")
            else:
                new_lines.append(line)

    if state == "present":
        for key, value in wanted.items():
            if key not in seen:
                added.append(key)
                new_lines.append(f"{key}={value}")
    return new_lines, added, updated, removed


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True),
            settings=dict(type="dict", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            create=dict(type="bool", default=True),
            backup=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
        add_file_common_args=True,
    )
    p = module.params
    invalid = validate_keys(p["settings"])
    if invalid:
        module.fail_json(msg=f"Clés invalides (ni '=' ni espace autorisés) : {invalid}")

    try:
        with open(p["path"], encoding="utf-8") as handle:
            before = handle.read()
        exists = True
    except FileNotFoundError:
        before, exists = "", False
        if not p["create"]:
            module.fail_json(msg=f"Le fichier {p['path']} n'existe pas et create=false")

    lines = before.splitlines()
    new_lines, added, updated, removed = apply_settings(lines, p["settings"], p["state"])
    after = "\n".join(new_lines) + ("\n" if new_lines else "")
    changed = after != before or (not exists and p["state"] == "present" and bool(new_lines))

    result = dict(changed=changed, added=added, updated=updated, removed=removed, path=p["path"])
    if changed:
        result["diff"] = dict(before=before, after=after, before_header=p["path"], after_header=p["path"])
        if not module.check_mode:
            if p["backup"] and exists:
                result["backup_file"] = module.backup_local(p["path"])
            try:
                with open(p["path"], "w", encoding="utf-8") as handle:
                    handle.write(after)
            except OSError as exc:
                module.fail_json(msg=f"Écriture impossible : {exc}", **result)

    if not module.check_mode and (exists or changed):
        file_args = module.load_file_common_arguments(p)
        result["changed"] = module.set_fs_attributes_if_different(file_args, result["changed"])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
