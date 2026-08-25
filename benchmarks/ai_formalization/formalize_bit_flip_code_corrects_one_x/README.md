# Formalize Bit Flip Code Corrects One X

## Claim

The informal source claim that the three-qubit bit-flip code detects and corrects a single X error is faithfully formalized by the checked three-qubit bit-flip lookup-table decoder theorem under the frozen gold target (declared single-X Pauli model).

## Why this matters

AI formalization track requires an explicit untrusted AI draft, a frozen AI gold *target*
(accepted formal statement), semantic rubric score, and dual reviews before any future
`reference_claim`. Gold maturity is frozen for v1; this package is `experimental_closed`.

## Objects

- `artifacts/source.txt` — informal source claim
- `artifacts/draft.lean` — untrusted AI draft
- `notes/semantic_rubric.md` — faithfulness rubric (score 4)
- `evidence/kernel_checked_draft.lean` — `#check` of accepted library theorem

## Specification

Relational faithfulness claim; gold package adjudicates the accepted formal statement.

## Evidence

- Lean kernel anchor for `bit_flip_lookup_decoder_correct`
- Human semantic rubric (score >= 4)
- Dual hash-bound reviews under `reviews/`

## Trust boundary

Explicit in `spec.yaml` trust_boundary. AI draft text remains untrusted; syndrome-extraction circuits and general decoders are not claimed.

## Status

Current maturity: **experimental_closed**.

## Known gaps

- Full faithfulness of AI draft wording to source phrasing remains unproved
- Syndrome-extraction circuit semantics remain out of scope for this AI gold package

## References

- Sibling QEC claim: `three_qubit_bit_flip_code_corrects_one_x`

## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap.
