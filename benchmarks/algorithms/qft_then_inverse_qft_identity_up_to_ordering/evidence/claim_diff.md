# Claim diff: qft_then_inverse_qft_identity_up_to_ordering

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
Applying QFT followed by inverse QFT yields the identity on the declared register up to bit-ordering conventions.

## Declared headline (claim_scope)
Applying QFT followed by inverse QFT yields the identity on the declared register up to bit-ordering conventions.

## Required obligations
- qft_inverse_identity
- semantic_bridge

## Checked obligations
- [x] qft_inverse_identity
- [x] semantic_bridge

## Unproved / open obligations
- [ ] semantic_correctness_of_circuit_vs_claim

## Gap
- Headline not marked checked despite obligation coverage; review maturity label.
