# Claim model

QSpecBench separates four object types that are often conflated in quantum verification discussions.

## Claim

A **claim** is what is being asserted — for example, "teleportation preserves the input state up to Pauli correction." The informal claim appears in the claim card (`README.md`) and in `informal_claim.statement` in `spec.yaml`.

## Machine specification

The **specification** is the machine-readable contract: preconditions, postconditions, invariants, approximation bounds, and resource constraints. It states *what* would count as satisfying the claim.

## Artifact

An **artifact** is the circuit, program, Hamiltonian, QEC code, or formal source file being checked. Artifacts live in `artifacts/` and are listed in `objects`.

## Evidence

**Evidence** is a file or command output that supports (or refutes) the claim. Evidence lives in `evidence/` or `notes/` when declared. Evidence is not automatically a proof.

## Proof

A **proof** is evidence checked by a trusted kernel, certified solver, or explicitly declared checker (e.g., Lean 4 kernel, SAT certificate checker). Only passing checked evidence supports a "proved" reading of the benchmark.

## Assumption

An **assumption** is explicit background not established by evidence in this benchmark — mathematical, physical, tool, artifact, or unverified.

## Trust boundary

The **trust boundary** declares what is checked, what external tools are trusted, what remains untrusted, and which assumptions are not verified.

## Quality ladder

| Maturity | Meaning |
|----------|---------|
| seed | Claim + spec + trust boundary; proof optional |
| usable | Complete card/spec, executable artifact, evidence path, CI |
| reference | Checked evidence, passing CI, no hidden assumptions |
| deprecated | Historical; README explains why |
