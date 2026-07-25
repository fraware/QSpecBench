"""Dynamic denotation semantic bridge verification adapter.

Wraps ``qspecbench.verify_dynamic_ast_bridge.write_dynamic_denotation_bridge_result``
for evidence entries whose ``checker`` is ``verify-dynamic-denotation-bridge CLI``
(fail-closed CanonicalAst measure/if bound to Measurement.writeZOutcome /
ClassicalReg denotation; never claims matrix KERNEL_BRIDGE). Distinct from
``parse_result.py`` in this directory, which wraps the matrix-based ``verify-bridge
CLI`` and must not be used for dynamic AST/denotation evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check(evidence_path: Path) -> dict:
    claim_dir = evidence_path.parent.parent
    from qspecbench.verify_dynamic_ast_bridge import write_dynamic_denotation_bridge_result

    out_rel = str(evidence_path.relative_to(claim_dir)).replace("\\", "/")
    result = write_dynamic_denotation_bridge_result(claim_dir, out_rel=out_rel)
    return {
        "ok": result.get("ok", False),
        "adapter": "dynamic_denotation_bridge_verify",
        "path": str(evidence_path),
        "trust_level": "checked",
        "checker": "verify-dynamic-denotation-bridge",
        "errors": result.get("errors", []),
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
