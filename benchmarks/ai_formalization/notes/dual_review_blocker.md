# AI formalization dual-review status

## Resolved (Phase C3 – Wave 2)

Four `ai_formalization` benchmarks are promoted to `reference_claim`, each with its own
frozen gold target and dual independent hash-bound reviews:

| Benchmark | Frozen gold target | Formal review | Domain review |
|-----------|--------------------|----------------|----------------|
| `formalize_bit_flip_code_corrects_one_x` | `QSpecBench.QEC.BitFlip.bit_flip_lookup_decoder_correct` | `reviews/formal_review.json` (`rkothari-formal`) | `reviews/domain_review.json` (`mlewis-quant-sem`) |
| `formalize_small_hamiltonian_hermiticity_statement` | `small_fermionic_hamiltonian_is_hermitian` | `reviews/formal_review.json` | `reviews/domain_review.json` |
| `formalize_stabilizer_commutation_statement` | `steane_stabilizers_commute` (5 adjacent Z-chain pairs) | `reviews/formal_review.json` | `reviews/domain_review.json` |
| `extract_teleportation_correctness_statement` | `teleport_measure_correct_ket0` / `teleport_measure_correct_ket1` | `reviews/formal_review.json` | `reviews/domain_review.json` |

Each promotion satisfies:

1. Frozen `ai_formalization_status.gold_target` (source claim, accepted formal statement,
   rejected nearby, assumptions, empty disagreement record, faithfulness >= 4,
   `kernel_status: checked_faithful`).
2. Dual independent hash-bound reviews under distinct named reviewer identities.
3. Author / reviewers / merger separation (`fraware` never occupies a review seat).

Reviews attest the frozen gold package only. AI draft text remains untrusted
(`full_faithfulness_of_ai_draft_text_to_source_phr` stays unproved on every promoted
benchmark). General-state teleportation beyond the computational basis, and general-code
stabilizer commutation beyond the declared adjacent-pair set, also stay explicitly
unchecked — see each benchmark's `spec.yaml` `not_checked_under`.

## Remaining scaffolds

`formalize_no_cloning_statement` (`reference_scaffold`), `formalize_qec_distance_claim_statement`
(`usable`), and `formalize_teleportation_spec_statement` (`usable`) stay below `reference_claim`
until each has its own frozen gold target and dual reviews. Do not copy approval artifacts
from a promoted benchmark onto an unreviewed one — every promotion needs an independent
gold freeze and independent review pair. See [TRACK.md](../TRACK.md) for the live maturity
table.
