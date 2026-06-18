# Lean 4 proof adapter

Runs `lake build` on the repository `lean/` project to kernel-check Lean evidence files.

- **Trust level:** `checked` (Lean 4 kernel)
- **Does not** upgrade trust for files containing `sorry`
- Requires `elan` + `lake` on PATH (installed in CI)

Evidence `.lean` files under benchmarks should `import` the corresponding `lean/QSpecBench/` module.
