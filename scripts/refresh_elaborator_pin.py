"""Refresh elaborator type pin from a real Lean elaborator export.

Writes schema/theorem_elaborator_types.json with authority lean_elaborator_export
only when lake export succeeds. On failure, exits non-zero without rewriting the pin
(so CI must fail closed rather than silently re-bootstrap from regex).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.bridge_codegen import (  # noqa: E402
    THEOREM_ELABORATOR_TYPES_PIN,
    write_elaborator_types_cache,
)


def _load_export_module():
    path = REPO / "scripts" / "export_theorem_types.py"
    spec = importlib.util.spec_from_file_location("export_theorem_types", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    export_mod = _load_export_module()
    exported = export_mod.export_elaborator_types()
    if not exported:
        print(
            "ERROR: elaborator export returned empty; "
            "run `lake build` then retry. Pin not updated.",
            file=sys.stderr,
        )
        return 1
    payload = {
        "authority": "lean_elaborator_export",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Produced by scripts/refresh_elaborator_pin.py from lake elaborator export.",
        "theorems": exported,
    }
    THEOREM_ELABORATOR_TYPES_PIN.parent.mkdir(parents=True, exist_ok=True)
    THEOREM_ELABORATOR_TYPES_PIN.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_elaborator_types_cache(exported)
    print(f"wrote {THEOREM_ELABORATOR_TYPES_PIN.relative_to(REPO)} ({len(exported)} theorems)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
