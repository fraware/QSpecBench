"""Coq proof evidence adapter — optional kernel when QSPECBENCH_COQ=1."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


COQ_COMPILE_TIMEOUT = 300


def _coq_available() -> bool:
    return shutil.which("coqc") is not None


def check(evidence_file: Path) -> dict:
    enabled = os.environ.get("QSPECBENCH_COQ", "0") == "1"
    if not enabled:
        return {
            "ok": False,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "not_checked",
            "skipped": True,
            "errors": [
                "Coq kernel not enabled; set QSPECBENCH_COQ=1 and install coqc for local checks"
            ],
        }

    if not evidence_file.is_file():
        return {
            "ok": False,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "not_checked",
            "skipped": True,
            "errors": [f"evidence file missing: {evidence_file}"],
        }

    if not _coq_available():
        return {
            "ok": False,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "not_checked",
            "skipped": True,
            "errors": [
                "QSPECBENCH_COQ=1 but coqc not found on PATH; install Coq or disable the flag"
            ],
        }

    try:
        subprocess.run(
            ["coqc", str(evidence_file)],
            check=True,
            capture_output=True,
            text=True,
            cwd=evidence_file.parent,
            timeout=COQ_COMPILE_TIMEOUT,
        )
        return {
            "ok": True,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "kernel_checked",
            "skipped": False,
            "errors": [],
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "not_checked",
            "skipped": False,
            "errors": [f"coqc timed out after {COQ_COMPILE_TIMEOUT}s"],
        }
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or "").strip()
        return {
            "ok": False,
            "adapter": "coq_proof",
            "path": str(evidence_file),
            "trust_level": "not_checked",
            "skipped": False,
            "errors": [stderr or f"coqc failed with exit code {exc.returncode}"],
        }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
