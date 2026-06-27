"""Extract unitary matrices from a restricted OpenQASM 3 gate subset."""

from __future__ import annotations

import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, TypeAlias

Cell: TypeAlias = tuple[Fraction, Fraction]
ComplexMatrix: TypeAlias = list[list[Cell]]

_GATE_LINE = re.compile(
    r"^\s*(h|x|y|z|s|t|sdg|tdg|cx|cnot|cz|swap|ccx)\s+(.*);?\s*$",
    re.IGNORECASE,
)
_ANGLE_ARG = r"([^)]+)"
_RX_LINE = re.compile(
    rf"^\s*rx\s*\(\s*{_ANGLE_ARG}\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)
_RY_LINE = re.compile(
    rf"^\s*ry\s*\(\s*{_ANGLE_ARG}\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)
_RZ_LINE = re.compile(
    rf"^\s*rz\s*\(\s*{_ANGLE_ARG}\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)
_U_LINE = re.compile(
    r"^\s*u\s*\(\s*([^)]+)\s*\)\s+(q\[\d+\]|q\d+)\s*;?\s*$",
    re.IGNORECASE,
)
_CP_LINE = re.compile(
    rf"^\s*cp\s*\(\s*{_ANGLE_ARG}\s*\)\s+(.*);?\s*$",
    re.IGNORECASE,
)

_ANGLE_LITERAL_RE = re.compile(
    r"^(?:"
    r"pi\s*/\s*2|(?:\(pi\s*/\s*2\))|"
    r"pi\s*/\s*4|(?:\(pi\s*/\s*4\))|"
    r"pi|(?:\(pi\))|"
    r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
    r")$",
    re.IGNORECASE,
)

_COMPLEX_TOLERANCE = Fraction(1, 10**9)
_SQRT2_HALF = Fraction(math.cos(math.pi / 4)).limit_denominator(10**12)

# Non-unitary / structural OpenQASM constructs that carry no unitary contribution
# and may therefore be skipped without affecting the extracted matrix.
_NONUNITARY_KEYWORDS = frozenset(
    {
        "measure",
        "reset",
        "barrier",
        "delay",
        "if",
        "else",
        "for",
        "while",
        "return",
        "break",
        "continue",
        "end",
        "box",
        "gate",
        "def",
        "defcal",
        "defcalgrammar",
        "cal",
        "extern",
        "pragma",
    }
)
_DECLARATION_KEYWORDS = frozenset(
    {
        "qubit",
        "bit",
        "creg",
        "qreg",
        "int",
        "uint",
        "float",
        "angle",
        "complex",
        "bool",
        "duration",
        "stretch",
        "const",
        "input",
        "output",
        "array",
        "let",
    }
)


class UnsupportedQasmError(ValueError):
    """Raised when a unitary-bearing QASM line cannot be modeled (fail-closed)."""


def _line_skip_category(line: str) -> str | None:
    """Classify a non-gate line for qasm_extraction policy (fail-closed by default)."""
    low = line.lower().strip()
    if low in {"{", "}"}:
        return "structural"
    if re.search(r"\bmeasure\b", low):
        return "measurement"
    if re.search(r"\breset\b", low):
        return "reset"
    if re.match(r"^(if|else|for|while)\b", low):
        return "classical_control"
    if re.match(r"^(gate|def|defcal)\b", low):
        return "gate_def"
    first = re.split(r"[\s\[\(;{}]", low, maxsplit=1)[0]
    if first in _NONUNITARY_KEYWORDS:
        if first in {"barrier", "delay", "pragma", "cal", "extern", "box"}:
            return "structural"
        if first in {"if", "else", "for", "while"}:
            return "classical_control"
        if first in {"gate", "def", "defcal", "defcalgrammar"}:
            return "gate_def"
        if first == "measure":
            return "measurement"
        if first == "reset":
            return "reset"
    if first in _DECLARATION_KEYWORDS:
        return "declaration"
    return None


def _extraction_allows_skip(extraction: dict[str, Any] | None, category: str) -> bool:
    if not extraction:
        return False
    mode = extraction.get("mode", "unitary_fragment")
    if mode == "full_dynamic_semantics":
        return True
    if mode == "syntax_only":
        return True
    allowed = set(extraction.get("allowed_to_skip") or [])
    return category in allowed


def _is_skippable_nonunitary(line: str, extraction: dict[str, Any] | None = None) -> bool:
    """Return True when extraction policy permits skipping this non-unitary line."""
    category = _line_skip_category(line)
    if category is None:
        return False
    if category in {"declaration", "structural"}:
        return True
    return _extraction_allows_skip(extraction, category)


def _cell(re: Fraction | int = 0, im: Fraction | int = 0) -> Cell:
    return (Fraction(re), Fraction(im))


def _eye(n: int) -> ComplexMatrix:
    return [[_cell(1 if i == j else 0) for j in range(n)] for i in range(n)]


def _phase_gate(name: str) -> ComplexMatrix:
    g = name.lower()
    if g == "s":
        return [[_cell(1), _cell()], [_cell(), _cell(im=1)]]
    if g == "sdg":
        return [[_cell(1), _cell()], [_cell(), _cell(im=-1)]]
    if g == "t":
        c = _SQRT2_HALF
        return [[_cell(1), _cell()], [_cell(), _cell(c, c)]]
    if g == "tdg":
        c = _SQRT2_HALF
        return [[_cell(1), _cell()], [_cell(), _cell(c, -c)]]
    raise ValueError(f"unsupported phase gate: {name}")


def _single_qubit_gate(name: str) -> ComplexMatrix:
    g = name.lower()
    if g == "h":
        return [[_cell(1), _cell(1)], [_cell(1), _cell(-1)]]
    if g == "x":
        return [[_cell(), _cell(1)], [_cell(1), _cell()]]
    if g == "y":
        return [[_cell(), _cell(im=-1)], [_cell(im=1), _cell()]]
    if g == "z":
        return [[_cell(1), _cell()], [_cell(), _cell(-1)]]
    if g in {"s", "t", "sdg", "tdg"}:
        return _phase_gate(g)
    raise ValueError(f"unsupported single-qubit gate: {name}")


def _rx_matrix(theta: float) -> ComplexMatrix:
    half = theta / 2.0
    c = Fraction(math.cos(half)).limit_denominator(10**12)
    s = Fraction(math.sin(half)).limit_denominator(10**12)
    return [[_cell(c), _cell(im=-s)], [_cell(im=-s), _cell(c)]]


def _ry_matrix(theta: float) -> ComplexMatrix:
    half = theta / 2.0
    c = Fraction(math.cos(half)).limit_denominator(10**12)
    s = Fraction(math.sin(half)).limit_denominator(10**12)
    return [[_cell(c), _cell(-s)], [_cell(s), _cell(c)]]


def _rz_matrix(theta: float) -> ComplexMatrix:
    half = theta / 2.0
    re_neg = Fraction(math.cos(-half)).limit_denominator(10**12)
    im_neg = Fraction(math.sin(-half)).limit_denominator(10**12)
    re_pos = Fraction(math.cos(half)).limit_denominator(10**12)
    im_pos = Fraction(math.sin(half)).limit_denominator(10**12)
    return [[_cell(re_neg, im_neg), _cell()], [_cell(), _cell(re_pos, im_pos)]]


def _u_matrix(theta: float, phi: float, lam: float) -> ComplexMatrix:
    half = theta / 2.0
    c = Fraction(math.cos(half)).limit_denominator(10**12)
    s = Fraction(math.sin(half)).limit_denominator(10**12)

    def cis(angle: float) -> Cell:
        return (
            Fraction(math.cos(angle)).limit_denominator(10**12),
            Fraction(math.sin(angle)).limit_denominator(10**12),
        )

    e_phi = cis(phi)
    e_lam = cis(lam)
    e_phi_lam = cis(phi + lam)

    def mul_cell(a: Cell, b: Cell) -> Cell:
        ar, ai = a
        br, bi = b
        return (ar * br - ai * bi, ar * bi + ai * br)

    neg_e_lam_s = mul_cell((-e_lam[0], -e_lam[1]), (s, 0))
    e_phi_s = mul_cell(e_phi, (s, 0))
    e_phi_lam_c = mul_cell(e_phi_lam, (c, 0))
    return [[_cell(c), neg_e_lam_s], [e_phi_s, e_phi_lam_c]]


def _parse_angle_list(text: str) -> list[float]:
    parts = [p.strip() for p in text.split(",") if p.strip()]
    return [_parse_angle(p) for p in parts]


def _sum_cells(cells: list[Cell]) -> Cell:
    re = sum(c[0] for c in cells)
    im = sum(c[1] for c in cells)
    return (re, im)


def _mat_mul(a: ComplexMatrix, b: ComplexMatrix) -> ComplexMatrix:
    n = len(a)

    def mul_cell(x: Cell, y: Cell) -> Cell:
        xr, xi = x
        yr, yi = y
        return (xr * yr - xi * yi, xr * yi + xi * yr)

    return [
        [
            _sum_cells([mul_cell(a[i][k], b[k][j]) for k in range(n)])
            for j in range(n)
        ]
        for i in range(n)
    ]


def _kron(a: ComplexMatrix, b: ComplexMatrix) -> ComplexMatrix:
    ra, ca = len(a), len(a[0])
    rb, cb = len(b), len(b[0])

    def mul_cell(x: Cell, y: Cell) -> Cell:
        xr, xi = x
        yr, yi = y
        return (xr * yr - xi * yi, xr * yi + xi * yr)

    return [
        [mul_cell(a[i // rb][j // cb], b[i % rb][j % cb]) for j in range(ca * cb)]
        for i in range(ra * rb)
    ]


def _apply_single(n_qubits: int, gate: str, qubit: int) -> ComplexMatrix:
    op = _single_qubit_gate(gate)
    mats: list[ComplexMatrix] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _apply_rx(n_qubits: int, theta: float, qubit: int) -> ComplexMatrix:
    op = _rx_matrix(theta)
    mats: list[ComplexMatrix] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _apply_ry(n_qubits: int, theta: float, qubit: int) -> ComplexMatrix:
    op = _ry_matrix(theta)
    mats: list[ComplexMatrix] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _apply_rz(n_qubits: int, theta: float, qubit: int) -> ComplexMatrix:
    op = _rz_matrix(theta)
    mats: list[ComplexMatrix] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _apply_u(n_qubits: int, theta: float, phi: float, lam: float, qubit: int) -> ComplexMatrix:
    op = _u_matrix(theta, phi, lam)
    mats: list[ComplexMatrix] = []
    for q in range(n_qubits):
        mats.append(op if q == qubit else _eye(2))
    result = mats[0]
    for m in mats[1:]:
        result = _kron(result, m)
    return result


def _cnot(n_qubits: int, control: int, target: int) -> ComplexMatrix:
    dim = 1 << n_qubits
    result = _eye(dim)
    for row in range(dim):
        bits = [(row >> q) & 1 for q in range(n_qubits)]
        col_bits = list(bits)
        if bits[control] == 1:
            col_bits[target] ^= 1
        col = sum(col_bits[q] << q for q in range(n_qubits))
        for c in range(dim):
            result[row][c] = _cell(1 if c == col else 0)
    return result


def _ccx(n_qubits: int, c1: int, c2: int, target: int) -> ComplexMatrix:
    dim = 1 << n_qubits
    result = _eye(dim)
    for row in range(dim):
        bits = [(row >> q) & 1 for q in range(n_qubits)]
        col_bits = list(bits)
        if bits[c1] == 1 and bits[c2] == 1:
            col_bits[target] ^= 1
        col = sum(col_bits[q] << q for q in range(n_qubits))
        for c in range(dim):
            result[row][c] = _cell(1 if c == col else 0)
    return result


def _cp(n_qubits: int, control: int, target: int, theta: float) -> ComplexMatrix:
    """Controlled phase: exp(i*theta) on |11> of (control, target) when both are 1."""
    dim = 1 << n_qubits
    result = _eye(dim)
    idx = (1 << control) | (1 << target)
    re = Fraction(math.cos(theta)).limit_denominator(10**12)
    im = Fraction(math.sin(theta)).limit_denominator(10**12)
    result[idx][idx] = _cell(re, im)
    return result


def _cz(n_qubits: int, control: int, target: int) -> ComplexMatrix:
    dim = 1 << n_qubits
    result = _eye(dim)
    idx = (1 << control) | (1 << target)
    result[idx][idx] = _cell(-1)
    return result


def _swap(n_qubits: int, a: int, b: int) -> ComplexMatrix:
    dim = 1 << n_qubits
    result = _eye(dim)
    for row in range(dim):
        bits = [(row >> q) & 1 for q in range(n_qubits)]
        col_bits = list(bits)
        if bits[a] != bits[b]:
            col_bits[a], col_bits[b] = col_bits[b], col_bits[a]
        col = sum(col_bits[q] << q for q in range(n_qubits))
        for c in range(dim):
            result[row][c] = _cell(1 if c == col else 0)
    return result


def _parse_angle(text: str) -> float:
    """Single angle parser shared by matrix extraction and denotation bridge."""
    s = text.strip().lower().replace(" ", "")
    if s in {"pi/2", "(pi/2)"}:
        return math.pi / 2.0
    if s in {"pi/4", "(pi/4)"}:
        return math.pi / 4.0
    if s in {"pi", "(pi)"}:
        return math.pi
    if not _ANGLE_LITERAL_RE.match(s):
        raise ValueError(f"unsupported angle literal: {text!r}")
    return float(s)


def _parse_qubit_index(token: str, n_qubits: int) -> int:
    m = re.search(r"\[(\d+)\]", token)
    if m:
        idx = int(m.group(1))
    else:
        m2 = re.search(r"q(\d+)", token.lower())
        if not m2:
            raise ValueError(f"cannot parse qubit index from {token}")
        idx = int(m2.group(1))
    if idx < 0 or idx >= n_qubits:
        raise ValueError(f"qubit index {idx} out of range for {n_qubits} qubits")
    return idx


def _parse_qubit_args(rest: str, n_qubits: int) -> list[int]:
    args: list[int] = []
    for token in rest.replace(",", " ").split():
        if "q" in token.lower():
            args.append(_parse_qubit_index(token, n_qubits))
    return args


def _register_size(text: str) -> int:
    m = re.search(r"qubit\s*\[\s*(\d+)\s*\]", text)
    if not m:
        raise ValueError("expected qubit[n] register declaration")
    return int(m.group(1))


def cell_to_json(cell: Cell) -> list[list[int]]:
    return [[cell[0].numerator, cell[0].denominator], [cell[1].numerator, cell[1].denominator]]


def cell_from_json(data: list[Any]) -> Cell:
    if len(data) == 2 and isinstance(data[0], int):
        return (Fraction(data[0], data[1]), Fraction(0))
    if len(data) == 2 and isinstance(data[0], list):
        return (Fraction(data[0][0], data[0][1]), Fraction(data[1][0], data[1][1]))
    raise ValueError(f"unsupported matrix cell format: {data!r}")


def matrix_from_json_rows(rows: list[list[Any]]) -> ComplexMatrix:
    return [[cell_from_json(cell) for cell in row] for row in rows]


def cells_close(a: Cell, b: Cell, tol: Fraction = _COMPLEX_TOLERANCE) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def matrices_equal(
    a: ComplexMatrix,
    b: ComplexMatrix,
    *,
    tol: Fraction = _COMPLEX_TOLERANCE,
) -> bool:
    if len(a) != len(b) or any(len(r1) != len(r2) for r1, r2 in zip(a, b)):
        return False
    return all(cells_close(x, y, tol=tol) for row_a, row_b in zip(a, b) for x, y in zip(row_a, row_b))


def extract_matrix(
    qasm_path: Path,
    extraction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = qasm_path.read_text(encoding="utf-8")
    n = _register_size(text)
    unitary = _eye(1 << n)
    gates_applied: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.lower().startswith("openqasm"):
            continue
        if line.lower().startswith("include"):
            continue

        rx = _RX_LINE.match(line)
        if rx:
            angle = _parse_angle(rx.group(1))
            q = _parse_qubit_index(rx.group(2), n)
            op = _apply_rx(n, angle, q)
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        ry = _RY_LINE.match(line)
        if ry:
            angle = _parse_angle(ry.group(1))
            q = _parse_qubit_index(ry.group(2), n)
            op = _apply_ry(n, angle, q)
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        rz = _RZ_LINE.match(line)
        if rz:
            angle = _parse_angle(rz.group(1))
            q = _parse_qubit_index(rz.group(2), n)
            op = _apply_rz(n, angle, q)
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        u = _U_LINE.match(line)
        if u:
            angles = _parse_angle_list(u.group(1))
            if len(angles) != 3:
                raise ValueError(f"U expects three angles: {line}")
            q = _parse_qubit_index(u.group(2), n)
            op = _apply_u(n, angles[0], angles[1], angles[2], q)
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        cp = _CP_LINE.match(line)
        if cp:
            angle = _parse_angle(cp.group(1))
            args = _parse_qubit_args(cp.group(2), n)
            if len(args) != 2:
                raise ValueError(f"CP expects two qubit arguments: {line}")
            op = _cp(n, args[0], args[1], angle)
            unitary = _mat_mul(op, unitary)
            gates_applied.append(line)
            continue

        m = _GATE_LINE.match(line)
        if not m:
            category = _line_skip_category(line)
            if category and _is_skippable_nonunitary(line, extraction):
                continue
            if category:
                raise UnsupportedQasmError(
                    f"QASM line {line!r} requires qasm_extraction.mode=unitary_fragment "
                    f"with allowed_to_skip including {category!r} (fail-closed default)"
                )
            raise UnsupportedQasmError(
                f"unsupported QASM line for matrix extraction (fail-closed): {line!r}"
            )
        gate = m.group(1).lower()
        args = _parse_qubit_args(m.group(2), n)
        if gate in {"cx", "cnot"}:
            if len(args) != 2:
                raise ValueError(f"CX expects two arguments: {line}")
            op = _cnot(n, args[0], args[1])
        elif gate == "ccx":
            if len(args) != 3:
                raise ValueError(f"CCX expects three arguments: {line}")
            op = _ccx(n, args[0], args[1], args[2])
        elif gate == "swap":
            if len(args) != 2:
                raise ValueError(f"SWAP expects two arguments: {line}")
            op = _swap(n, args[0], args[1])
        elif gate == "cz":
            if len(args) != 2:
                raise ValueError(f"CZ expects two arguments: {line}")
            op = _cz(n, args[0], args[1])
        else:
            if len(args) != 1:
                raise ValueError(f"single-qubit gate expects one argument: {line}")
            op = _apply_single(n, gate, args[0])
        unitary = _mat_mul(op, unitary)
        gates_applied.append(line)

    gate_trace: list[dict[str, Any]] = []
    for line in gates_applied:
        stripped = line.strip().rstrip(";")
        parts = stripped.split()
        gate = parts[0].lower()
        if gate.startswith("rx"):
            args = [_parse_qubit_index(parts[-1], n)]
        else:
            args = _parse_qubit_args(" ".join(parts[1:]), n)
        gate_trace.append({"gate": gate, "args": args})

    return {
        "source": str(qasm_path),
        "n_qubits": n,
        "gate_model": "openqasm3_complex_unitary",
        "normalization": {
            "hadamard": "unnormalized_int_model",
            "qasm_factor": "1/sqrt(2) per gate",
            "phase_gates": "complex_diagonal",
        },
        "gates_applied": gates_applied,
        "gate_trace": gate_trace,
        "matrix": [[cell_to_json(unitary[i][j]) for j in range(len(unitary))] for i in range(len(unitary))],
    }


def write_matrix(qasm_path: Path, out_path: Path) -> dict[str, Any]:
    data = extract_matrix(qasm_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data
