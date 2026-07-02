"""QCEC equivalence checker adapter for QSpecBench."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


QCEC_CLI_TIMEOUT = 300


def _parse_equivalence_verdict(text: str) -> str:
    lowered = text.lower()
    if "not equivalent" in lowered or "non-equivalent" in lowered or "non_equivalent" in lowered:
        return "not_equivalent"
    if "equivalent" in lowered:
        return "equivalent"
    return text.strip() or "unknown"


def _check_with_mqt(source: Path, target: Path) -> dict:
    from mqt import qcec

    result = qcec.verify(str(source), str(target))
    verdict_raw = str(getattr(result, "equivalence", result))
    verdict = _parse_equivalence_verdict(verdict_raw)
    ok = verdict == "equivalent"
    return {
        "ok": ok,
        "adapter": "qcec",
        "source": str(source),
        "target": str(target),
        "equivalence_verdict": verdict,
        "trust_level": "externally_trusted",
        "errors": [] if ok else [f"QCEC verdict: {verdict_raw}"],
    }


def _check_with_cli(source: Path, target: Path) -> dict:
    qcec_bin = shutil.which("qcec")
    if not qcec_bin:
        raise FileNotFoundError("qcec not in PATH")
    proc = subprocess.run(
        [qcec_bin, str(source), str(target)],
        capture_output=True,
        text=True,
        timeout=QCEC_CLI_TIMEOUT,
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    verdict = _parse_equivalence_verdict(combined)
    ok = proc.returncode == 0 and verdict == "equivalent"
    return {
        "ok": ok,
        "adapter": "qcec",
        "source": str(source),
        "target": str(target),
        "equivalence_verdict": verdict,
        "trust_level": "externally_trusted",
        "errors": [] if ok else [combined.strip() or f"exit code {proc.returncode}"],
    }


def check(source: Path, target: Path | None = None) -> dict:
    errors: list[str] = []
    if not source.is_file():
        errors.append(f"missing source: {source}")
    if target is None:
        errors.append("target path required for QCEC equivalence check")
    elif not target.is_file():
        errors.append(f"missing target: {target}")
    if errors:
        return {
            "ok": False,
            "adapter": "qcec",
            "source": str(source),
            "target": str(target) if target else None,
            "equivalence_verdict": "unknown",
            "errors": errors,
        }

    try:
        return _check_with_mqt(source, target)
    except ImportError:
        try:
            return _check_with_cli(source, target)
        except FileNotFoundError:
            return {
                "ok": False,
                "adapter": "qcec",
                "source": str(source),
                "target": str(target),
                "equivalence_verdict": "unknown",
                "errors": ["mqt.qcec not installed and qcec CLI not in PATH"],
            }
    except Exception as exc:
        return {
            "ok": False,
            "adapter": "qcec",
            "source": str(source),
            "target": str(target),
            "equivalence_verdict": "unknown",
            "errors": [str(exc)],
        }


def main() -> None:
    source = Path(sys.argv[1])
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    result = check(source, target)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
