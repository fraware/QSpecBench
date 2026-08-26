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


def test_dynamic_profile_rejects_unsupported_predicate(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "c[0] = measure q[0];\n"
        "if (c[0] == 0) x q[1];\n",
    )
    with pytest.raises(UnsupportedQasmError, match="single-bit predicates"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_unset_classical_bit(tmp_path: Path) -> None:
    path = _write(tmp_path, "if (c[0] == 1) x q[1];\n")
    with pytest.raises(UnsupportedQasmError, match="unset measurement bit"):
        simulate_instrument_feedforward_v2(path)


def test_dynamic_profile_rejects_reset(tmp_path: Path) -> None:
    path = _write(tmp_path, "reset q[0];\n")
    with pytest.raises(UnsupportedQasmError, match="unsupported executable construct"):
        simulate_instrument_feedforward_v2(path)
