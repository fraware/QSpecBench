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
| formalize_small_hamiltonian_hermiticity_statement | experimental_closed | Frozen AI gold target (`small_fermionic_hamiltonian_is_hermitian`) + retained reviews; not maturity-gold |
| formalize_stabilizer_commutation_statement | experimental_closed | Frozen AI gold target (`steane_stabilizers_commute`, 5 adjacent Z-chain pairs) + retained reviews; not maturity-gold |
| formalize_bit_flip_code_corrects_one_x | experimental_closed | QEC code formalization; former `reference_claim` demoted for v1 |
| extract_teleportation_correctness_statement | experimental_closed | Frozen AI gold target (`teleport_measure_correct_ket0`/`ket1`, computational basis) + retained reviews; not maturity-gold |
| formalize_qec_distance_claim_statement | usable | Distance claim draft |
| formalize_teleportation_spec_statement | usable | Teleportation spec draft |

## Semantic rubric (0–5)

See `docs/ai_formalization_track.md`. Reference maturity requires score >= 4.

## Known limitations

Syntactic validity and kernel checking do not imply semantic faithfulness to source text. AI drafts remain untrusted; kernel anchors import library theorems only.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md) for the AI track stack
(kernel anchor + rubric score >= 4 + named reviewer). Gold/`reference_claim` promotion is
frozen for v1 (live inventory 0). Four benchmarks are **`experimental_closed`** with a frozen
AI gold *target* (accepted formal statement), kernel-checked library-theorem anchor, and
retained review YAML labeled `unauthenticated_legacy_review` — not authentic independent
review and not maturity-gold: `formalize_bit_flip_code_corrects_one_x`,
`formalize_small_hamiltonian_hermiticity_statement`,
`formalize_stabilizer_commutation_statement`, and
`extract_teleportation_correctness_statement` (kernel anchors `teleport_measure_correct_ket0` /
`teleport_measure_correct_ket1`, computational-basis inputs over all four Alice measurement
outcomes; general-state transfer for an arbitrary superposition remains outside checked scope
per trust boundary and is covered by the sibling
`teleportation_preserves_state_up_to_pauli_correction` benchmark).
