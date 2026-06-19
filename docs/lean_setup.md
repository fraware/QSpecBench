# Lean 4 setup

QSpecBench kernel-checked evidence requires **Lean 4** and **Lake**.

## Linux / CI

CI installs elan non-interactively:

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | bash -s -- -y
cd lean && lake build
```

CI on Ubuntu is the **authoritative** proof build for kernel-checked evidence.

## Windows (recommended: WSL2)

Native Windows Lean builds are supported but often hit SSL or toolchain path issues. **WSL2 is the recommended local path** for proof work:

1. Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) with an Ubuntu distribution.
2. Inside WSL, install elan:

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | bash -s -- -y
source ~/.elan/env
cd /mnt/c/path/to/QSpecBench/lean && lake build
```

3. Run `qspecbench check-evidence` from WSL or from Windows for non-Lean adapters.

### Native Windows (optional)

1. Install elan: https://github.com/leanprover/elan
2. If the installer prompts, choose default toolchain install
3. Build proofs:

```powershell
cd lean
lake build
```

### SSL / certificate errors

If `elan` or `lake` fails with `CRYPT_E_NO_REVOCATION_CHECK`, `SEC_E_CERT_EXPIRED`, or similar:

- **Preferred:** use WSL2 and install elan inside Linux (avoids most Windows certificate store issues).
- Retry on a network without SSL inspection.
- Temporarily adjust Windows Internet Options → Advanced → uncheck “Check for server certificate revocation” (re-enable afterward).
- Set `GIT_SSL_NO_VERIFY=1` only as a last resort for elan bootstrap downloads (not recommended long term).

Local Lean failures do **not** block contribution if `qspecbench validate`, `qspecbench check-evidence` (non-Lean paths), and `pytest` pass. CI remains authoritative for kernel-checked proofs.

## Mathlib (Layer 3)

The `lean/` project depends on **Mathlib** pinned to the repository `lean-toolchain` (Lean 4.14.0). First builds download Mathlib and can take 30–45 minutes without cache.

```bash
cd lean
lake exe cache get   # optional; CI runs this
lake build
```

Library layout:

- `QSpecBench.Legacy.*` — integer matrix proofs (backward-compatible evidence anchors)
- `QSpecBench.Quantum.*` — OpenQASM denotation semantics and Mathlib scaffolds

## Verify local build

```bash
cd lean && lake build
```

Expected: `Build completed successfully` with no `sorry` in proof files under `lean/QSpecBench/`.

## Verify evidence

```bash
qspecbench check-evidence benchmarks/equivalence/cnot_self_inverse_cancellation/
```

Proofs must not contain `sorry` — the Lean adapter rejects them.
