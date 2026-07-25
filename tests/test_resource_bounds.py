"""Phase 6 resource bounds + backend + schedule regressions."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from qspecbench.circuit_backend import PermutationBackend, select_backend
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.evidence_schedule import (
    EvidenceClass,
    batches_by_class,
    classify_evidence_type,
    max_workers_for,
    run_bounded,
    schedule_evidence,
)
from qspecbench.perm_circuit import apply_qasm_permutation
from qspecbench.qasm_matrix import extract_matrix
from qspecbench.resource_bounds import DENSE_DISABLED_MSG, max_dense_qubits

REPO = Path(__file__).resolve().parents[1]


def test_dense_rejects_oversized(monkeypatch, tmp_path):
    monkeypatch.setenv("QSPECBENCH_MAX_DENSE_QUBITS", "2")
    qasm = tmp_path / "big.qasm"
    qasm.write_text("OPENQASM 3.0;\nqubit[3] q;\nx q[0];\n", encoding="utf-8")
    with pytest.raises(ValueError, match="dense matrix backend disabled for 3 qubits"):
        extract_matrix(qasm)
    assert "select a scalable adapter" in DENSE_DISABLED_MSG.format(n=3)


def test_perm_backend_handles_larger_reversible(tmp_path, monkeypatch):
    monkeypatch.setenv("QSPECBENCH_MAX_DENSE_QUBITS", "2")
    qasm = tmp_path / "perm.qasm"
    # 4 qubits would blow dense default-2; permutation must still work.
    qasm.write_text(
        "OPENQASM 3.0;\nqubit[4] q;\nx q[0];\ncx q[0], q[1];\nswap q[2], q[3];\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="dense matrix backend disabled"):
        extract_matrix(qasm)
    backend = select_backend(permutation_only=True)
    assert isinstance(backend, PermutationBackend)
    parsed = backend.parse(qasm)
    assert parsed["n_qubits"] == 4
    assert len(parsed["permutation"]) == 16
    # Identity compare against itself.
    assert backend.compare(parsed, parsed)["ok"]


def test_select_backend_prefers_perm_when_flagged():
    b = select_backend(permutation_only=True)
    assert b.name == "permutation"


def test_concurrency_bounded():
    assert max_workers_for(EvidenceClass.LEAN) == 1
    assert max_workers_for(EvidenceClass.QCEC) == 1
    assert max_workers_for(EvidenceClass.LIGHTWEIGHT) >= 1

    seen: list[int] = []

    def work(x: int) -> int:
        seen.append(x)
        return x * 2

    out = run_bounded([1, 2, 3, 4], work, max_workers=2, timeout_s=5)
    assert out == [2, 4, 6, 8]
    assert sorted(seen) == [1, 2, 3, 4]


def test_subprocess_timeout_fail_closed():
    with pytest.raises(TimeoutError, match="fail-closed"):
        run_bounded(
            [1, 2],
            lambda _x: __import__("time").sleep(2),
            max_workers=2,
            timeout_s=0.1,
        )


def test_schedule_deterministic_order():
    entries = [
        {"id": "lean", "type": "lean_proof"},
        {"id": "qasm", "type": "qasm_parse"},
        {"id": "qcec", "type": "qcec_result"},
        {"id": "py", "type": "internal_denotation_consistency"},
    ]
    scheduled = schedule_evidence(entries)
    assert [s.evidence_id for s in scheduled] == ["qasm", "py", "lean", "qcec"]
    assert classify_evidence_type("lean_proof") == EvidenceClass.LEAN
    batches = batches_by_class(scheduled)
    assert [c for c, _ in batches] == [
        EvidenceClass.LIGHTWEIGHT,
        EvidenceClass.PYTHON,
        EvidenceClass.LEAN,
        EvidenceClass.QCEC,
    ]


def test_run_bounded_wired_into_evidence_runner(tmp_path, monkeypatch):
    """F-015: evidence_runner dispatches per-class batches through run_bounded."""
    from qspecbench import evidence_runner as er

    calls: list[tuple[int, EvidenceClass | None]] = []
    real_run_bounded = er.run_bounded

    def tracking_run_bounded(items, worker, *, max_workers, timeout_s=None):
        cls = None
        if items and isinstance(items[0], dict):
            cls = classify_evidence_type(str(items[0].get("type") or ""))
        calls.append((max_workers, cls))
        return real_run_bounded(items, worker, max_workers=max_workers, timeout_s=timeout_s)

    monkeypatch.setattr(er, "run_bounded", tracking_run_bounded)

    claim = tmp_path / "claim"
    claim.mkdir()
    (claim / "evidence").mkdir()
    review = claim / "evidence" / "review.md"
    review.write_text(
        "Formal claim review: unitary proof on qubit state assumptions.\n" * 4,
        encoding="utf-8",
    )
    (claim / "evidence" / "a.py").write_text("print('ok')\n", encoding="utf-8")
    minimal = yaml.safe_load(
        (REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8")
    )
    minimal["acceptable_evidence"] = [
        {
            "type": "human_review",
            "checker": "manual",
            "path": None,
            "required_for_claim": False,
            "trust_level": "externally_trusted",
        },
        {
            "type": "lean_proof",
            "checker": "Lean 4 kernel",
            "path": None,
            "required_for_claim": False,
            "trust_level": "checked",
        },
    ]
    minimal["evidence"] = [
        {
            "id": "lean_a",
            "type": "lean_proof",
            "path": "evidence/a.py",
            "checker": "Lean 4 kernel",
            "status": "passing",
            "adapter": "human_review",
        },
        {
            "id": "rev",
            "type": "human_review",
            "path": "evidence/review.md",
            "checker": "manual",
            "status": "passing",
        },
    ]
    (claim / "spec.yaml").write_text(yaml.dump(minimal), encoding="utf-8")

    results = run_evidence_checks(claim, dry_run=True)
    assert [r.evidence_id for r in results] == ["rev", "lean_a"]
    lean_calls = [w for w, c in calls if c == EvidenceClass.LEAN]
    assert lean_calls == [1]
    assert calls, "run_bounded must be invoked for class batches"


def test_cnot_perm_matches_identity_pair():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    src = claim / "artifacts/source.qasm"
    tgt = claim / "artifacts/target.qasm"
    p_src = apply_qasm_permutation(src)
    p_tgt = apply_qasm_permutation(tgt)
    # CX.CX is identity permutation; empty target is identity.
    assert p_src == p_tgt == list(range(4))


def test_max_dense_default_conservative():
    os.environ.pop("QSPECBENCH_MAX_DENSE_QUBITS", None)
    assert max_dense_qubits() == 8


def test_perm_rejects_oversized(monkeypatch, tmp_path):
    monkeypatch.setenv("QSPECBENCH_MAX_PERM_QUBITS", "2")
    qasm = tmp_path / "big.qasm"
    qasm.write_text("OPENQASM 3.0;\nqubit[3] q;\nx q[0];\n", encoding="utf-8")
    with pytest.raises(ValueError, match="permutation backend disabled for 3 qubits"):
        apply_qasm_permutation(qasm)
