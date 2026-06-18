# Equivalence Track

## Purpose

Encode source-target equivalence claims for circuits, compiler passes, and transformations.

## Accepted claim types

Unitary equivalence, phase equivalence, distribution equivalence, approximate equivalence under a metric.

## Accepted artifacts

At minimum two artifacts per claim: `source` and `target` QASM (or formal objects).

## Accepted evidence

QASM parse (syntax only), QCEC results, ZX certificates, independently checkable small-instance certificates.

## Good first claims

- `cnot_self_inverse_cancellation` (introductory, **reference** with checkable certificate)
- `single_qubit_gate_cancellation` (introductory, seed)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| cnot_self_inverse_cancellation | introductory | reference | SAT-style unitary certificate |
| hadamard_conjugates_x_to_z | intermediate | seed | Pauli conjugation |
| source_optimized_qasm_equivalence_small_instance | intermediate | seed | Compiler output pattern |

## Known limitations

QASM parsing does not establish semantic equivalence. Reference benchmark certificate applies only to the declared fixed instance.
