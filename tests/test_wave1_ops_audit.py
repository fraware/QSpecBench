"""F-016 Lean env probe cache + F-026 human_review ABRC/RC gate."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from qspecbench.trust import validate_trust_rules

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"


def test_lean_elan_and_lake_env_probe_cached(monkeypatch):
    """F-016: elan toolchain + lake env probe run once per process."""
    from adapters.lean import parse_result as lean

    lean.clear_lean_env_caches()
    monkeypatch.delenv("QSPECBENCH_SKIP_LEAN_ENV_PROBE", raising=False)
    monkeypatch.setenv("QSPECBENCH_LEAN_TOOLCHAIN", "leanprover/lean4:v4.14.0")

    calls: list[tuple] = []

    def fake_run(cmd, **kwargs):
        calls.append(tuple(cmd))
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = "leanprover/lean4:v4.14.0\n"
        proc.stderr = ""
        return proc

    monkeypatch.setattr(lean, "_lake_exe", lambda: "lake")
    monkeypatch.setattr(lean.shutil, "which", lambda _n: "elan")

    with patch.object(lean.subprocess, "run", side_effect=fake_run):
        # Probe path only (no real evidence compile): call caches directly.
        path_key = "fake-path"
        lean._ensure_elan_toolchain_cached("leanprover/lean4:v4.14.0", path_key)
        lean._ensure_elan_toolchain_cached("leanprover/lean4:v4.14.0", path_key)
        lean._lake_env_probe_cached("lake", str(lean.LEAN_ROOT), path_key)
        lean._lake_env_probe_cached("lake", str(lean.LEAN_ROOT), path_key)

    elan_list_calls = [c for c in calls if c[:3] == ("elan", "toolchain", "list")]
    lake_probe_calls = [c for c in calls if c[0] == "lake" and c[1] == "env"]
    assert len(elan_list_calls) == 1
    assert len(lake_probe_calls) == 1
    assert lean._ensure_elan_toolchain_cached.cache_info().hits >= 1
    assert lean._lake_env_probe_cached.cache_info().hits >= 1


def test_lean_skip_probe_env(monkeypatch, tmp_path):
    """F-016: QSPECBENCH_SKIP_LEAN_ENV_PROBE skips cold elan/lake probes."""
    from adapters.lean import parse_result as lean

    lean.clear_lean_env_caches()
    monkeypatch.setenv("QSPECBENCH_SKIP_LEAN_ENV_PROBE", "1")
    evidence = tmp_path / "ev.lean"
    evidence.write_text(
        "import QSpecBench.Quantum.OpenQASM3\n"
        "#check QSpecBench.Quantum.OpenQASM3.cnot_self_inverse\n",
        encoding="utf-8",
    )

    calls: list[tuple] = []

    def fake_run(cmd, **kwargs):
        calls.append(tuple(cmd))
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = "ok\n"
        proc.stderr = ""
        return proc

    monkeypatch.setattr(lean, "_lake_exe", lambda: "lake")
    monkeypatch.setattr(lean, "scan_lean_package_for_sorry", lambda root=None: [])
    with patch.object(lean.subprocess, "run", side_effect=fake_run):
        result = lean.check(evidence)

    assert result["ok"]
    assert not any(c[:2] == ("elan", "toolchain") for c in calls)
    assert any(c[0] == "lake" and c[1] == "env" and c[2] == "lean" for c in calls)


def test_human_review_adapter_declares_not_required_for_claim(tmp_path):
    """F-026: adapter result explicitly cannot satisfy ABRC/RC required_for_claim."""
    from adapters.human_review.parse_result import check

    path = tmp_path / "review.md"
    path.write_text(
        "Formal claim review covering unitary theorem assumptions on qubit state.\n" * 3,
        encoding="utf-8",
    )
    result = check(path)
    assert result["ok"]
    assert result["satisfies_required_for_claim"] is False
    assert "reference_claim" in result["cannot_satisfy_required_for_claim_maturities"]


def _abrc_spec_with_human_review(*, with_dual_reviews: bool) -> dict:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec["status"]["maturity"] = "artifact_bound_reference_claim"
    spec["status"]["ci"] = "passing"
    spec["claim_scope"] = {
        "headline_claim_id": "h",
        "headline_claim_text": spec["informal_claim"]["statement"],
        "required_obligations": ["ob_a"],
    }
    spec["proved_scope"] = {
        "checked_obligations": ["ob_a"],
        "unproved_obligations": [],
    }
    spec["headline_claim_status"] = {
        "status": "checked",
        "checked_under": ["lean_kernel"],
        "not_checked_under": ["device"],
    }
    spec["acceptable_evidence"] = [
        {
            "type": "human_review",
            "checker": "rubric",
            "path": None,
            "required_for_claim": True,
            "trust_level": "externally_trusted",
        },
        {
            "type": "lean_proof",
            "checker": "Lean 4 kernel",
            "path": None,
            "required_for_claim": True,
            "trust_level": "checked",
        },
    ]
    spec["evidence"] = [
        {
            "id": "rev",
            "type": "human_review",
            "path": "notes/r.md",
            "checker": "rubric",
            "status": "passing",
        },
        {
            "id": "lean",
            "type": "lean_proof",
            "path": "evidence/p.lean",
            "checker": "Lean 4 kernel",
            "status": "passing",
        },
    ]
    if with_dual_reviews:
        spec["status"]["reviews"] = {
            "formal_evidence_review": {"status": "approved", "reviewer": "alice-formal"},
            "domain_semantics_review": {"status": "approved", "reviewer": "bob-domain"},
        }
    else:
        spec["status"]["reviews"] = {}
    return spec


def test_human_review_heuristic_alone_cannot_satisfy_abrc_required_for_claim():
    """F-026: passing heuristic human_review without dual reviews fails ABRC."""
    spec = _abrc_spec_with_human_review(with_dual_reviews=False)
    errors = validate_trust_rules(spec)
    assert any("heuristic adapter alone" in e for e in errors)


def test_human_review_required_for_claim_ok_with_dual_reviews():
    """F-026: dual approved reviews satisfy the human_review required_for_claim gate."""
    spec = _abrc_spec_with_human_review(with_dual_reviews=True)
    errors = validate_trust_rules(spec)
    assert not any("heuristic adapter alone" in e for e in errors)
