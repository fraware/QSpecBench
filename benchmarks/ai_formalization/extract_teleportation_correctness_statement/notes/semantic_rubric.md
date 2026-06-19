# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Teleportation`)

## Score: 2

Partial capture of teleportation correctness. The kernel-checked anchor (`teleportation_preserves_state`) only establishes Bell-pair preparation is nontrivial; it does not encode unknown-state transfer, Bell measurement, or Pauli correction from the source.

## Reviewer role

QSpecBench seed reviewer

## Assumptions

- source claim requires transfer up to Pauli corrections
- kernel anchor is Bell-prep scaffold only
- AI draft is untrusted placeholder text
- measurement and classical feed-forward remain outside checked scope

## Rubric checklist

- [x] Source claim identified correctly
- [ ] Transfer relation formalized
- [ ] Pauli correction frame explicit
- [ ] Measurement semantics encoded
- [ ] Library-compatible full protocol statement
