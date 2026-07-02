"""Run a Python evidence script and capture structured output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PYTHON_SCRIPT_TIMEOUT = 120


def check(path: Path) -> dict:
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            cwd=str(path.parent),
            timeout=PYTHON_SCRIPT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "adapter": "python_simulation",
            "path": str(path),
            "trust_level": "heuristic",
            "exit_code": 1,
            "stdout": "",
            "stderr": "",
            "error": f"script timed out after {PYTHON_SCRIPT_TIMEOUT}s",
        }
    return {
        "ok": proc.returncode == 0,
        "adapter": "python_simulation",
        "path": str(path),
        "trust_level": "heuristic",
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "error": None if proc.returncode == 0 else "script failed",
    }


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    out = path.with_suffix(".result.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
