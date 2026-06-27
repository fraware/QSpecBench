"""Repository policy tests."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_proof_assistant_stub_adapters_present():
    adapters = REPO / "adapters"
    for name in ("coq", "rocq", "isabelle"):
        assert (adapters / name / "parse_result.py").is_file()


def test_lean_adapter_present():
    assert (REPO / "adapters" / "lean" / "parse_result.py").is_file()


def test_no_legacy_lean_kernel_string_in_specs():
    """Specs must say Lean 4 kernel, not legacy Lean kernel."""
    bad: list[str] = []
    for pattern in (REPO / "benchmarks", REPO / "schema" / "examples"):
        for path in pattern.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                if "Lean kernel" in line and "Lean 4 kernel" not in line:
                    bad.append(f"{path}:{i}: {line.strip()}")
    assert not bad, "legacy Lean kernel strings:\n" + "\n".join(bad)
