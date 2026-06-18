# Lean 4 setup

QSpecBench kernel-checked evidence requires **Lean 4** and **Lake**.

## Linux / CI

CI installs elan non-interactively:

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | bash -s -- -y
cd lean && lake build
```

## Windows

1. Install elan: https://github.com/leanprover/elan
2. If the installer prompts, choose default toolchain install
3. Build proofs:

```powershell
cd lean
lake build
```

### SSL / certificate errors

If `elan` or `lake` fails with `CRYPT_E_NO_REVOCATION_CHECK` or similar:

- Retry on a network without SSL inspection, or
- Temporarily allow certificate revocation checks in Windows Internet Options, or
- Install Lean via elan on WSL2 and run `lake build` there

CI on Ubuntu is the authoritative proof build; local failures do not block contribution if `qspecbench validate` and `pytest` pass.

## Verify evidence

```bash
qspecbench check-evidence benchmarks/equivalence/cnot_self_inverse_cancellation/
```

Proofs must not contain `sorry` — the Lean adapter rejects them.
