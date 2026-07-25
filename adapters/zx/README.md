# zx adapter

Independent checker for ``zx_certificate`` evidence.

## Trust level

`independently_checkable` — verifies ``qspecbench.zx_certificate.v1`` normal-form
equality by canonicalizing spider generators. Bare success / verdict strings
without diagrams are rejected.

## Usage

```bash
python adapters/zx/parse_result.py certificate.json
```

## Certificate shape (v1)

Required fields:

- `schema_version`: `qspecbench.zx_certificate.v1`
- `relation`: `normal_form_equality`
- `n_qubits`: integer in 1..16
- `source_normal_form.generators` / `target_normal_form.generators`
  - each generator: `{ "kind": "Z"|"X", "phase_pi_rational": [num, den], "arity": int }`

Optional: `bound_artifact_sha256` must match a secondary path when provided.

## Limits

Adapters exist; this is **still not a complete FV standard**. Do not promote a
benchmark to ABRC solely on ZX certificate evidence.
