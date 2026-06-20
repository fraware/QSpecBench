# Informal derivation: quantum teleportation

## Setup

Alice holds unknown pure state \(|\psi\rangle\) on qubit `q[0]`. Qubits `q[1]` and `q[2]` start in Bell state
\((|00\rangle + |11\rangle)/\sqrt{2}\) shared with Bob (`q[2]`).

## Circuit

1. \(H\) on `q[1]`, then \(\mathrm{CX}_{1,2}\) prepares the Bell pair.
2. \(\mathrm{CX}_{0,1}\) and \(H\) on `q[0]` entangle input with Alice's Bell qubit.
3. Measure `q[0]` and `q[1]` into classical bits `c[0]`, `c[1]`.

## Post-measurement state

The joint state of `q[2]` with classical outcomes is related to \(|\psi\rangle\) by a Pauli operator
\(P(c_0,c_1)\in\{I,X,Z,XZ\}\) acting on Bob's qubit.

## Correction table (documented, not kernel-checked)

| c[0] | c[1] | Correction on q[2] |
|------|------|---------------------|
| 0    | 0    | I                   |
| 0    | 1    | X                   |
| 1    | 0    | Z                   |
| 1    | 1    | XZ                  |

Lean documents this table as `teleportCorrectionLabel` in `QSpecBench.Teleportation`.

## Correction

Applying \(P^{-1}(c_0,c_1)\) on `q[2]` restores \(|\psi\rangle\) on Bob's wire (standard textbook argument).

## What is kernel-checked

- Bell-pair preparation scaffold matches OpenQASM3 denotation (`bridge_teleportation_scaffold`).
- Two-qubit Alice entangling fragment (`teleportation_unitary_fragment_checked`) is nontrivial on the declared wire ordering.

## What is not kernel-checked

- Arbitrary-state relational transfer after measurement and Pauli correction.
- QASM classical feed-forward semantics for unexpanded corrections.
- Idealized projective measurement model.
