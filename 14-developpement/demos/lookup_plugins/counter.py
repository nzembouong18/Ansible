"""Lookup 'counter' : compteur persistant dans un fichier (démo).

{{ lookup('counter', '/tmp/demo.counter') }}  -> 1, 2, 3 ... à chaque évaluation
"""
from __future__ import annotations

DOCUMENTATION = """
  name: counter
  short_description: Compteur persistant stocké dans un fichier
  description:
    - Incrémente et renvoie un entier stocké dans le fichier donné.
  options:
    _terms:
      description: Chemin du fichier compteur.
      required: true
"""

import os

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if not terms:
            raise AnsibleLookupError("counter attend un chemin de fichier")
        results = []
        for path in terms:
            value = 0
            if os.path.exists(path):
                with open(path, encoding="utf-8") as handle:
                    value = int(handle.read().strip() or 0)
            value += 1
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(str(value))
            results.append(value)
        return results
