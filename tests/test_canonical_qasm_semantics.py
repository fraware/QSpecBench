"""Regression tests for the canonical little-endian OpenQASM semantics."""

from __future__ import annotations

from pathlib import Path

import pytest

from qspecbench.canonical_qasm import extract_lsb_unitary
from qspecbench.dynamic_profile import simulate_instrument_feedforward_v2
from qspecbench.qasm_matrix import ComplexMatrix, UnsupportedQasmError, matrix_from_json_rows


def _write_qasm(tmp_path: Path, body: str, *, header: str = "OPENQASM 3.0;") -> Path:
    path = tmp_path / "circuit.qasm"
    path.write_text(f"{header}\nqubit[2] q;\n{body}", encoding="utf-8")
    return path


def _one_output_row(matrix: ComplexMatrix, input_column: int) -> int:
    rows = [row for row in range(len(matrix)) if matrix[row][input_column] != (0, 0)]
    assert len(rows) == 1
    return rows[0]


def test_q0_is_lsb_in_canonical_single_qubit_embedding(tmp_path: Path) -> None:
    q0 = extract_lsb_unitary(_write_qasm(tmp_path, "x q[0];\n"))
    matrix = matrix_from_json_rows(q0["matrix"])
    assert _one_output_row(matrix, 0) == 1

    q1 = extract_lsb_unitary(_write_qasm(tmp_path, "x q[1];\n"))
    matrix = matrix_from_json_rows(q1["matrix"])
    assert _one_output_row(matrix, 0) == 2


def test_single_and_controlled_gates_share_one_wire_order(tmp_path: Path) -> None:
    data = extract_lsb_unitary(
        _write_qasm(
            tmp_path,
            "x q[0];\n"
            "cx q[0], q[1];\n",
        )
    )
    matrix = matrix_from_json_rows(data["matrix"])

    # |00> --X(q0)--> |01> --CX(q0,q1)--> |11> under q[i] = bit weight 2**i.
    assert _one_output_row(matrix, 0) == 3
    assert data["wire_order"] == "openqasm_little_endian_wire_order"
    assert data["numeric_semantics"] == "Fraction-based rational approximation"


def test_static_and_dynamic_v2_agree_on_shared_fragment(tmp_path: Path) -> None:
    path = _write_qasm(
        tmp_path,
        "x q[0];\n"
        "cx q[0], q[1];\n",
    )
    static = extract_lsb_unitary(path)
    static_matrix = matrix_from_json_rows(static["matrix"])
    dynamic = simulate_instrument_feedforward_v2(path)

    assert _one_output_row(static_matrix, 0) == 3
    assert set(dynamic["final_amplitudes"]) == {"3"}
    assert dynamic["simulation_model"] == "statevector_projective_v2"
    assert dynamic["wire_order"] == static["wire_order"]


def test_canonical_unitary_profile_fails_closed_on_measurement(tmp_path: Path) -> None:
    path = _write_qasm(tmp_path, "measure q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="does not interpret 'measurement'"):
        extract_lsb_unitary(path)


def test_canonical_unitary_profile_fails_closed_on_classical_control(tmp_path: Path) -> None:
    path = _write_qasm(tmp_path, "if (c == 1) x q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="does not interpret 'classical_control'"):
        extract_lsb_unitary(path)


def test_canonical_unitary_profile_rejects_wrong_upstream_version(tmp_path: Path) -> None:
    path = _write_qasm(tmp_path, "x q[0];\n", header="OPENQASM 3.1;")
    with pytest.raises(UnsupportedQasmError, match="OPENQASM 3.0"):
        extract_lsb_unitary(path)


def test_canonical_unitary_profile_rejects_non_qubit_declarations(tmp_path: Path) -> None:
    path = _write_qasm(tmp_path, "bit[1] c;\nx q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="requires declaration 'qubit\\[n\\] q;'"):
        extract_lsb_unitary(path)


def test_canonical_unitary_profile_rejects_wrong_qubit_register_name(tmp_path: Path) -> None:
    path = tmp_path / "wrong-register.qasm"
    path.write_text(
        "OPENQASM 3.0;\n"
        "qubit[2] r;\n"
        "x q[0];\n",
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedQasmError, match="requires declaration 'qubit\\[n\\] q;'"):
        extract_lsb_unitary(path)


def test_canonical_unitary_profile_rejects_duplicate_qubit_register(tmp_path: Path) -> None:
    path = _write_qasm(tmp_path, "qubit[2] q;\nx q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="exactly one qubit register q"):
        extract_lsb_unitary(path)
