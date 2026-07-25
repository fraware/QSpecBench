"""Docs: elaborator pin freshness.

The committed pin `schema/theorem_elaborator_types.json` must come from a real
Lean elaborator export (`lake env lean ExportTheoremTypesCheck.lean` or
`lake exe exportTheoremTypes`), not from regex theorem-source bootstrapping.

Local refresh (after Mathlib/lake available):

```text
cd lean && lake build
cd .. && python scripts/refresh_elaborator_pin.py
```

CI path (authoritative):

1. `validate` / `release` jobs run `lake build` then
   `uv run python scripts/export_theorem_types.py`.
2. Release archives the export under `artifacts/release/theorem-elaborator-types.json`.
3. Maintainers refresh the committed pin with `scripts/refresh_elaborator_pin.py`
   when CI export hashes diverge from `schema/theorem_elaborator_types.json`.

Fail-closed rule: artifact-bound promotion requires elaborator export availability;
regex-only fallback must not promote ABRC benchmarks.
"""
