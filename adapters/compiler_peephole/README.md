# Reference OpenQASM peephole compiler adapter

Stable adapter ID: `qspecbench.compiler.peephole.v1`.

This adapter establishes **transformation provenance**, not semantic equivalence by itself. It runs
the deterministic QSpecBench reference compiler on a source OpenQASM artifact and requires its
emitted bytes to exactly equal the declared target artifact.

The compiler is deliberately narrow and fail-closed. Version 1 accepts an exact OpenQASM 3.0
header, `stdgates.inc`, one `qubit[N] q` register, and `h`/`x` single-qubit gates. Its only
optimization is adjacent `x q[i]; x q[i];` cancellation. Unsupported syntax is an error.

A successful result records compiler ID/version, source/target SHA-256, and the applied rewrite
sequence. It supports only the `compiler_transformation_reproduced` obligation. Circuit semantic
equivalence must be discharged independently (e.g. Lean artifact denotation plus QCEC supporting
evidence).
