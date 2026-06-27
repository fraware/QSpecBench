# Claim diff: circuit_identity_after_layout

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
Renaming qubit registers preserves circuit unitary under declared layout map.

## Declared headline (claim_scope)
Renaming qubit registers preserves circuit unitary under declared layout map.

## Required obligations
- lean_kernel_proof
- semantic_bridge
- layout_equivalence

## Checked obligations
- [x] lean_kernel_proof
- [x] semantic_bridge
- [x] layout_equivalence

## Unproved / open obligations
- [ ] register_renaming_semantics_beyond_isomorphic_ma

## Gap
- Headline not marked checked despite obligation coverage; review maturity label.
