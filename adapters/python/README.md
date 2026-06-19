# python adapter

Runs heuristic Python simulation scripts for Hamiltonian and QEC sanity checks.

## Trust level

`heuristic` — numeric scripts are not kernel-checked proofs.

## Usage

```bash
python adapters/python/parse_result.py path/to/check_script.py
```

## Limitations

- Does not verify formal correctness claims
- Suitable for small-instance numeric smoke tests only
