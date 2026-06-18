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

## Limitations

Many seed benchmarks assume decoder correctness explicitly.
