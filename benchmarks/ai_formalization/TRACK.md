# AI Formalization Track

## Purpose

Evaluate AI-assisted extraction and formalization of quantum claims with explicit untrusted labels.

## Required per benchmark

Source text, target formal system, expected statement shape, rubric, trust boundary.

## Accepted evidence

`ai_draft` (untrusted), human semantic review, kernel-checked anchor linking to library theorems.

## Track maturity (live spec.yaml)

| ID | Maturity | Notes |
|----|----------|-------|
| formalize_no_cloning_statement | reference_scaffold | Rubric + Lean anchor |
| formalize_small_hamiltonian_hermiticity_statement | reference_scaffold | Hermiticity formalization |
| formalize_stabilizer_commutation_statement | reference_scaffold | Stabilizer commutation |
| formalize_bit_flip_code_corrects_one_x | reference_scaffold | QEC code formalization |
| extract_teleportation_correctness_statement | reference_scaffold | Rubric 4 + unitary-fragment anchor |
| formalize_qec_distance_claim_statement | usable | Distance claim draft |
| formalize_teleportation_spec_statement | usable | Teleportation spec draft |

## Semantic rubric (0–5)

See `docs/ai_formalization_track.md`. Reference maturity requires score >= 4.

## Known limitations

Syntactic validity and kernel checking do not imply semantic faithfulness to source text. AI drafts remain untrusted; kernel anchors import library theorems only.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md) for the AI track stack (kernel anchor + rubric score >= 4 + named reviewer). Mission benchmark `extract_teleportation_correctness_statement` is **reference** with kernel anchor `teleportation_unitary_fragment_checked`; full measurement and Pauli correction remain outside checked scope per trust boundary.
