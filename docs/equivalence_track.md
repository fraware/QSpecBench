# Equivalence track

## Purpose

Source-target equivalence for circuits, transformations, and compiler passes.

## Accepted claim types

Unitary equivalence, phase equivalence, distribution equivalence, approximate equivalence.

## Accepted artifacts

Source and target QASM (minimum two artifacts per claim).

## Accepted evidence

QASM parse, QCEC results, ZX certificates.

## Rules

Declare equivalence relation, ancillae, garbage qubits, measurements, parameterized gates.

## Examples

- `cnot_self_inverse_cancellation` — exact unitary equality

## Limitations

QASM parsing is syntax only, not semantic equivalence.
