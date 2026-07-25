# Extract Teleportation Correctness Statement

## Claim

The informal source claim that quantum teleportation transfers an unknown qubit state to a remote party up to Pauli corrections is faithfully formalized — for the declared computational-basis inputs zero and one, over all four Alice measurement outcomes — by the checked measure-and-correct recovery theorems under the frozen gold target; general-state transfer for an arbitrary superposition remains outside this gold target.

## Why this matters

AI formalization track requires an explicit untrusted AI draft, a frozen gold target, semantic rubric score, and dual independent reviews before `reference_claim`.

## Objects

- `artifacts/source.txt` — informal teleportation correctness claim
- `artifacts/draft.lean` — untrusted AI draft placeholder
- `notes/semantic_rubric.md` — semantic faithfulness rubric (score 4)
- `evidence/kernel_checked_draft.lean` — `#check` of both accepted library theorems

## Specification

Relational faithfulness claim; gold package adjudicates the accepted formal statement.

## Evidence

- Lean kernel anchors for `teleport_measure_correct_ket0` and `teleport_measure_correct_ket1`
- Human semantic rubric (score >= 4)
- Dual hash-bound reviews under `reviews/`

## Trust boundary

Explicit in `spec.yaml` trust_boundary. AI draft text remains untrusted; general-state transfer for an arbitrary superposition beyond the declared computational-basis inputs is not claimed.

## Status

Current maturity: **reference_claim**.

## Known gaps

- Full faithfulness of AI draft wording to source phrasing remains unproved
- General-state teleportation for an arbitrary superposition remains out of scope for this AI gold package

## References

- [`teleportation_preserves_state_up_to_pauli_correction`](../../algorithms/teleportation_preserves_state_up_to_pauli_correction/) — full-protocol benchmark (arbitrary superposition)

## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap.
