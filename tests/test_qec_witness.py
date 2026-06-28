"""Tests for QEC witness hash export helper."""

from __future__ import annotations

import json
from pathlib import Path

from qspecbench.qec_witness import export_small_code_witness, syndrome_table_sha256

REPO = Path(__file__).resolve().parents[1]
BIT_FLIP = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"


def test_syndrome_table_sha256_stable():
    table_path = BIT_FLIP / "artifacts/syndrome_table.json"
    table = json.loads(table_path.read_text(encoding="utf-8"))
    h1 = syndrome_table_sha256(table)
    h2 = syndrome_table_sha256(table)
    assert h1 == h2
    assert len(h1) == 64


def test_export_small_code_witness_includes_syndrome_hash():
    witness = export_small_code_witness(
        syndrome_table_path=BIT_FLIP / "artifacts/syndrome_table.json",
        correction_table_path=BIT_FLIP / "artifacts/correction_table.json",
        complete_for="[[3,1,3]] bit-flip lookup decoder",
    )
    assert witness["method"] == "lookup_table"
    assert witness["syndrome_table_sha256"]
    assert witness["correction_table_sha256"]
    assert witness["complete_for"]
