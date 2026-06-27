# QEC track

## Purpose

QEC code, syndrome extraction, decoding, correction, and distance claims.

## Accepted artifacts

Stabilizer code JSON, syndrome/correction tables, circuits.

## Stabilizer JSON format

See `benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/artifacts/code.json`.

## QEC status fields

Optional `qec_status` sub-block: code_definition, stabilizer_commutation, distance_claim, syndrome_extraction, decoder_claim, correction_claim, repeated_round_claim.

## Rules

Separate code definition, syndrome extraction, decoder, correction, and physical assumptions. State whether decoder is proved, assumed, simulated, or out of scope.

A QEC **correction** claim (e.g. "corrects any single X error") is only `reference_claim` when there is
**checked correction evidence** — not an assumed lookup table. Stabilizer-commutation evidence alone
supports at most `reference_scaffold` / `reference_artifact`, with the correction obligation listed in
`proved_scope.unproved_obligations` and `headline_claim_status: partially_checked`.

## Distance claims

Declared distance constants are metadata, not proofs. Distinguish the **bit-flip distance** (X-only)
from the **quantum distance** using explicit `parameters.bit_flip_distance` and
`parameters.quantum_distance` fields where relevant. For example, the three-qubit bit-flip code has
`bit_flip_distance: 3` but `quantum_distance: 1` (no protection against Z errors), so a bare `d: 3`
must not be read as a full quantum distance.

## Syndrome table convention

Syndrome bits are listed in stabilizer order. For the bit-flip code with stabilizers `S0 = Z0 Z1`
(`ZZI`) and `S1 = Z1 Z2` (`IZZ`), a single `X` error on qubit `i` flips syndrome bit `sj` iff `Sj`
carries a `Z` on qubit `i`, giving `X0 -> 10`, `X1 -> 11`, `X2 -> 01` (syndrome written `s0 s1`).
Artifacts declare this convention explicitly.

## Limitations

Many seed benchmarks assume decoder correctness explicitly.
