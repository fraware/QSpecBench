"""Minimal deterministic OpenQASM reference compiler used by the compiler flagship.

The pass is intentionally narrow and fail-closed. It preserves accepted headers/declarations and
eliminates only adjacent identical X gates on the same qubit (`X·X = I`). It is not presented as a
general OpenQASM optimizer; its purpose is to turn a concrete source→target transformation into a
reproducible artifact with an auditable compiler identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

COMPILER_ID = "qspecbench.reference_qasm_peephole.v1"
COMPILER_VERSION = "1.0.0"

_SINGLE_GATE = re.compile(r"^(?P<gate>[hx])\s+q\[(?P<qubit>[0-9]+)\];$")
_QUBIT_DECL = re.compile(r"^qubit\[(?P<width>[1-9][0-9]*)\]\s+q;$")

GateOp = tuple[str, int]


class ReferenceCompilerError(ValueError):
    """Raised when the source is outside the explicitly supported compiler subset."""


@dataclass(frozen=True)
class CompileResult:
    output: str
    transformations: tuple[str, ...]
    source_sha256: str
    target_sha256: str
    source_ops: tuple[GateOp, ...]
    target_ops: tuple[GateOp, ...]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compile_qasm(source: str) -> CompileResult:
    """Compile the declared one-register H/X subset, cancelling adjacent `x;x` pairs.

    Accepted non-executable lines are exactly:
    - `OPENQASM 3.0;`
    - `include "stdgates.inc";`
    - one `qubit[N] q;` declaration.

    Executable lines are `h q[i];` and `x q[i];`, with indices checked against the declaration.
    Anything else fails closed rather than being copied or silently dropped.
    """
    if not source.endswith("\n"):
        raise ReferenceCompilerError("source must be LF-terminated")
    raw_lines = source.splitlines()
    if len(raw_lines) < 3:
        raise ReferenceCompilerError("source is missing required OpenQASM header/declaration")
    if raw_lines[0] != "OPENQASM 3.0;":
        raise ReferenceCompilerError("only exact OPENQASM 3.0 header is supported")
    if raw_lines[1] != 'include "stdgates.inc";':
        raise ReferenceCompilerError("only exact stdgates.inc include is supported")
    decl = _QUBIT_DECL.fullmatch(raw_lines[2])
    if decl is None:
        raise ReferenceCompilerError("expected exactly one qubit[N] q declaration")
    width = int(decl.group("width"))

    source_ops: list[GateOp] = []
    optimized: list[GateOp] = []
    transformations: list[str] = []
    for line_no, line in enumerate(raw_lines[3:], start=4):
        match = _SINGLE_GATE.fullmatch(line)
        if match is None:
            raise ReferenceCompilerError(
                f"unsupported executable/source line {line_no}: {line!r}"
            )
        gate = match.group("gate")
        qubit = int(match.group("qubit"))
        if qubit >= width:
            raise ReferenceCompilerError(
                f"qubit index {qubit} out of range for declared width {width}"
            )

        op = (gate, qubit)
        source_ops.append(op)
        if gate == "x" and optimized and optimized[-1] == op:
            optimized.pop()
            transformations.append(f"cancel_x_pair:q[{qubit}]")
        else:
            optimized.append(op)

    output_lines = raw_lines[:3] + [f"{gate} q[{qubit}];" for gate, qubit in optimized]
    output = "\n".join(output_lines) + "\n"
    return CompileResult(
        output=output,
        transformations=tuple(transformations),
        source_sha256=_sha256(source),
        target_sha256=_sha256(output),
        source_ops=tuple(source_ops),
        target_ops=tuple(optimized),
    )
