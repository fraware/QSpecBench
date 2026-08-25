# AI formalization dual-review status

## Historical (Phase C3 – Wave 2; superseded by v1 demotion)

As of v0.2.x, four `ai_formalization` benchmarks carried `reference_claim` with a frozen
AI gold *target* and dual hash-bound review YAML. Those maturity labels were **demoted for
v1** to `experimental_closed` (machine closure only). Retained review files are
`unauthenticated_legacy_review` aliases — not authentic independent review and not
maturity-gold. See [docs/promotion_freeze.md](../../../docs/promotion_freeze.md).

| Benchmark | Frozen AI gold target | Formal review | Domain review |
|-----------|--------------------|----------------|----------------|
| `formalize_bit_flip_code_corrects_one_x` | `QSpecBench.QEC.BitFlip.bit_flip_lookup_decoder_correct` | `reviews/formal_review.json` (`rkothari-formal`) | `reviews/domain_review.json` (`mlewis-quant-sem`) |
| `formalize_small_hamiltonian_hermiticity_statement` | `small_fermionic_hamiltonian_is_hermitian` | `reviews/formal_review.json` | `reviews/domain_review.json` |
| `formalize_stabilizer_commutation_statement` | `steane_stabilizers_commute` (5 adjacent Z-chain pairs) | `reviews/formal_review.json` | `reviews/domain_review.json` |
| `extract_teleportation_correctness_statement` | `teleport_measure_correct_ket0` / `teleport_measure_correct_ket1` | `reviews/formal_review.json` | `reviews/domain_review.json` |

Each package still documents:

1. Frozen `ai_formalization_status.gold_target` (source claim, accepted formal statement,
   rejected nearby, assumptions, empty disagreement record, faithfulness >= 4,
   `kernel_status: checked_faithful`).
2. Dual hash-bound review YAML under distinct named *alias* identities (not v1 gold).
3. Author / reviewers / merger separation (`fraware` never occupies a review seat).

Reviews attest the frozen AI gold package only. AI draft text remains untrusted
(`full_faithfulness_of_ai_draft_text_to_source_phr` stays unproved on every package).
General-state teleportation beyond the computational basis, and general-code
stabilizer commutation beyond the declared adjacent-pair set, also stay explicitly
unchecked — see each benchmark's `spec.yaml` `not_checked_under`.

## Remaining scaffolds

`formalize_no_cloning_statement` (`reference_scaffold`), `formalize_qec_distance_claim_statement`
(`usable`), and `formalize_teleportation_spec_statement` (`usable`) stay below machine-closure
and any future gold promotion until each has its own frozen AI gold target and authentic
independent reviews (gold/`reference_claim` frozen for v1). Do not copy approval artifacts
from a demoted package onto an unreviewed one. See [TRACK.md](../TRACK.md) for the live
maturity table.
