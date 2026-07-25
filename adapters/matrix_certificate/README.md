# matrix_certificate adapter

Independent checker for `matrix_certificate` evidence.

## Trust level

`independently_checkable` -- verifies a declared-matrix certificate JSON file
without importing `qasm_matrix`, `denotate`, or `bridge_codegen`. It never
reuses the same extraction path a benchmark's headline claim depends on, so it
cannot rubber-stamp a bridge bug shared by both sides.

## Usage

```bash
python adapters/matrix_certificate/parse_result.py certificate.json
```

## Certificate shape

Required fields:

- `gate_profile`: free-form label identifying the circuit fragment
- `n_qubits`: integer in 1..8
- `source_matrix` / `target_matrix`: square `2**n_qubits` nested lists of
  complex entries (`[re, im]`, `{"re": ..., "im": ...}`, or real number)
- `relation`: `exact` or `global_phase`

Optional: `tolerance` (defaults to `1e-9`).

## Limits

This adapter is a standalone numerical equality check on matrices supplied in
the certificate; it does not itself extract a matrix from an OpenQASM source
or confirm the certificate's matrices correspond to any particular circuit.
Adapters exist; this is **still not a complete FV standard**. Do not promote a
benchmark to ABRC solely on matrix certificate evidence.
