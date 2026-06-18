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

## Correction

Applying \(P^{-1}(c_0,c_1)\) on `q[2]` restores \(|\psi\rangle\) on Bob's wire.

## What is not proved here

- QASM semantics match the relational claim
- Classical feed-forward is modeled correctly
- No formal kernel-checked proof is included
