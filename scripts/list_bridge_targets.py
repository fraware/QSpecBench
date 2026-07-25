"""List bridge verify targets dynamically from the corpus (no hardcoded paths)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.artifacts import find_spec_files  # noqa: E402
from qspecbench.bridge_codegen import is_dynamic_ast_checked_link  # noqa: E402
from qspecbench.validate import load_spec  # noqa: E402


def _load_bridge(spec: dict, claim_dir: Path) -> dict | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        try:
            return json.loads(bridge_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def bridge_targets(root: Path | None = None) -> list[str]:
    """Static (matrix/AST-authority) bridge verify targets.

    Excludes benchmarks whose claimed_link is dynamic-AST/denotation-only
    (measure+if `CanonicalAst`): those are never gate-only and are checked
    separately via ``qspecbench dynamic-simulate`` / ``check-evidence``,
    not the static ``verify-bridge`` command.
    """
    root = root or (REPO / "benchmarks")
    out: list[str] = []
    for spec_path in find_spec_files(root):
        claim_dir = spec_path.parent
        if "_template" in claim_dir.parts:
            continue
        spec = load_spec(spec_path)
        maturity = (spec.get("status") or {}).get("maturity")
        if maturity not in {"artifact_bound_reference_claim", "reference_claim"}:
            continue
        bridge = _load_bridge(spec, claim_dir)
        if bridge is None:
            continue
        if is_dynamic_ast_checked_link(bridge.get("claimed_link")):
            continue
        out.append(str(claim_dir.relative_to(REPO)).replace("\\", "/"))
    return sorted(out)


def main() -> None:
    targets = bridge_targets()
    if "--json" in sys.argv:
        print(json.dumps(targets, indent=2))
    else:
        for t in targets:
            print(t)


if __name__ == "__main__":
    main()
