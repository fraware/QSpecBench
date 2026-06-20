# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Teleportation`)

## Score: 4

The kernel-checked anchor (`teleportation_unitary_fragment_checked`) matches the declared unitary fragment before measurement on the fixed wire ordering. Transfer for arbitrary `|ψ⟩`, Bell measurement outcomes, and Pauli correction remain outside the checked scope and are documented in the trust boundary.

## Reviewer role

QSpecBench seed reviewer

## Assumptions

- source claim describes full teleportation protocol
- kernel anchor covers Bell prep plus Alice entangling gates only
- AI draft is untrusted placeholder text
- measurement and classical feed-forward remain outside checked scope

## Rubric checklist

- [x] Source claim identified correctly
- [x] Transfer relation formalized for documented unitary fragment
- [x] Pauli correction frame explicit in trust boundary
- [x] Measurement semantics documented as unchecked
- [ ] Library-compatible full protocol statement
