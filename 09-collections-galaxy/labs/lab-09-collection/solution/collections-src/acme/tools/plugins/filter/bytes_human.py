"""Filtre acme.tools.bytes_human."""
from __future__ import annotations

from ansible.errors import AnsibleFilterError

DOCUMENTATION = """
  name: bytes_human
  author: acme
  version_added: "0.1.0"
  short_description: Convertit un nombre d'octets en taille lisible
  description:
    - Convertit un nombre d'octets en chaîne lisible (Ko, Mo, Go...).
  positional: _input, precision
  options:
    _input:
      description: Nombre d'octets.
      type: int
      required: true
    precision:
      description: Nombre de décimales.
      type: int
      default: 1
"""

EXAMPLES = """
- ansible.builtin.debug:
    msg: "{{ 1610612736 | acme.tools.bytes_human }}"        # 1.5 Go
- ansible.builtin.debug:
    msg: "{{ 1500 | acme.tools.bytes_human(precision=2) }}"  # 1.46 Ko
"""

RETURN = """
  _value:
    description: Taille formatée.
    type: str
"""

UNITS = ["o", "Ko", "Mo", "Go", "To", "Po"]


def bytes_human(value, precision=1):
    try:
        size = float(value)
    except (TypeError, ValueError) as exc:
        raise AnsibleFilterError(f"bytes_human attend un nombre, reçu : {value!r}") from exc
    idx = 0
    while size >= 1024 and idx < len(UNITS) - 1:
        size /= 1024
        idx += 1
    if idx == 0:
        return f"{int(size)} o"
    return f"{size:.{int(precision)}f} {UNITS[idx]}"


class FilterModule:
    """Enregistre les filtres de la collection."""

    def filters(self):
        return {"bytes_human": bytes_human}
