"""P2 community infrastructure tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from qspecbench.claim_diff import claim_diff_report
from qspecbench.trust import validate_trust_rules
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]


def test_claim_diff_reports_gap():
    spec = {
        "id": "x",
        "informal_claim": {"statement": "Full protocol correct"},
        "status": {"maturity": "reference_scaffold"},
        "claim_scope": {
            "headline_claim_text": "Full protocol correct",
            "required_obligations": ["a", "b"],
        },
        "proved_scope": {"checked_obligations": ["a"], "unproved_obligations": ["b"]},
        "headline_claim_status": {"status": "partially_checked"},
    }
    report = claim_diff_report(spec)
    assert "Gap" in report
    assert "b" in report


def test_cnot_artifact_bound_validates():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = validate_path(claim)
    assert results and results[0].ok
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    assert spec["status"]["maturity"] == "artifact_bound_reference_claim"
    assert spec["headline_claim_status"]["status"] == "checked"


def test_hamiltonian_contract_cannot_be_reference_claim():
    spec = yaml.safe_load(
        (REPO / "schema/examples/hamiltonian.spec.yaml").read_text(encoding="utf-8")
    )
    spec["status"]["maturity"] = "reference_claim"
    spec["hamiltonian_claim_scope"] = {
        "claim_class": "declared_contract_claim",
        "derivation_status": "declared_only",
    }
    spec["claim_scope"] = {
        "headline_claim_id": "h",
        "headline_claim_text": "t",
        "required_obligations": ["c"],
    }
    spec["proved_scope"] = {"checked_obligations": ["c"], "unproved_obligations": []}
    spec["headline_claim_status"] = {"status": "checked", "notes": None}
    errors = validate_trust_rules(spec)
    assert any("declared_contract_claim cannot be reference_claim" in e for e in errors)


def test_scaffold_claim_diff_evidence_generated():
    """Batch claim-diff writes evidence/claim_diff.md for reference_scaffold benchmarks."""
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    tools = str(REPO / "tools")
    env["PYTHONPATH"] = tools + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run(
        [sys.executable, str(REPO / "scripts" / "run_claim_diff_all.py"), "--write-evidence"],
        check=True,
        cwd=REPO,
        env=env,
    )
    sample = REPO / "benchmarks/equivalence/clifford_simplification_preserves_unitary/evidence/claim_diff.md"
    assert sample.is_file()
    text = sample.read_text(encoding="utf-8")
    assert "clifford_simplification_preserves_unitary" in text
    assert "semantic_correctness_of_circuit_vs_claim" in text


def test_cp_gate_extracts():
    from qspecbench.qasm_matrix import extract_matrix
    import tempfile

    qasm = "OPENQASM 3.0;\nqubit[2] q;\ncp(pi/2) q[0], q[1];\n"
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        data = extract_matrix(path)
        assert len(data["gates_applied"]) == 1
    finally:
        path.unlink(missing_ok=True)
