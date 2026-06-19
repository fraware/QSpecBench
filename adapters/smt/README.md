# smt adapter

Validates SMT-LIB distance certificates with Z3.

## Trust level

`independently_checkable` when Z3 succeeds on the declared certificate.

## Usage

```bash
python adapters/smt/parse_result.py path/to/certificate.smt2
```

## Requirements

- Z3 installed and on PATH (or via system package manager in CI)
