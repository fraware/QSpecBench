# AI Formalization Track

## Purpose

Evaluate AI-assisted extraction and formalization of quantum claims with explicit untrusted labels.

## Required per benchmark

Source text, target formal system, expected statement shape, rubric, trust boundary.

## Accepted evidence

`ai_draft` (untrusted), human semantic review, kernel-checked anchor linking to library theorems.

## Reference exemplars

- `formalize_no_cloning_statement` (reference)
- `formalize_small_hamiltonian_hermiticity_statement` (reference)
- `formalize_stabilizer_commutation_statement` (reference)
- `formalize_bit_flip_code_corrects_one_x` (reference)

## Semantic rubric (0–5)

See `docs/ai_formalization_track.md`. Reference maturity requires score >= 4.

## Known limitations

Syntactic validity and kernel checking do not imply semantic faithfulness to source text. AI drafts remain untrusted; kernel anchors import library theorems only.
