"""Executable conformance tests for the bounded dynamic profile v2."""

from __future__ import annotations

from pathlib import Path

import pytest

from qspecbench.dynamic_profile import simulate_instrument_feedforward_v2
from qspecbench.qasm_matrix import UnsupportedQasmError


def _write(tmp_path: Path, body: str, *, header: str = "OPENQASM 3.0;") -> Path:
    path = tmp_path / "dynamic.qasm"
    path.write_text(
        f"{header}\n"
        'include "stdgates.inc";\n'
        "qubit[2] q;\n"
        "bit[1] c;\n"
        f"{body}",
        encoding="utf-8",
    )
    return path


def test_indexed_measurement_bit_feedforward_is_applied(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "x q[0];\n"
        "c[0] = measure q[0];\n"
        "if (c[0] == 1) x q[1];\n",
    )
    result = simulate_instrument_feedforward_v2(path)
    assert result["classical_registers"] == {"c[0]": 1}
    assert set(result["final_amplitudes"]) == {"3"}
    assert result["numeric_semantics"] == "Fraction-based rational approximation"
    controls = [step for step in result["steps"] if step["kind"] == "classical_control"]
    assert controls == [
        {
            "kind": "classical_control",
            "line": "if (c[0] == 1) x q[1];",
            "predicate": "c[0] == 1",
            "register": "c[0]",
            "applied": True,
        }
    ]


def test_false_indexed_feedforward_branch_is_explicit(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "c[0] = measure q[0];\n"
        "if (c[0] == 1) x q[1];\n",
    )
    result = simulate_instrument_feedforward_v2(path)
    assert result["classical_registers"] == {"c[0]": 0}
    assert set(result["final_amplitudes"]) == {"0"}
    control = next(step for step in result["steps"] if step["kind"] == "classical_control")
    assert control["applied"] is False


def test_dynamic_profile_rejects_wrong_upstream_version(tmp_path: Path) -> None:
    path = _write(tmp_path, "x q[0];\n", header="OPENQASM 3.1;")
    with pytest.raises(UnsupportedQasmError, match="OPENQASM 3.0"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unterminated_header(tmp_path: Path) -> None:
    path = _write(tmp_path, "x q[0];\n", header="OPENQASM 3.0")
    with pytest.raises(UnsupportedQasmError, match="leading 'OPENQASM 3.0;'"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unsupported_predicate(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "c[0] = measure q[0];\n"
        "if (c[0] == 0) x q[1];\n",
    )
    with pytest.raises(UnsupportedQasmError, match="indexed predicates"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unset_classical_bit(tmp_path: Path) -> None:
    path = _write(tmp_path, "if (c[0] == 1) x q[1];\n")
    with pytest.raises(UnsupportedQasmError, match="unset measurement bit"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unterminated_conditional(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "c[0] = measure q[0];\n"
        "if (c[0] == 1) x q[1]\n",
    )
    with pytest.raises(UnsupportedQasmError, match="malformed conditional"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_reset(tmp_path: Path) -> None:
    path = _write(tmp_path, "reset q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="unsupported executable construct"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_undeclared_measurement_bit(tmp_path: Path) -> None:
    path = _write(tmp_path, "d[0] = measure q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="register 'd' is not declared"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_out_of_range_measurement_bit(tmp_path: Path) -> None:
    path = _write(tmp_path, "c[1] = measure q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="outside declared bit\\[1\\] c"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_legacy_q0_measurement_alias(tmp_path: Path) -> None:
    path = _write(tmp_path, "c[0] = measure q0;\n")
    with pytest.raises(UnsupportedQasmError, match="malformed measurement"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unterminated_measurement(tmp_path: Path) -> None:
    path = _write(tmp_path, "c[0] = measure q[0]\n")
    with pytest.raises(UnsupportedQasmError, match="malformed measurement"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_malformed_include(tmp_path: Path) -> None:
    path = tmp_path / "bad-include.qasm"
    path.write_text(
        "OPENQASM 3.0;\n"
        "include stdgates.inc;\n"
        "qubit[2] q;\n"
        "bit[1] c;\n"
        "x q[0];\n",
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedQasmError, match="malformed include"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_wrong_qubit_register_name(tmp_path: Path) -> None:
    path = tmp_path / "wrong-register.qasm"
    path.write_text(
        "OPENQASM 3.0;\n"
        "qubit[2] r;\n"
        "bit[1] c;\n"
        "x q[0];\n",
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedQasmError, match="exactly one declaration"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_comments_cannot_spoof_qubit_register_size(tmp_path: Path) -> None:
    path = tmp_path / "commented-register.qasm"
    path.write_text(
        "OPENQASM 3.0;\n"
        "// qubit[4] q; must not influence parser state\n"
        "qubit[2] q;\n"
        "bit[1] c;\n"
        "x q[0];\n",
        encoding="utf-8",
    )
    result = simulate_instrument_feedforward_v2(path)
    assert result["n_qubits"] == 2
