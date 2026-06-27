"""Tests for extended OpenQASM gate matrix extraction."""

from __future__ import annotations

import math
import tempfile
from fractions import Fraction
from pathlib import Path

import pytest

from qspecbench.qasm_matrix import (
    UnsupportedQasmError,
    cells_close,
    extract_matrix,
    matrices_equal,
    matrix_from_json_rows,
)


def _matrix_from_qasm(qasm: str):
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        data = extract_matrix(path)
        return matrix_from_json_rows(data["matrix"])
    finally:
        path.unlink(missing_ok=True)


def _extract_from_qasm(qasm: str):
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        return extract_matrix(path)
    finally:
        path.unlink(missing_ok=True)


def _cell(re: Fraction | int = 0, im: Fraction | int = 0):
    return (Fraction(re), Fraction(im))


def test_rx_pi2_is_proper_rotation_not_h():
    m_rx = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nrx(1.57079632679) q[0];\n")
    m_h = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nh q[0];\n")
    assert m_rx != m_h
    c = Fraction(math.cos(math.pi / 4)).limit_denominator(10**12)
    assert cells_close(m_rx[0][0], _cell(c))
    assert cells_close(m_rx[0][1], _cell(im=-c))


def test_s_gate_phase_on_one():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ns q[0];\n")
    assert m[0][0] == _cell(1)
    assert m[1][1] == _cell(im=1)


def test_t_gate_phase_on_one():
    c = Fraction(math.cos(math.pi / 4)).limit_denominator(10**12)
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nt q[0];\n")
    assert m[0][0] == _cell(1)
    assert m[1][1] == _cell(c, c)


def test_sdg_gate_phase_on_one():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nsdg q[0];\n")
    assert m[0][0] == _cell(1)
    assert m[1][1] == _cell(im=-1)


def test_tdg_gate_phase_on_one():
    c = Fraction(math.cos(math.pi / 4)).limit_denominator(10**12)
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ntdg q[0];\n")
    assert m[0][0] == _cell(1)
    assert m[1][1] == _cell(c, -c)


def test_t_squared_equals_s_phase():
    m_t2 = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nt q[0];\nt q[0];\n")
    m_s = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ns q[0];\n")
    assert cells_close(m_t2[1][1], m_s[1][1])


def test_phase_cancellation_s_sdg():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ns q[0];\nsdg q[0];\n")
    eye = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\n")
    assert m == eye


def test_phase_cancellation_t_tdg():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nt q[0];\ntdg q[0];\n")
    eye = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\n")
    assert matrices_equal(m, eye)


def test_ccx_is_permutation():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[3] q;\nccx q[0], q[1], q[2];\n")
    dim = 8
    for row in m:
        assert sum(1 for x in row if x != _cell()) == 1
    assert len(m) == dim


def test_swap_exchanges_qubits():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[2] q;\nswap q[0], q[1];\n")
    col = 1
    row_one = next(i for i in range(4) if m[i][col] == _cell(1))
    assert row_one == 2


def test_general_rx_theta():
    theta = math.pi / 4
    m = _matrix_from_qasm(f"OPENQASM 3.0;\nqubit[1] q;\nrx({theta}) q[0];\n")
    half = theta / 2.0
    c = Fraction(math.cos(half)).limit_denominator(10**12)
    s = Fraction(math.sin(half)).limit_denominator(10**12)
    assert m[0][0] == _cell(c)
    assert m[0][1] == _cell(im=-s)
    assert m[1][0] == _cell(im=-s)
    assert m[1][1] == _cell(c)


def test_rz_gate_supported():
    data = _extract_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nrz(1.57079632679) q[0];\n")
    assert len(data["gates_applied"]) == 1


def test_ry_gate_supported():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nry(1.57079632679) q[0];\n")
    c = Fraction(math.cos(math.pi / 4)).limit_denominator(10**12)
    assert cells_close(m[0][0], _cell(c))


def test_cz_gate_supported():
    m = _matrix_from_qasm("OPENQASM 3.0;\nqubit[2] q;\ncz q[0], q[1];\n")
    assert m[3][3] == _cell(-1)


def test_u_gate_supported():
    data = _extract_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nu(1.57079632679,0,0) q[0];\n")
    assert len(data["gates_applied"]) == 1


def test_unsupported_rotation_gate_fails_closed():
    with pytest.raises(UnsupportedQasmError):
        _extract_from_qasm("OPENQASM 3.0;\nqubit[1] q;\nr1(0.5) q[0];\n")


def test_cp_gate_supported():
    data = _extract_from_qasm("OPENQASM 3.0;\nqubit[2] q;\ncp(0.7853981634) q[0], q[1];\n")
    assert len(data["gates_applied"]) == 1


def test_unknown_line_fails_closed():
    with pytest.raises(UnsupportedQasmError):
        _extract_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ngibberish q[0];\n")


def test_unsupported_error_is_value_error():
    # Fail-closed errors remain ValueErrors for callers catching the base type.
    with pytest.raises(ValueError):
        _extract_from_qasm("OPENQASM 3.0;\nqubit[1] q;\ngibberish_gate q[0];\n")


def test_measurement_fail_closed_without_extraction_policy():
    qasm = (
        "OPENQASM 3.0;\n"
        'include "stdgates.inc";\n'
        "qubit[2] q;\n"
        "bit[2] c;\n"
        "h q[0];\n"
        "cx q[0], q[1];\n"
        "c[0] = measure q[0];\n"
    )
    with pytest.raises(UnsupportedQasmError):
        _extract_from_qasm(qasm)


def test_measurement_skipped_with_unitary_fragment_policy():
    qasm = (
        "OPENQASM 3.0;\n"
        'include "stdgates.inc";\n'
        "qubit[2] q;\n"
        "bit[2] c;\n"
        "h q[0];\n"
        "cx q[0], q[1];\n"
        "barrier q;\n"
        "c[0] = measure q[0];\n"
        "c[1] = measure q[1];\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".qasm", delete=False, encoding="utf-8") as f:
        f.write(qasm)
        path = Path(f.name)
    try:
        extraction = {"mode": "unitary_fragment", "allowed_to_skip": ["measurement", "structural"]}
        data = extract_matrix(path, extraction=extraction)
        assert data["n_qubits"] == 2
        assert data["gates_applied"] == ["h q[0];", "cx q[0], q[1];"]
    finally:
        path.unlink(missing_ok=True)
