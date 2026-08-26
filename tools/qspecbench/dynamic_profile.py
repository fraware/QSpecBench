"""Executable interpreter for the bounded dynamic-instrument semantic profile.

This module defines the v2 profile boundary rather than changing the historical
``simulate_dynamic_circuit`` entry point. The supported language is intentionally
small and explicit: exact OpenQASM 3.0 header, one ``qubit[n] q`` declaration,
explicit vector bit declarations, QSpecBench's bounded gate subset,
computational-basis measurements, and indexed single-bit ``== 1`` feed-forward.
Everything else fails closed.
"""

from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path
from typing import Any

from qspecbench.dynamic_simulator import (
    MAX_OPERATIONAL_QUBITS,
    _MEASURE_LINE,
    _apply_gate_line,
    _apply_pauli_x,
    _apply_pauli_z,
    _initial_state,
    _measure_qubit,
)
from qspecbench.qasm_matrix import UnsupportedQasmError, cell_to_json

_PROFILE_VERSION = "statevector_projective_v2"
_HEADER = "OPENQASM 3.0"
_QUBIT_DECL = re.compile(r"^qubit\s*\[\s*(\d+)\s*\]\s+q\s*;?$")
_BIT_DECL = re.compile(r"^bit\s*\[\s*(\d+)\s*\]\s+([A-Za-z_]\w*)\s*;?$")
_CLASSICAL_REF = re.compile(r"^([A-Za-z_]\w*)\[(\d+)\]$")
_IF_LINE = re.compile(r"^if\s*\(([^)]+)\)\s*(.+);?\s*$", re.IGNORECASE)
_PREDICATE = re.compile(
    r"^([A-Za-z_]\w*\[\d+\])\s*==\s*1$",
    re.IGNORECASE,
)


def _clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def _validate_header(lines: list[str]) -> None:
    headers = [
        line.rstrip(";").strip()
        for line in lines
        if line.lower().startswith("openqasm")
    ]
    if headers != [_HEADER]:
        raise UnsupportedQasmError(
            "dynamic profile requires exactly one 'OPENQASM 3.0;' header; "
            f"found {headers!r}"
        )


def _declared_qubit_count(lines: list[str]) -> int:
    declarations = [
        match
        for line in lines
        if (match := _QUBIT_DECL.fullmatch(line)) is not None
    ]
    if len(declarations) != 1:
        raise UnsupportedQasmError(
            "dynamic profile requires exactly one declaration 'qubit[n] q;'"
        )
    n_qubits = int(declarations[0].group(1))
    if n_qubits <= 0:
        raise UnsupportedQasmError("qubit register width must be positive")
    if n_qubits > MAX_OPERATIONAL_QUBITS:
        raise ValueError(
            f"dynamic profile supports at most {MAX_OPERATIONAL_QUBITS} qubits"
        )
    return n_qubits


def _classical_sort_key(reference: str) -> tuple[str, int]:
    match = _CLASSICAL_REF.fullmatch(reference)
    if match is None:
        return (reference, -1)
    return (match.group(1), int(match.group(2)))


def _classical_key(registers: dict[str, int]) -> str:
    ordered = sorted(registers, key=_classical_sort_key)
    return ",".join(str(registers[name]) for name in ordered)


def _require_declared_bit(reference: str, bit_widths: dict[str, int]) -> None:
    match = _CLASSICAL_REF.fullmatch(reference)
    if match is None:
        raise UnsupportedQasmError(
            f"dynamic profile requires indexed classical-bit references, got {reference!r}"
        )
    name, raw_index = match.groups()
    width = bit_widths.get(name)
    if width is None:
        raise UnsupportedQasmError(f"classical bit register {name!r} is not declared")
    index = int(raw_index)
    if index >= width:
        raise UnsupportedQasmError(
            f"classical bit {reference!r} outside declared bit[{width}] {name}"
        )


