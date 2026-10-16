"""Callback 'task_summary' : affiche un résumé compact à la fin du playbook."""
from __future__ import annotations

DOCUMENTATION = """
  name: task_summary
  type: aggregate
  short_description: Résumé du nombre de tâches ok/changed/failed
  description: Compte les résultats de tâches et affiche un résumé final.
  requirements:
    - Activer via callbacks_enabled = task_summary
"""

from collections import Counter

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "task_summary"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        self.counts = Counter()

    def v2_runner_on_ok(self, result):
        self.counts["changed" if result._result.get("changed") else "ok"] += 1

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.counts["failed"] += 1

    def v2_runner_on_skipped(self, result):
        self.counts["skipped"] += 1

    def v2_playbook_on_stats(self, stats):
        self._display.banner("RÉSUMÉ task_summary")
        self._display.display(", ".join(f"{k}={v}" for k, v in sorted(self.counts.items())))
