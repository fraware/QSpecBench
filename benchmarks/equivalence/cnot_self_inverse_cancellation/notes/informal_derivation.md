# Informal derivation: CNOT self-inverse

## Claim

Two consecutive CNOT gates on the same control–target pair implement the identity on the declared two-qubit register.

## Argument

Let `CX` denote CNOT with control qubit 0 and target qubit 1 in the computational basis. The action on basis kets is:

- `CX |00⟩ = |00⟩`, `CX |01⟩ = |01⟩`
- `CX |10⟩ = |11⟩`, `CX |11⟩ = |10⟩`

Applying `CX` twice maps each basis state back to itself, so `CX · CX = I` on `{ |00⟩, |01⟩, |10⟩, |11⟩ }`. By linearity, the equality holds on all two-qubit states.

This note scopes the claim to the fixed OpenQASM instance in `artifacts/source.qasm` and `artifacts/target.qasm`. Kernel-checked alignment with Lean is recorded separately via `bridge_verify` evidence.
