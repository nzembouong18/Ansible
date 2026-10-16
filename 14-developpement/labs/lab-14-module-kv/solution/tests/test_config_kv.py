"""Tests unitaires de la logique pure du module config_kv (pytest)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "library"))

from config_kv import apply_settings, validate_keys  # noqa: E402


def test_ajout_nouvelle_cle():
    lines, added, updated, removed = apply_settings(["a=1"], {"b": 2})
    assert lines == ["a=1", "b=2"]
    assert (added, updated, removed) == (["b"], [], [])


def test_mise_a_jour():
    lines, added, updated, _ = apply_settings(["a=1", "b=2"], {"a": 10})
    assert lines == ["a=10", "b=2"]
    assert updated == ["a"] and added == []


def test_idempotence():
    lines = ["a=1", "# commentaire", "b=2"]
    new, added, updated, removed = apply_settings(lines, {"a": 1, "b": "2"})
    assert new == lines
    assert not (added or updated or removed)


def test_suppression():
    lines, _, _, removed = apply_settings(["a=1", "b=2"], {"a": ""}, state="absent")
    assert lines == ["b=2"] and removed == ["a"]


def test_commentaires_et_ordre_conserves():
    src = ["# en-tête", "", "z=26", "# milieu", "a=1"]
    new, *_ = apply_settings(src, {"a": 2})
    assert new == ["# en-tête", "", "z=26", "# milieu", "a=2"]


def test_doublons_dedoublonnes():
    new, _, _, _ = apply_settings(["a=1", "a=2"], {"a": 3})
    assert new == ["a=3"]


def test_cles_invalides():
    assert validate_keys({"ok": 1, "a b": 2, "c=d": 3}) == ["a b", "c=d"]
