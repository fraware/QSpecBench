"""Coq adapter CI smoke tests (parse_result stub only)."""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_coq_stub_returns_not_checked():
    from adapters.coq.parse_result import check

    result = check(REPO / "adapters" / "coq" / "README.md")
    assert result["adapter"] == "coq_proof"
    assert not result["ok"]
    assert result.get("skipped")
    assert result["trust_level"] == "not_checked"


def test_rocq_stub_returns_not_checked():
    from adapters.rocq.parse_result import check

    result = check(REPO / "adapters" / "rocq" / "README.md")
    assert result["adapter"] == "rocq_proof"
    assert not result["ok"]
    assert result.get("skipped")


def test_isabelle_stub_returns_not_checked():
    from adapters.isabelle.parse_result import check

    result = check(REPO / "adapters" / "isabelle" / "README.md")
    assert result["adapter"] == "isabelle_proof"
    assert not result["ok"]
    assert result.get("skipped")
