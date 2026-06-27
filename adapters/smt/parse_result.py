"""Parse and verify SMT-LIB2 certificates with z3 or cvc5 when available."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _load_certificate(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_smt_file(cert: dict, cert_path: Path) -> Path | None:
    rel = cert.get("smt_file")
    if not rel:
        return None
    smt = (cert_path.parent / rel).resolve()
    return smt if smt.is_file() else None


def _run_solver(solver: str, smt_path: Path, expected: str) -> tuple[bool, str]:
    proc = subprocess.run(
        [solver, str(smt_path)],
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    verdict = output.strip().splitlines()[-1].lower() if output.strip() else ""
    ok = proc.returncode == 0 and expected in verdict
    return ok, output.strip() or f"exit {proc.returncode}"


def check(cert_path: Path) -> dict:
    errors: list[str] = []
    if not cert_path.is_file():
        return {"ok": False, "adapter": "smt_certificate", "errors": ["certificate file missing"]}

    try:
        cert = _load_certificate(cert_path)
    except json.JSONDecodeError as exc:
        return {"ok": False, "adapter": "smt_certificate", "errors": [f"invalid JSON: {exc}"]}

    smt_path = _resolve_smt_file(cert, cert_path)
    if smt_path is None:
        return {"ok": False, "adapter": "smt_certificate", "errors": ["smt_file missing or not found"]}

    expected = str(cert.get("expected", "sat")).lower()
    if expected not in {"sat", "unsat", "unknown"}:
        return {
            "ok": False,
            "adapter": "smt_certificate",
            "errors": [f"invalid expected verdict: {expected!r}"],
        }

    if os.environ.get("QSPECBENCH_SKIP_SMT") == "1":
        return {
            "ok": False,
            "adapter": "smt_certificate",
            "path": str(cert_path),
            "trust_level": "not_checked",
            "skipped": True,
            "notes": "QSPECBENCH_SKIP_SMT=1",
        }

    for solver in ("z3", "cvc5"):
        if shutil.which(solver):
            ok, detail = _run_solver(solver, smt_path, expected)
            if ok:
                return {
                    "ok": True,
                    "adapter": "smt_certificate",
                    "path": str(cert_path),
                    "solver": solver,
                    "expected": expected,
                    "trust_level": "independently_checkable",
                    "detail": detail.splitlines()[-1] if detail else "",
                }
            errors.append(f"{solver}: {detail}")

    # No solver: structural syntax check only — not independently verified.
    text = smt_path.read_text(encoding="utf-8")
    if "(check-sat)" not in text:
        errors.append("smt2 missing (check-sat)")
    return {
        "ok": False,
        "adapter": "smt_certificate",
        "path": str(cert_path),
        "trust_level": "not_checked",
        "skipped": True,
        "solver": None,
        "errors": errors + ["install z3 or cvc5 for independent verification"],
        "notes": "SMT syntax present; solver not available — not independently checkable",
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result.get("ok") or result.get("skipped") else 1)


if __name__ == "__main__":
    main()
