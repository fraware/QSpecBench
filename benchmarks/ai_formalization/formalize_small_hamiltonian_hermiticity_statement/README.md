# Formalize Small Hamiltonian Hermiticity Statement

## Claim

The informal source claim that a small Pauli-decomposed Hamiltonian with real coefficients represents a Hermitian operator is faithfully formalized by the checked small-fermionic-Hamiltonian Hermiticity theorem under the frozen gold target (declared 2-qubit Pauli-term artifact).

## Why this matters

AI formalization track requires an explicit untrusted AI draft, a frozen gold target, semantic rubric score, and dual independent reviews before `reference_claim`.

## Objects

- `artifacts/source.txt` — informal source claim
- `artifacts/draft.lean` — untrusted AI draft
- `notes/semantic_rubric.md` — faithfulness rubric (score 4)
- `evidence/kernel_checked_draft.lean` — `#check` of accepted library theorem

## Specification

Relational faithfulness claim; gold package adjudicates the accepted formal statement.

## Evidence

- Lean kernel anchor for `small_fermionic_hamiltonian_is_hermitian`
- Human semantic rubric (score >= 4)
- Dual hash-bound reviews under `reviews/`

## Trust boundary

Explicit in `spec.yaml` trust_boundary. AI draft text remains untrusted; general-size or complex-coefficient Hamiltonians are not claimed.

## Status

Current maturity: **reference_claim**.

## Known gaps

- Full faithfulness of AI draft wording to source phrasing remains unproved
- General-size Hamiltonian Hermiticity beyond the declared 2-qubit instance remains out of scope for this AI gold package

## References

- Sibling Hamiltonian claim: `small_fermionic_hamiltonian_is_hermitian`

## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap.
