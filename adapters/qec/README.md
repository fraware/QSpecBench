# qec adapter

Validates stabilizer-code JSON artifacts (structure, commutation, parameters).

## Trust level

`externally_trusted` for JSON schema checks; Lean proofs are separate `lean_proof` evidence.

## Usage

```bash
python adapters/qec/parse_result.py artifacts/code.json
```

## Limitations

- Does not prove decoder or correction correctness
