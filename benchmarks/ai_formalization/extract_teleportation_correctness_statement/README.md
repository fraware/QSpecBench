# Extract Teleportation Correctness Statement

## Claim

Evaluate AI-assisted formalization faithfulness for extracting a teleportation correctness statement from source text.

## Why this matters

Mission-corpus AI formalization requires explicit untrusted labels, semantic rubric scoring, and honest kernel-anchor scope. This benchmark tests extraction (not full protocol proof).

## Objects

- `artifacts/source.txt` — informal teleportation correctness claim
- `artifacts/draft.lean` — untrusted AI draft placeholder
- `notes/semantic_rubric.md` — semantic faithfulness rubric (score 0–5)

## Specification

Relational faithfulness claim; rubric score documents how well the kernel-checked anchor captures the source.

## Evidence

- `evidence/kernel_checked_draft.lean` — imports `QSpecBench.teleportation_preserves_state` (Bell-prep scaffold only)
- `evidence/rubric_result.json` — parsed rubric (score 2 at current maturity)
- `notes/semantic_rubric.md` — human review rubric (partial; score < 4)

## Trust boundary

The Lean anchor proves Bell-pair preparation is nontrivial; it does **not** prove state transfer, measurement, or Pauli correction from the source text. AI draft remains untrusted.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel anchor scope mismatch with full teleportation correctness claim
- Rubric score 2: partial capture; measurement and correction not encoded
- Reference promotion blocked until anchor and rubric align honestly

## References

- [`teleportation_preserves_state_up_to_pauli_correction`](../../algorithms/teleportation_preserves_state_up_to_pauli_correction/) — full protocol benchmark
