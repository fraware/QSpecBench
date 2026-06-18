# AI Formalization Track

## Purpose

Evaluate AI-assisted extraction and formalization of quantum claims with explicit untrusted labels.

## Required per benchmark

Source text, target formal system, expected statement shape, rubric, trust boundary.

## Accepted evidence

`ai_draft` (untrusted), human semantic review, kernel check (if available).

## Good first claims

- `formalize_no_cloning_statement` (introductory, usable)
- `extract_teleportation_correctness_statement` (intermediate, seed)

## Semantic rubric (0–5)

See `docs/ai_formalization_track.md`.

## Known limitations

Syntactic validity and kernel checking do not imply semantic faithfulness to source text.
