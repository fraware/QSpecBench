# Decoder and correction assumptions (bit-flip code)

## Code definition (in scope)

The stabilizer generators in `artifacts/code.json` define the code space. JSON validation checks structure only.

## Syndrome / correction tables (assumed)

`artifacts/syndrome_table.json` and `artifacts/correction_table.json` document the **lookup decoder** used in the claim narrative.

## Decoder correctness (out of proof scope here)

Decoder correctness is **assumed**, not kernel-checked. A formal proof must show the lookup table maps syndromes to corrections that restore the logical state for all single-X errors in the declared model.

## Separation of claims

| Sub-claim | Status |
|-----------|--------|
| Code JSON well-formed | checked (qec json validator) |
| Stabilizer commutation | complete in spec |
| Decoder correctness | assumed |
| Correction restores logical state | draft / not proved |

## Error model

See `artifacts/error_model.json`. Pauli-only, single X, no leakage or measurement errors.
