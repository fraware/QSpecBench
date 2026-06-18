"""Repository policy tests."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_no_coq_rocq_adapters():
    adapters = REPO / "adapters"
    names = {p.name for p in adapters.iterdir() if p.is_dir()}
    assert "coq" not in names
    assert "rocq" not in names


def test_lean_adapter_present():
    assert (REPO / "adapters" / "lean" / "parse_result.py").is_file()
