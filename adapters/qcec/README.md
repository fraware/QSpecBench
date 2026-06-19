# qcec adapter

Checks QCEC equivalence result artifacts for declared QASM circuit pairs.

## Trust level

`externally_trusted` — relies on QCEC tool output format validation.

## Usage

```bash
python adapters/qcec/parse_result.py source.qasm target.qasm
```

## Limitations

- Validates artifact structure and declared equivalence metadata
- Does not replace kernel-checked semantic bridges for reference benchmarks
