# Qiskit Optimize1qGates provenance adapter

Stable adapter ID: `qspecbench.qiskit.optimize_1q_gates.v1`.

This adapter checks **compiler provenance** for a committed Optimize1qGates
transformation. It loads `compiler_provenance.json`, resolves claim-relative
source/target OpenQASM paths against the claim root, verifies the committed
SHA-256 digests, and (when Qiskit is installed) optionally regenerates the
target to confirm it still matches.

A successful result records compiler identity, Qiskit version, regeneration
status, and the target digest. Semantic equivalence of source vs target must be
discharged independently (Lean denotation and/or QCEC).
