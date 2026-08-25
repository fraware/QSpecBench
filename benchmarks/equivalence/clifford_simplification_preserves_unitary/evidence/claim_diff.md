# Claim diff: clifford_simplification_preserves_unitary

<!-- scope_fingerprint: 94221f2b6c2573aa0d2f3c949388a01ecb372c96bfe5cb1e403485f2cf074c22 -->

**Maturity:** experimental_closed
**Headline status:** checked

## Informal claim (README/spec)
Clifford simplification of the declared H-H-S source trace to the S-only target circuit preserves the unitary exactly under the normalized 1-qubit complex denotation (algebraic H = H/√2; global phase φ = 0).

## Declared headline (claim_scope)
Clifford simplification of the declared H-H-S source trace to the S-only target circuit preserves the unitary exactly under the normalized 1-qubit complex denotation (algebraic H = H/√2; global phase φ = 0).

## Required obligations
- source_artifact_parse
- target_artifact_parse
- source_denotation
- target_denotation
- source_target_equivalence
- global_phase_policy
- wire_order_alignment

## Checked obligations
- [x] source_artifact_parse
- [x] target_artifact_parse
- [x] source_denotation
- [x] target_denotation
- [x] source_target_equivalence
- [x] global_phase_policy
- [x] wire_order_alignment

## Unproved / open obligations

## Gap
- None among declared required obligations.
