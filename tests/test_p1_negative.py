"""P1 negative tests: overclaim classes, QEC tables, adapter discipline."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest import mock

import yaml

from qspecbench.bridge_manifest import validate_kernel_bridge
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.trust import validate_trust_rules
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]
MINIMAL = REPO / "schema" / "examples" / "minimal.spec.yaml"


def _base() -> dict:
    spec = yaml.safe_load(MINIMAL.read_text(encoding="utf-8"))
    spec["claim_scope"] = {
        "headline_claim_id": "h",
        "headline_claim_text": "test",
        "required_obligations": ["ob_a", "ob_b"],
    }
    spec["proved_scope"] = {
        "checked_obligations": ["ob_a"],
        "unproved_obligations": ["ob_b"],
    }
    spec["headline_claim_status"] = {"status": "partially_checked", "notes": None}
    return spec


def test_reference_claim_partial_obligation_rejected():
    spec = _base()
    spec["status"]["maturity"] = "reference_claim"
    spec["headline_claim_status"]["status"] = "checked"
    spec["acceptable_evidence"] = [
        {
            "type": "lean_proof",
            "checker": "Lean 4 kernel",
            "path": None,
            "required_for_claim": True,
            "trust_level": "checked",
        }
    ]
    spec["evidence"] = [
        {
            "id": "lean_ob",
            "type": "lean_proof",
            "path": "evidence/p.lean",
            "checker": "Lean 4 kernel",
            "status": "passing",
        }
    ]
    spec["formal_claims"] = [
        {
            "id": "fc1",
            "evidence_id": "lean_ob",
            "formal_system": "lean",
            "theorem": "t",
            "supports": ["ob_a"],
            "does_not_support": ["ob_b"],
            "benchmark_anchor": "minimal_example",
        }
    ]
    errors = validate_trust_rules(spec)
    assert any("unchecked headline obligations" in e for e in errors)


def test_syndrome_table_mismatch_rejected():
    from adapters.qec.parse_result import validate_syndrome_table

    code = {
        "parameters": {"n": 3},
        "stabilizers": [{"pauli": "ZZI"}, {"pauli": "IZZ"}],
    }
    bad_table = {
        "entries": [
            {"syndrome": "10", "error": "X0"},
            {"syndrome": "01", "error": "X1"},
            {"syndrome": "11", "error": "X2"},
        ]
    }
    errors, _ = validate_syndrome_table(code, bad_table)
    assert errors


def test_kernel_bridge_hash_drift_rejected():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    bridge = json.loads((claim / "expected/semantic_bridge.json").read_text(encoding="utf-8"))
    bridge_bad = dict(bridge)
    bridge_bad["artifact_sha256"] = "0" * 64
    errors = validate_kernel_bridge(claim, bridge_bad, spec)
    assert any("artifact_sha256 drift" in e or "semantic_bridge artifact_sha256 drift" in e for e in errors)


def test_ai_reference_without_human_review_rejected():
    spec = _base()
    spec["track"] = "ai_formalization"
    spec["status"]["maturity"] = "reference_scaffold"
    spec["acceptable_evidence"] = [
        {
            "type": "lean_proof",
            "checker": "Lean 4 kernel",
            "path": None,
            "required_for_claim": False,
            "trust_level": "checked",
        }
    ]
    spec["evidence"] = [
        {
            "id": "lean_ob",
            "type": "lean_proof",
            "path": "evidence/p.lean",
            "checker": "Lean 4 kernel",
            "status": "passing",
        }
    ]
    spec["formal_claims"] = [
        {
            "id": "fc1",
            "evidence_id": "lean_ob",
            "formal_system": "lean",
            "theorem": "t",
            "supports": ["ob_a"],
            "does_not_support": [],
            "benchmark_anchor": "minimal_example",
        }
    ]
    errors = validate_trust_rules(spec)
    assert any("human_review" in e for e in errors)


def test_raw_command_rejected_without_escape_hatch():
    with tempfile.TemporaryDirectory() as tmp:
        claim = Path(tmp)
        (claim / "evidence").mkdir()
        artifact = claim / "evidence" / "x.txt"
        artifact.write_text("ok", encoding="utf-8")
        spec = _base()
        spec["evidence"] = [
            {
                "id": "raw",
                "type": "human_review",
                "path": "evidence/x.txt",
                "checker": "manual",
                "command": "python -c print(1)",
                "status": "passing",
            }
        ]
        spec["acceptable_evidence"].append(
            {
                "type": "human_review",
                "checker": "manual",
                "path": None,
                "required_for_claim": False,
                "trust_level": "externally_trusted",
            }
        )
        (claim / "spec.yaml").write_text(yaml.dump(spec), encoding="utf-8")
        results = run_evidence_checks(claim)
        raw = next(r for r in results if r.evidence_id == "raw")
        assert not raw.ok
        assert any("raw command" in e for e in raw.errors)


def test_smt_no_solver_not_independently_checkable():
    from adapters.smt.parse_result import check

    with tempfile.TemporaryDirectory() as tmp:
        cert_dir = Path(tmp)
        smt = cert_dir / "t.smt2"
        smt.write_text("(declare-const x Bool)\n(assert true)\n(check-sat)\n", encoding="utf-8")
        cert = cert_dir / "cert.json"
        cert.write_text(
            json.dumps({"smt_file": "t.smt2", "expected": "sat"}),
            encoding="utf-8",
        )
        with mock.patch("adapters.smt.parse_result.shutil.which", return_value=None):
            result = check(cert)
        assert result.get("skipped") is True
        assert result.get("trust_level") == "not_checked"
        assert not result.get("ok")


def test_cnot_kernel_checked_validates():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = validate_path(claim)
    assert results and results[0].ok
