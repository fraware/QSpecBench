# Decoder and correction assumptions (bit-flip code)

## Code definition (in scope)

The stabilizer generators in `artifacts/code.json` define the code space. JSON validation checks structure only.

## Syndrome / correction tables (checked)

`artifacts/syndrome_table.json` and `artifacts/correction_table.json` document the **lookup decoder** used in the claim narrative. Tables are aligned with the Lean model in `QSpecBench.QEC.BitFlip` and exercised by the QEC brute-force validator.

## Decoder correctness (lookup-table scope)

**Kernel-checked:** `QSpecBench.QEC.BitFlip.bit_flip_lookup_decoder_correct` proves that for each single-X error on one wire, multiplying the error by the lookup correction yields a stabilizer (residual in the stabilizer group).

This is **not** a general decoder-algorithm proof: syndrome-extraction circuits, measurement errors, and lookup tables beyond the declared three-qubit bit-flip instance remain out of scope.

## Separation of claims

| Sub-claim | Status |
|-----------|--------|
| Code JSON well-formed | checked (qec json validator) |
| Stabilizer commutation | checked (Lean) |
| Lookup-table decoder | checked (Lean + brute force) |
| Correction restores logical state | checked (brute force under declared model) |
| Syndrome extraction circuits | out of scope |
| General decoder algorithm | out of scope |

## Error model

See `artifacts/error_model.json`. Pauli-only, single X, no leakage or measurement errors.
