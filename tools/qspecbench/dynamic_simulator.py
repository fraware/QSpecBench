"""Operational dynamic-circuit simulation for small OpenQASM fragments.

Provides projective measurement semantics on top of the unitary gate model in
``qasm_matrix``. This closes part of the ``full_dynamic_semantics`` gap for
fixed small instances; it is not kernel-checked and does not model full OpenQASM
classical control or feed-forward inside the artifact unless explicitly declared.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from qspecbench.qasm_matrix import (
    UnsupportedQasmError,
    _GATE_LINE,
    _RX_LINE,
    _SQRT2_HALF,
    _RY_LINE,
    _RZ_LINE,
    _U_LINE,
    _CP_LINE,
    _ccx,
    _classical_control_metadata,
    _cnot,
    _cp,
    _cz,
    _eye,
    _is_skippable_nonunitary,
    _kron,
    _line_skip_category,
    _parse_angle,
    _parse_angle_list,
    _parse_qubit_args,
    _parse_qubit_index,
    _register_size,
    _rx_matrix,
    _ry_matrix,
    _rz_matrix,
    _single_qubit_gate,
    _swap,
    _u_matrix,
    cell_from_json,
    cell_to_json,
    extract_matrix,
    matrix_from_json_rows,
)

_MEASURE_LINE = re.compile(
    r"^\s*(\w+(?:\[\d+\])?)\s*=\s*measure\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)
_IF_LINE = re.compile(
    r"^\s*if\s*\(([^)]+)\)\s*(.+);?\s*$",
    re.IGNORECASE,
)


def _vec_norm(st: list[tuple[Fraction, Fraction]]) -> float:
    return math.sqrt(sum(float(r * r + i * i) for r, i in st))


def _normalize(st: list[tuple[Fraction, Fraction]]) -> list[tuple[Fraction, Fraction]]:
    n = _vec_norm(st)
    if n == 0:
        return st
    inv = Fraction(1) / Fraction(n).limit_denominator(10**12)
    return [(r * inv, i * inv) for r, i in st]


def _basis_index(n: int, qubit: int, bit: int) -> int:
    return bit << qubit


def _apply_unitary_matrix(
    st: list[tuple[Fraction, Fraction]],
    mat: list[list[tuple[Fraction, Fraction]]],
) -> list[tuple[Fraction, Fraction]]:
    dim = len(st)
    out = [(Fraction(0), Fraction(0)) for _ in range(dim)]
    for j in range(dim):
        acc_r = Fraction(0)
        acc_i = Fraction(0)
        for i in range(dim):
            mr, mi = mat[j][i]
            sr, si = st[i]
            acc_r += mr * sr - mi * si
            acc_i += mr * si + mi * sr
        out[j] = (acc_r, acc_i)
    return out


def _measure_qubit(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    qubit: int,
) -> tuple[int, list[tuple[Fraction, Fraction]], float]:
    """Projective measurement in computational basis; returns outcome, collapsed state, prob."""
    dim = 1 << n
    prob0 = Fraction(0)
    for idx in range(dim):
        if ((idx >> qubit) & 1) == 0:
            r, i = st[idx]
            prob0 += r * r + i * i
    p0 = float(prob0)
    if p0 >= 1.0 - 1e-12:
        outcome = 0
    elif p0 <= 1e-12:
        outcome = 1
    else:
        raise ValueError(
            f"non-deterministic measurement on qubit {qubit} in operational simulator "
            f"(prob0={p0}); use basis-state inputs only"
        )
    collapsed = [(Fraction(0), Fraction(0)) for _ in range(dim)]
    for idx in range(dim):
        if ((idx >> qubit) & 1) == outcome:
            collapsed[idx] = st[idx]
    collapsed = _normalize(collapsed)
    return outcome, collapsed, p0 if outcome == 0 else 1.0 - p0


def _apply_pauli_x(st: list[tuple[Fraction, Fraction]], n: int, qubit: int) -> list[tuple[Fraction, Fraction]]:
    dim = 1 << n
    out = [(Fraction(0), Fraction(0)) for _ in range(dim)]
    for idx in range(dim):
        flipped = idx ^ (1 << qubit)
        out[flipped] = st[idx]
    return out


def _apply_pauli_z(st: list[tuple[Fraction, Fraction]], n: int, qubit: int) -> list[tuple[Fraction, Fraction]]:
    out: list[tuple[Fraction, Fraction]] = []
    for idx, (r, i) in enumerate(st):
        if (idx >> qubit) & 1:
            out.append((-r, -i))
        else:
            out.append((r, i))
    return out


def _initial_state(n: int, amplitudes: dict[int, tuple[Fraction, Fraction]] | None) -> list[tuple[Fraction, Fraction]]:
    dim = 1 << n
    st = [(Fraction(0), Fraction(0)) for _ in range(dim)]
    if amplitudes:
        for idx, amp in amplitudes.items():
            if idx < 0 or idx >= dim:
                raise ValueError(f"amplitude index {idx} out of range for {n} qubits")
            st[idx] = amp
    else:
        st[0] = (Fraction(1), Fraction(0))
    return _normalize(st)


def _scale_matrix(
    mat: list[list[tuple[Fraction, Fraction]]],
    factor: Fraction,
) -> list[list[tuple[Fraction, Fraction]]]:
    return [[(r * factor, i * factor) for r, i in row] for row in mat]


def _tensor_product_on_qubit(
    n_qubits: int,
    qubit: int,
    op: list[list[tuple[Fraction, Fraction]]],
) -> list[list[tuple[Fraction, Fraction]]]:
    """Place ``op`` on OpenQASM wire ``q[i]`` (bit ``i`` in state index; matches ``_cnot``).

    ``qasm_matrix._apply_single`` uses a legacy Kronecker order aligned with Lean ``kron2I`` /
    ``kronI2`` for verify-bridge matrix extraction. The operational dynamic simulator must
    agree with ``_cnot`` and projective measurement on the same ``q[i]`` labels.
    """
    factors = [op if q == qubit else _eye(2) for q in range(n_qubits)]
    result = factors[0]
    for factor in factors[1:]:
        result = _kron(factor, result)
    return result


def _single_qasm(n_qubits: int, gate: str, qubit: int) -> list[list[tuple[Fraction, Fraction]]]:
    return _tensor_product_on_qubit(n_qubits, qubit, _single_qubit_gate(gate))


def _apply_gate_line(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    line: str,
) -> list[tuple[Fraction, Fraction]]:
    rx = _RX_LINE.match(line)
    if rx:
        q = _parse_qubit_index(rx.group(2), n)
        op = _tensor_product_on_qubit(n, q, _rx_matrix(_parse_angle(rx.group(1))))
        return _apply_unitary_matrix(st, op)
    ry = _RY_LINE.match(line)
    if ry:
        q = _parse_qubit_index(ry.group(2), n)
        op = _tensor_product_on_qubit(n, q, _ry_matrix(_parse_angle(ry.group(1))))
        return _apply_unitary_matrix(st, op)
    rz = _RZ_LINE.match(line)
    if rz:
        q = _parse_qubit_index(rz.group(2), n)
        op = _tensor_product_on_qubit(n, q, _rz_matrix(_parse_angle(rz.group(1))))
        return _apply_unitary_matrix(st, op)
    u = _U_LINE.match(line)
    if u:
        angles = _parse_angle_list(u.group(1))
        q = _parse_qubit_index(u.group(2), n)
        op = _tensor_product_on_qubit(n, q, _u_matrix(angles[0], angles[1], angles[2]))
        return _apply_unitary_matrix(st, op)
    cp = _CP_LINE.match(line)
    if cp:
        args = _parse_qubit_args(cp.group(2), n)
        op = _cp(n, args[0], args[1], _parse_angle(cp.group(1)))
        return _apply_unitary_matrix(st, op)
    m = _GATE_LINE.match(line)
    if not m:
        raise UnsupportedQasmError(f"unsupported gate line in dynamic simulator: {line!r}")
    gate = m.group(1).lower()
    args = _parse_qubit_args(m.group(2), n)
    if gate in {"cx", "cnot"}:
        op = _cnot(n, args[0], args[1])
    elif gate == "ccx":
        op = _ccx(n, args[0], args[1], args[2])
    elif gate == "swap":
        op = _swap(n, args[0], args[1])
    elif gate == "cz":
        op = _cz(n, args[0], args[1])
    else:
        op = _single_qasm(n, gate, args[0])
        if gate == "h":
            op = _scale_matrix(op, _SQRT2_HALF)
    return _apply_unitary_matrix(st, op)


def _project_measurement(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    qubit: int,
    outcome: int,
) -> list[tuple[Fraction, Fraction]]:
    dim = 1 << n
    collapsed = [(Fraction(0), Fraction(0)) for _ in range(dim)]
    for idx in range(dim):
        if ((idx >> qubit) & 1) == outcome:
            collapsed[idx] = st[idx]
    return _normalize(collapsed)


def _measurement_outcome_probability(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    qubit: int,
    outcome: int,
) -> float:
    dim = 1 << n
    prob = Fraction(0)
    for idx in range(dim):
        if ((idx >> qubit) & 1) == outcome:
            r, i = st[idx]
            prob += r * r + i * i
    return float(prob)


def simulate_dynamic_circuit(
    qasm_path: Path,
    extraction: dict[str, Any] | None = None,
    *,
    initial_amplitudes: dict[int, tuple[Fraction, Fraction]] | None = None,
    pauli_corrections: dict[str, list[tuple[str, int]]] | None = None,
) -> dict[str, Any]:
    """Simulate a small dynamic QASM circuit with projective measurement.

    ``pauli_corrections`` maps classical register tuples (e.g. ``"0,1"``) to a list of
    ``("X"|"Z", qubit)`` corrections applied after measurement (teleportation tables).
    """
    text = qasm_path.read_text(encoding="utf-8")
    n = _register_size(text)
    if n > 4:
        raise ValueError("operational dynamic simulator supports at most 4 qubits")
    state = _initial_state(n, initial_amplitudes)
    classical: dict[str, int] = {}
    steps: list[dict[str, Any]] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.lower().startswith("openqasm"):
            continue
        if line.lower().startswith("include"):
            continue

        meas = _MEASURE_LINE.match(line)
        if meas:
            reg, qref = meas.group(1), meas.group(2)
            qubit = _parse_qubit_index(qref, n)
            outcome, state, prob = _measure_qubit(state, n, qubit)
            classical[reg] = outcome
            steps.append({
                "kind": "measure",
                "line": line,
                "qubit": qubit,
                "classical_register": reg,
                "outcome": outcome,
                "probability": prob,
            })
            continue

        if_line = _IF_LINE.match(line)
        if if_line:
            pred, body = if_line.group(1).strip(), if_line.group(2).strip()
            if not _is_skippable_nonunitary(line, extraction):
                raise UnsupportedQasmError(f"classical control not allowed without extraction policy: {line!r}")
            meta = _classical_control_metadata(line)
            applied = False
            if re.match(r"^(\w+)\s*==\s*1$", pred):
                reg = re.match(r"^(\w+)\s*==\s*1$", pred).group(1)  # type: ignore[union-attr]
                if classical.get(reg) == 1:
                    state = _apply_gate_line(state, n, body if body.endswith(";") else body + ";")
                    applied = True
            steps.append({
                "kind": "classical_control",
                "line": line,
                "predicate": pred,
                "applied": applied,
                "metadata": meta,
            })
            continue

        rx = _RX_LINE.match(line)
        if rx:
            state = _apply_gate_line(state, n, line if line.endswith(";") else line + ";")
            steps.append({"kind": "gate", "line": line})
            continue

        category = _line_skip_category(line)
        if category and _is_skippable_nonunitary(line, extraction):
            steps.append({"kind": "skipped", "line": line, "category": category})
            continue
        if category:
            raise UnsupportedQasmError(
                f"dynamic simulator cannot skip {category!r} without extraction policy: {line!r}"
            )

        state = _apply_gate_line(state, n, line if line.endswith(";") else line + ";")
        steps.append({"kind": "gate", "line": line})

    if pauli_corrections:
        regs = sorted(
            classical.keys(),
            key=lambda r: int(m.group()) if (m := re.search(r"\d+", r)) else 0,
        )
        key = ",".join(str(classical[r]) for r in regs)
        for op, qubit in pauli_corrections.get(key, []):
            if op == "X":
                state = _apply_pauli_x(state, n, qubit)
            elif op == "Z":
                state = _apply_pauli_z(state, n, qubit)
            else:
                raise ValueError(f"unsupported correction {op!r}")
        steps.append({"kind": "pauli_corrections", "classical_key": key, "ops": pauli_corrections.get(key, [])})

    return {
        "simulation_model": "statevector_projective_v0",
        "n_qubits": n,
        "classical_registers": classical,
        "steps": steps,
        "final_amplitudes": {str(i): cell_to_json(state[i]) for i in range(len(state)) if state[i] != (0, 0)},
        "operational_note": (
            "Python operational simulator; not kernel-checked. Classical control applies "
            "only when predicate matches recorded measurement bits."
        ),
    }


def reduced_qubit_amplitudes(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    qubit: int,
) -> tuple[Fraction, Fraction]:
    """Dominant amplitude on ``qubit`` (largest-magnitude branch)."""
    dim = 1 << n
    best0 = (Fraction(0), Fraction(0))
    best1 = (Fraction(0), Fraction(0))
    mag0 = Fraction(-1)
    mag1 = Fraction(-1)
    for idx in range(dim):
        r, i = st[idx]
        m = r * r + i * i
        if m == 0:
            continue
        if (idx >> qubit) & 1 == 0 and m > mag0:
            mag0 = m
            best0 = (r, i)
        elif (idx >> qubit) & 1 == 1 and m > mag1:
            mag1 = m
            best1 = (r, i)
    chosen = best0 if mag0 >= mag1 else best1
    norm = (chosen[0] * chosen[0] + chosen[1] * chosen[1]).limit_denominator(10**12)
    if norm == 0:
        return (Fraction(1), Fraction(0))
    inv = norm ** Fraction(-1, 2) if isinstance(norm, Fraction) else Fraction(1)
    # approximate normalize for comparison
    length = float(chosen[0] * chosen[0] + chosen[1] * chosen[1]) ** 0.5
    if length == 0:
        return (Fraction(1), Fraction(0))
    return (Fraction(float(chosen[0]) / length).limit_denominator(10**9), Fraction(float(chosen[1]) / length).limit_denominator(10**9))


def qubit_bit_probability(
    st: list[tuple[Fraction, Fraction]],
    n: int,
    qubit: int,
    bit: int,
    *,
    classical_fixed: dict[int, int] | None = None,
) -> float:
    dim = 1 << n
    prob = Fraction(0)
    for idx in range(dim):
        if classical_fixed:
            skip = False
            for cq, cb in classical_fixed.items():
                if ((idx >> cq) & 1) != cb:
                    skip = True
                    break
            if skip:
                continue
        if ((idx >> qubit) & 1) == bit:
            r, i = st[idx]
            prob += r * r + i * i
    return float(prob)


def state_after_unitary_prefix(
    qasm_path: Path,
    extraction: dict[str, Any] | None,
    initial_amplitudes: dict[int, tuple[Fraction, Fraction]] | None = None,
) -> tuple[int, list[tuple[Fraction, Fraction]]]:
    """Apply the unitary prefix using the same ``extract_matrix`` model as bridge checks."""
    data = extract_matrix(qasm_path, extraction=extraction)
    n = data["n_qubits"]
    dim = 1 << n
    st = _initial_state(n, initial_amplitudes)
    if len(st) != dim:
        raise ValueError(f"state dimension {len(st)} != 2**{n}")
    unitary = matrix_from_json_rows(data["matrix"])
    st = _apply_unitary_matrix(st, unitary)
    return n, _normalize(st)


def state_after_unitary_prefix_normalized(
    qasm_path: Path,
    extraction: dict[str, Any] | None,
    initial_amplitudes: dict[int, tuple[Fraction, Fraction]] | None = None,
) -> tuple[int, list[tuple[Fraction, Fraction]]]:
    """Apply gate lines before measurement using complex-normalized single-qubit gates."""
    text = qasm_path.read_text(encoding="utf-8")
    n = _register_size(text)
    state = _initial_state(n, initial_amplitudes)
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.lower().startswith("openqasm"):
            continue
        if line.lower().startswith("include"):
            continue
        if _MEASURE_LINE.match(line) or _IF_LINE.match(line):
            break
        category = _line_skip_category(line)
        if category and _is_skippable_nonunitary(line, extraction):
            continue
        if category:
            break
        state = _apply_gate_line(state, n, line if line.endswith(";") else line + ";")
    return n, _normalize(state)


def _basis_check_for_state(
    state: list[tuple[Fraction, Fraction]],
    n: int,
    *,
    label: str,
    receiver_qubit: int,
    corrections: dict[str, list[tuple[str, int]]],
) -> dict[str, Any]:
    branch_ok = True
    branch_details: list[dict[str, Any]] = []
    for c0 in (0, 1):
        for c1 in (0, 1):
            p0 = _measurement_outcome_probability(state, n, 0, c0)
            if p0 < 1e-9:
                continue
            s1 = _project_measurement(state, n, 0, c0)
            p1 = _measurement_outcome_probability(s1, n, 1, c1)
            if p1 < 1e-9:
                continue
            collapsed = _project_measurement(s1, n, 1, c1)
            key = f"{c0},{c1}"
            for op, qubit in corrections.get(key, []):
                if op == "X":
                    collapsed = _apply_pauli_x(collapsed, n, qubit)
                elif op == "Z":
                    collapsed = _apply_pauli_z(collapsed, n, qubit)
            target_bit = 0 if label == "|0>" else 1
            prob = qubit_bit_probability(
                collapsed, n, receiver_qubit, target_bit, classical_fixed={0: c0, 1: c1},
            )
            ok = prob > 0.999
            branch_ok = branch_ok and ok
            branch_details.append({
                "classical": key,
                "branch_probability": p0 * p1,
                "receiver_bit_probability": prob,
                "ok": ok,
            })
    return {"input": label, "branches": branch_details, "ok": branch_ok}


def verify_teleportation_basis_states(
    qasm_path: Path,
    extraction: dict[str, Any] | None,
    receiver_qubit: int = 2,
    *,
    artifact_role: str = "source",
) -> dict[str, Any]:
    """Check |0>, |1> teleportation with documented Pauli corrections (branch enumeration).

    Primary check uses complex-normalized gate application on the unitary prefix.
    Int-scaffold diagnostics (``extract_matrix``) are included for calibration when they differ.
    """
    # Textbook σ_x^{c1} σ_z^{c0} on Bob's qubit (apply Z when c0=1, then X when c1=1).
    corrections = {
        "0,0": [],
        "0,1": [("X", receiver_qubit)],
        "1,0": [("Z", receiver_qubit)],
        "1,1": [("Z", receiver_qubit), ("X", receiver_qubit)],
    }
    results: list[dict[str, Any]] = []
    int_scaffold_results: list[dict[str, Any]] = []
    for label, init in (
        ("|0>", {0: (Fraction(1), Fraction(0))}),
        ("|1>", {1: (Fraction(0), Fraction(1))}),
    ):
        n_norm, state_norm = state_after_unitary_prefix_normalized(qasm_path, extraction, init)
        results.append(
            _basis_check_for_state(
                state_norm, n_norm, label=label, receiver_qubit=receiver_qubit, corrections=corrections,
            )
        )
        n_int, state_int = state_after_unitary_prefix(qasm_path, extraction, init)
        int_scaffold_results.append(
            _basis_check_for_state(
                state_int, n_int, label=label, receiver_qubit=receiver_qubit, corrections=corrections,
            )
        )
    all_ok = all(r["ok"] for r in results)
    int_all_ok = all(r["ok"] for r in int_scaffold_results)
    failure_mode = None if all_ok else "receiver_marginal_uniform_after_documented_corrections"
    calibration_note = (
        "Basis enumeration with the documented correction table does not restore |0>/|1> "
        "on the receiver under complex-normalized gates (operational wire model). "
        "See docs/operational_semantics.md."
        if failure_mode
        else (
            "Basis-state teleportation check passed under complex-normalized unitary prefix "
            "with OpenQASM-consistent single-qubit/CNOT wire indexing."
        )
    )
    return {
        "type": "teleportation_basis_check_v0",
        "artifact_role": artifact_role,
        "receiver_qubit": receiver_qubit,
        "correction_table": "informal_derivation.md",
        "gate_model": "complex_normalized_unitary_prefix",
        "failure_mode": failure_mode,
        "calibration_note": calibration_note,
        "results": results,
        "all_ok": all_ok,
        "int_scaffold_diagnostic": {
            "gate_model": "extract_matrix_int_scaffold_unitary_prefix",
            "all_ok": int_all_ok,
            "results": int_scaffold_results,
            "note": (
                "Int scaffold (verify-bridge / Lean kron2I-kronI2 order) uses a different "
                "single-qubit wire convention than operational dynamic simulation; basis "
                "restoration failure here is expected until scaffold alignment is proved."
            ),
        },
        "not_checked": (
            ["arbitrary_state", "kernel_checked"]
            if artifact_role == "supplementary_feedforward"
            else ["arbitrary_state", "feed_forward_in_artifact", "kernel_checked"]
        ),
    }


def write_dynamic_simulation_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
