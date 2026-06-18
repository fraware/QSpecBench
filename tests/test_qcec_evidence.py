"""QCEC equivalence evidence tests (skipped when mqt.qcec unavailable)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from qspecbench.evidence_runner import run_evidence_checks

REPO = Path(__file__).resolve().parents[1]

try:
    import mqt.qcec  # noqa: F401

    HAS_QCEC = True
except ImportError:
    HAS_QCEC = shutil.which("qcec") is not None

pytestmark = pytest.mark.skipif(not HAS_QCEC, reason="QCEC (mqt.qcec or qcec CLI) not installed")


def test_cnot_qcec_equivalence_passes():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    results = {r.evidence_id: r for r in run_evidence_checks(claim)}
    assert "qcec_equivalence" in results
    assert results["qcec_equivalence"].ok, results["qcec_equivalence"].errors


def test_qft_inverse_qcec_equivalence_passes():
    claim = REPO / "benchmarks/equivalence/qft_inverse_qft_small_instance"
    results = {r.evidence_id: r for r in run_evidence_checks(claim)}
    if "qcec_equivalence" not in results:
        pytest.skip("qcec evidence not declared on benchmark")
    assert results["qcec_equivalence"].ok, results["qcec_equivalence"].errors
