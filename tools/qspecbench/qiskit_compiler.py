"""Pinned public-compiler (Qiskit) transformation used by the compiler flagship.

This is not the internal peephole compiler. Regeneration must match committed target bytes.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

COMPILER_ID = "qiskit.transpiler.passes.Optimize1qGates"
COMPILER_PACKAGE = "qiskit"
# Pin recorded in provenance; regeneration uses whatever installed qiskit reports.
PASS_CONFIG = {
    "pass": "Optimize1qGates",
    "optimization_level": None,
    "seed": 0,
}


class QiskitCompilerError(ValueError):
    pass


@dataclass(frozen=True)
class QiskitCompileResult:
    output: str
    source_sha256: str
    target_sha256: str
    qiskit_version: str
    pass_name: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compile_hxx_with_optimize_1q_gates(source: str) -> QiskitCompileResult:
    """Run Qiskit's Optimize1qGates on a 1-qubit H/X OpenQASM 3 circuit."""
    try:
        import qiskit
        from qiskit import QuantumCircuit, qasm3, transpile
        from qiskit.transpiler.passes import Optimize1qGates
    except ImportError as exc:
        raise QiskitCompilerError("qiskit is not installed") from exc

    if "OPENQASM 3.0" not in source:
        raise QiskitCompilerError("expected OPENQASM 3.0 source")
    circuit = qasm3.loads(source)
    if not isinstance(circuit, QuantumCircuit):
        raise QiskitCompilerError("qasm3.loads did not return a QuantumCircuit")
    # Named public pass, then a trivial transpile to emit QASM. Seed is recorded even
    # though this 1q pass is deterministic.
    optimized = Optimize1qGates()(circuit)
    transpiled = transpile(optimized, optimization_level=0, seed_transpiler=PASS_CONFIG["seed"])
    output = qasm3.dumps(transpiled)
    if not output.endswith("\n"):
        output += "\n"
    return QiskitCompileResult(
        output=output,
        source_sha256=_sha256(source),
        target_sha256=_sha256(output),
        qiskit_version=str(qiskit.__version__),
        pass_name="Optimize1qGates",
    )
