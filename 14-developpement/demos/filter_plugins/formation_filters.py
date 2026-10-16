"""Filtres locaux : chargés automatiquement depuis filter_plugins/ à côté du playbook."""
from __future__ import annotations

from ansible.errors import AnsibleFilterError


def to_csv_line(values, sep=","):
    """['a', 'b', 'c'] | to_csv_line  ->  'a,b,c' (échappe les séparateurs)."""
    if not isinstance(values, (list, tuple)):
        raise AnsibleFilterError("to_csv_line attend une liste")
    out = []
    for value in values:
        text = str(value)
        out.append(f'"{text}"' if sep in text or '"' in text else text)
    return sep.join(out)


def mask_secret(value, visible=2):
    """'abcdef' | mask_secret  ->  'ab****'."""
    text = str(value)
    return text[:visible] + "*" * max(len(text) - visible, 0)


class FilterModule:
    def filters(self):
        return {"to_csv_line": to_csv_line, "mask_secret": mask_secret}
