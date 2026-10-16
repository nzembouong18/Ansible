"""Filtres de démonstration pour la collection formation.utils."""
from __future__ import annotations

from ansible.errors import AnsibleFilterError

DOCUMENTATION = """
  name: slugify
  author: formation-ansible
  version_added: "1.0.0"
  short_description: Transforme un texte en slug d'URL
  description:
    - Met en minuscules, remplace les espaces et caractères spéciaux par des tirets.
  positional: _input
  options:
    _input:
      description: Texte à transformer.
      type: str
      required: true
"""

EXAMPLES = """
- ansible.builtin.debug:
    msg: "{{ 'Mon Super Site!' | formation.utils.slugify }}"   # mon-super-site
"""

RETURN = """
  _value:
    description: Le slug.
    type: str
"""

import re
import unicodedata


def slugify(value):
    if not isinstance(value, str):
        raise AnsibleFilterError("slugify attend une chaîne de caractères")
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


class FilterModule:
    """Enregistre les filtres de la collection."""

    def filters(self):
        return {"slugify": slugify}
