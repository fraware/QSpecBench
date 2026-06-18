"""Verify SAT-style independently checkable certificates."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def verify(cert_path: Path) -> dict:
    errors: list[str] = []
    if not cert_path.is_file():
        return {"ok": False, "errors": ["certificate missing"]}
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    claim_dir = cert_path.parent.parent
    generator_rel = cert.get("generator")
    if generator_rel:
        generator = (claim_dir / generator_rel).resolve()
    else:
        generator = claim_dir / "evidence" / "verify_unitary_equality.py"
    if generator.is_file():
        proc = subprocess.run([sys.executable, str(generator)], capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append("generator failed")
        fresh = json.loads(cert_path.read_text(encoding="utf-8"))
        if not fresh.get("equal"):
            errors.append("certificate reports equal=false")
    else:
        if not cert.get("equal"):
            errors.append("certificate equal flag false")
    return {
        "ok": not errors,
        "adapter": "sat_certificate",
        "path": str(cert_path),
        "trust_level": "independently_checkable",
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = verify(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
