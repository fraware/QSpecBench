"""Semantic bridge verification adapter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check(evidence_path: Path) -> dict:
    claim_dir = evidence_path.parent.parent
    from qspecbench.verify_bridge import write_bridge_result

    result = write_bridge_result(claim_dir, evidence_path)
    return {
        "ok": result.get("ok", False),
        "adapter": "bridge_verify",
        "path": str(evidence_path),
        "trust_level": "checked",
        "checker": "verify-bridge",
        "errors": result.get("errors", []),
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
