#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module de démonstration : dépose un fichier « tampon » contenant un texte.

Illustre : argument_spec, check_mode, diff, idempotence, valeurs de retour, fail_json.
"""
from __future__ import annotations

DOCUMENTATION = r"""
---
module: file_stamp
short_description: Gère un fichier tampon contenant un texte
description:
  - Crée ou met à jour un fichier avec le texte fourni, de façon idempotente.
version_added: "1.0.0"
author: Formation Ansible (@formation)
options:
  path:
    description: Chemin du fichier.
    type: path
    required: true
  text:
    description: Texte à écrire (une fin de ligne est ajoutée).
    type: str
    required: true
  state:
    description: C(present) crée/met à jour, C(absent) supprime.
    type: str
    choices: [present, absent]
    default: present
  mode:
    description: Permissions du fichier.
    type: raw
    default: "0644"
notes:
  - Supporte C(check_mode) et C(diff).
"""

EXAMPLES = r"""
- name: Déposer un tampon
  file_stamp:
    path: /tmp/stamp.txt
    text: "déployé par Ansible"

- name: Le supprimer
  file_stamp:
    path: /tmp/stamp.txt
    text: ignoré
    state: absent
"""

RETURN = r"""
path:
  description: Chemin géré.
  type: str
  returned: always
previous:
  description: Contenu précédent (si le fichier existait).
  type: str
  returned: when changed
"""

import os

from ansible.module_utils.basic import AnsibleModule


def read_file(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="path", required=True),
            text=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent"]),
            mode=dict(type="raw", default="0644"),
        ),
        supports_check_mode=True,
        add_file_common_args=True,
    )
    path = module.params["path"]
    wanted = module.params["text"] + "\n"
    current = read_file(path)
    result = dict(changed=False, path=path)

    if module.params["state"] == "absent":
        if current is not None:
            result.update(changed=True, diff=dict(before=current, after=""))
            if not module.check_mode:
                os.remove(path)
        module.exit_json(**result)

    if current != wanted:
        result.update(changed=True, diff=dict(before=current or "", after=wanted))
        if current is not None:
            result["previous"] = current
        if not module.check_mode:
            try:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(wanted)
            except OSError as exc:
                module.fail_json(msg=f"Écriture impossible : {exc}", **result)

    # permissions via les arguments communs (mode, owner, group...)
    file_args = module.load_file_common_arguments(module.params)
    if not module.check_mode and os.path.exists(path):
        result["changed"] = module.set_fs_attributes_if_different(file_args, result["changed"])
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
