# Flagship specification: three-qubit bit-flip QEC chain

Status: **machine-closed experimental package** (`experimental_closed`). Not independently reviewed. Not a gold/reference claim.

The completed instance is [`three_qubit_bit_flip_code_corrects_one_x`](../benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/). Lean-QEC BB90 remains a separate distance-only interoperability claim and does not close this package.

## Headline layers (distinct edges)

1. `code_definition`
2. `stabilizer_commutation`
3. `syndrome_extraction_circuit_semantics`
4. `lookup_table_decoder` / `decoder_correctness` (decoder evidence; removing it fails only these closures)
5. `correction_restores_logical_state`

Distance is not a required headline obligation. Bounded noise is an accepted declared-universe hypothesis; `error_model_json` is not a discharging edge. Repeated-round FT is supporting, not headline-required.

## Residual

Independent review is absent. Physical realism outside the declared single-X universe remains out of scope.