def simulate_instrument_feedforward_v2(
    qasm_path: Path,
    *,
    initial_amplitudes: dict[int, tuple[Fraction, Fraction]] | None = None,
    pauli_corrections: dict[str, list[tuple[str, int]]] | None = None,
) -> dict[str, Any]:
    """Execute the v2 bounded dynamic profile and fail closed outside its grammar."""
    text = qasm_path.read_text(encoding="utf-8")
    lines = _clean_lines(text)
    _validate_header(lines)
    n_qubits = _declared_qubit_count(lines)

    state = _initial_state(n_qubits, initial_amplitudes)
    classical: dict[str, int] = {}
    bit_widths: dict[str, int] = {}
    steps: list[dict[str, Any]] = []

    for line in lines:
        lower = line.lower()
        if lower.startswith("openqasm"):
            continue
        if lower.startswith("include"):
            steps.append({"kind": "include_skipped", "line": line})
            continue

        if _QUBIT_DECL.fullmatch(line):
            continue
        if lower.startswith("qubit"):
            raise UnsupportedQasmError(
                "dynamic profile requires declaration 'qubit[n] q;'"
            )

        bit_declaration = _BIT_DECL.fullmatch(line)
        if bit_declaration:
            width = int(bit_declaration.group(1))
            name = bit_declaration.group(2)
            if width <= 0:
                raise UnsupportedQasmError("bit register width must be positive")
            if name == "q":
                raise UnsupportedQasmError("bit register name 'q' conflicts with qubit register")
            if name in bit_widths:
                raise UnsupportedQasmError(f"duplicate bit register {name!r}")
            bit_widths[name] = width
            continue
        if lower.startswith("bit"):
            raise UnsupportedQasmError(
                "dynamic profile requires declaration 'bit[n] name;'"
            )

        measurement = _MEASURE_LINE.match(line)
        if measurement:
            register, qref = measurement.group(1), measurement.group(2)
            _require_declared_bit(register, bit_widths)
            qubit_match = re.search(r"\[(\d+)\]", qref)
            if qubit_match is None:
                qubit_match = re.search(r"q(\d+)", qref.lower())
            if qubit_match is None:
                raise UnsupportedQasmError(f"cannot resolve measurement wire: {line!r}")
            qubit = int(qubit_match.group(1))
            if qubit < 0 or qubit >= n_qubits:
                raise UnsupportedQasmError(
                    f"measurement wire q[{qubit}] outside {n_qubits}-qubit register"
                )
            outcome, state, probability = _measure_qubit(state, n_qubits, qubit)
            classical[register] = outcome
            steps.append(
                {
                    "kind": "measure",
                    "line": line,
                    "qubit": qubit,
                    "classical_register": register,
                    "outcome": outcome,
                    "probability": probability,
                }
            )
            continue

        conditional = _IF_LINE.match(line)
        if conditional:
            predicate_text = conditional.group(1).strip()
            body = conditional.group(2).strip()
            predicate = _PREDICATE.fullmatch(predicate_text)
            if predicate is None:
                raise UnsupportedQasmError(
                    "dynamic profile supports only indexed predicates '<bit> == 1'; "
                    f"got {predicate_text!r}"
                )
            register = predicate.group(1)
            _require_declared_bit(register, bit_widths)
            if register not in classical:
                raise UnsupportedQasmError(
                    f"classical predicate references unset measurement bit {register!r}"
                )
            applied = classical[register] == 1
            if applied:
                state = _apply_gate_line(
                    state,
                    n_qubits,
                    body if body.endswith(";") else body + ";",
                )
            steps.append(
                {
                    "kind": "classical_control",
                    "line": line,
                    "predicate": predicate_text,
                    "register": register,
                    "applied": applied,
                }
            )
            continue

        unsupported_prefixes = (
            "reset ",
            "for ",
            "while ",
            "else",
            "gate ",
            "def ",
            "defcal",
        )
        if lower.startswith(unsupported_prefixes):
            raise UnsupportedQasmError(
                f"unsupported executable construct under dynamic profile v2: {line!r}"
            )

        # Gate parsing/arity/angle handling remains centralized in the operational gate engine.
        state = _apply_gate_line(
            state,
            n_qubits,
            line if line.endswith(";") else line + ";",
        )
        steps.append({"kind": "gate", "line": line})

    if pauli_corrections:
        key = _classical_key(classical)
        operations = pauli_corrections.get(key, [])
        for operation, qubit in operations:
            if qubit < 0 or qubit >= n_qubits:
                raise ValueError(
                    f"correction qubit {qubit} outside {n_qubits}-qubit register"
                )
            if operation == "X":
                state = _apply_pauli_x(state, n_qubits, qubit)
            elif operation == "Z":
                state = _apply_pauli_z(state, n_qubits, qubit)
            else:
                raise ValueError(f"unsupported correction {operation!r}")
        steps.append(
            {
                "kind": "pauli_corrections",
                "classical_key": key,
                "ops": operations,
            }
        )

    return {
        "simulation_model": _PROFILE_VERSION,
        "n_qubits": n_qubits,
        "wire_order": "openqasm_little_endian_wire_order",
        "numeric_semantics": "Fraction-based rational approximation",
        "classical_registers": classical,
        "steps": steps,
        "final_amplitudes": {
            str(index): cell_to_json(amplitude)
            for index, amplitude in enumerate(state)
            if amplitude != (0, 0)
        },
        "operational_note": (
            "Bounded Python statevector interpreter; not kernel-checked. "
            "Nondeterministic measurement outcomes fail closed."
        ),
    }
