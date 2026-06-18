# Informal derivation: no-cloning theorem

## Claim

No unitary quantum channel can copy an arbitrary unknown pure qubit state to two outputs.

## Proof sketch

Suppose a unitary `U` acts on `|ψ⟩|0⟩` and produces `|ψ⟩|ψ⟩` for every pure qubit state `|ψ⟩`.
Linearity of quantum operations forces the same map on superpositions.
Choosing non-orthogonal states `|ψ⟩` and `|φ⟩` leads to inconsistent requirements on `U`, contradicting unitarity.
Therefore no universal cloner exists in finite-dimensional quantum mechanics.

This note is a standard textbook argument; it is not kernel-checked in Lean.
