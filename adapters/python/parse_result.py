"""Run a Python evidence script and capture structured output."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PYTHON_SCRIPT_TIMEOUT = 120
_RESULT_JSON_SUFFIX = ".result.json"


def script_for_evidence_path(path: Path) -> Path:
    """Map evidence path to the executable script.

    Specs may point at either the ``.py`` checker or its hashed ``.result.json``
    certificate. The latter must not be executed as Python.
    """
    name = path.name
    if name.endswith(_RESULT_JSON_SUFFIX):
        return path.with_name(name[: -len(_RESULT_JSON_SUFFIX)] + ".py")
    return path


def check(path: Path) -> dict:
    path = path.resolve()
    script = script_for_evidence_path(path).resolve()
    if not script.is_file():
        return {
            "ok": False,
            "adapter": "python_simulation",
            "path": str(path),
            "trust_level": "heuristic",
            "exit_code": 1,
            "stdout": "",
            "stderr": "",
            "error": f"python evidence script missing: {script.name}",
        }
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            cwd=str(script.parent),
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
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    # Only write the adapter sidecar when the evidence path is the script itself.
    # Never overwrite a hashed ``*.result.json`` certificate produced by the script.
    if path.suffix == ".py":
        out = path.with_name(path.stem + _RESULT_JSON_SUFFIX)
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
