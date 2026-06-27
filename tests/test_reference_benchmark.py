"""Reference benchmark and bulk evidence tests."""

from pathlib import Path

import yaml

from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.models import ALL_REFERENCE_LEVELS
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]


def test_reference_benchmark_exists():
    rows = list((REPO / "benchmarks").rglob("spec.yaml"))
    refs = []
    for p in rows:
        if "_template" in p.parts:
            continue
        spec = yaml.safe_load(p.read_text(encoding="utf-8"))
        if spec.get("status", {}).get("maturity") in ALL_REFERENCE_LEVELS:
            refs.append(p)
    assert len(refs) >= 8


def test_cnot_reference_validates():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = validate_path(claim)
    assert results and results[0].ok


def test_cnot_certificate_evidence_passes():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = {r.evidence_id: r for r in run_evidence_checks(claim)}
    assert results["unitary_equality_certificate"].ok


def test_check_evidence_all_flagships():
    flagships = [
        "benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction",
        "benchmarks/equivalence/cnot_self_inverse_cancellation",
        "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x",
        "benchmarks/hamiltonian/small_fermionic_hamiltonian_is_hermitian",
        "benchmarks/ai_formalization/formalize_no_cloning_statement",
    ]
    for rel in flagships:
        claim = REPO / rel
        runs = [r for r in run_evidence_checks(claim) if not r.skipped]
        assert runs, f"no runnable evidence for {rel}"
