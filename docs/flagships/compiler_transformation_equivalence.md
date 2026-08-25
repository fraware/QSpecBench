# Flagship specification: real compiler transformation equivalence

Status: **machine-closed experimental package** (`experimental_closed`). Not independently reviewed. Not a gold/reference claim.

The completed instance is [`qiskit_optimize_1q_gates_hxx_identity`](../benchmarks/equivalence/qiskit_optimize_1q_gates_hxx_identity/): pinned OpenQASM `H;X;X` source, target emitted by `qiskit.transpiler.passes.Optimize1qGates` (hash-bound provenance), Lean denotation equality, QCEC supporting.

Internal peephole `qspecbench.reference_qasm_peephole.v1` remains infrastructure, not this flagship.

## Proposition (this instance)

Under the QSpecBench OpenQASM fragment denotation, the committed source and the Optimize1qGates target have identical denotations. This is not a general Qiskit correctness theorem.

## Closed obligations

1. `source_artifact_parse`
2. `target_artifact_parse`
3. `source_target_equivalence` (Lean kernel + QCEC supporting)
4. `compiler_provenance` (named public pass, pinned hashes; regeneration when Qiskit is installed)

## Residual

Independent review is absent. Gold/reference promotion is blocked. Unsupported OpenQASM constructs, wire permutation, and other compiler versions are outside the proposition.
