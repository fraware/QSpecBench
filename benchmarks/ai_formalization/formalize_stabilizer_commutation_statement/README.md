# Formalize Stabilizer Commutation Statement

## Claim

The informal source claim that all stabilizer generators of a stabilizer code pairwise commute under Pauli multiplication is faithfully formalized — for the declared six-generator Steane Z-chain scaffold's five adjacent generator pairs — by the checked Steane stabilizer-commutation theorem under the frozen gold target; full all-pairs commutation for a general stabilizer code remains outside this gold target.

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

- Lean kernel anchor for `steane_stabilizers_commute`
- Human semantic rubric (score >= 4)
- Dual hash-bound reviews under `reviews/`

## Trust boundary

Explicit in `spec.yaml` trust_boundary. AI draft text remains untrusted; all-pairs commutation for a general stabilizer code (beyond the 5 checked adjacent pairs) is not claimed.

## Status

Current maturity: **reference_claim**.

## Known gaps

- Full faithfulness of AI draft wording to source phrasing remains unproved
- All-pairs stabilizer commutation for a general stabilizer code, and non-adjacent Steane generator pairs, remain out of scope for this AI gold package

## References

- Sibling QEC claim: `steane_code_stabilizer_commutation`

## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap.
