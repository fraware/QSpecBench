"""Run Lean 4 kernel check via Lake build."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEAN_ROOT = REPO_ROOT / "lean"


def _lake_exe() -> str | None:
    lake = shutil.which("lake")
    if lake:
        return lake
    elan = Path.home() / ".elan" / "bin" / "lake"
    if elan.is_file():
        return str(elan)
    return None


def check(evidence_file: Path) -> dict:
    errors: list[str] = []
    if not evidence_file.is_file():
        return {"ok": False, "adapter": "lean_proof", "errors": ["evidence file missing"]}

    sorry_hits: list[str] = []
    qspec_root = LEAN_ROOT / "QSpecBench"
    scan_roots = [qspec_root] if qspec_root.is_dir() else [LEAN_ROOT]
    for root in scan_roots:
        for lean_file in root.rglob("*.lean"):
            if ".lake" in lean_file.parts:
                continue
            text = lean_file.read_text(encoding="utf-8")
            if "sorry" in text and not lean_file.name.endswith(".olean"):
                # ignore comments-only sorry by checking non-comment lines
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("--") or stripped.startswith("/-"):
                        continue
                    if "sorry" in stripped:
                        sorry_hits.append(str(lean_file.relative_to(REPO_ROOT)))
                        break
    evidence_text = evidence_file.read_text(encoding="utf-8")
    if "sorry" in evidence_text:
        sorry_hits.append(str(evidence_file))

    if sorry_hits:
        return {
            "ok": False,
            "adapter": "lean_proof",
            "errors": [f"sorry found in: {', '.join(sorry_hits)}"],
        }

    lake = _lake_exe()
    if not lake:
        return {
            "ok": False,
            "adapter": "lean_proof",
            "trust_level": "checked",
            "errors": ["lake not found; install Lean 4 via elan"],
        }

    env = os.environ.copy()
    elan_bin = Path.home() / ".elan" / "bin"
    if elan_bin.is_dir():
        env["PATH"] = str(elan_bin) + os.pathsep + env.get("PATH", "")

    toolchain_file = LEAN_ROOT / "lean-toolchain"
    if toolchain_file.is_file():
        subprocess.run(
            ["elan", "toolchain", "install", toolchain_file.read_text(encoding="utf-8").strip()],
            cwd=str(LEAN_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

    proc = subprocess.run(
        [lake, "build"],
        cwd=str(LEAN_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.returncode != 0:
        errors.append("lake build failed")
        if proc.stderr:
            errors.append(proc.stderr.strip()[:500])

    return {
        "ok": proc.returncode == 0 and not errors,
        "adapter": "lean_proof",
        "path": str(evidence_file),
        "trust_level": "checked",
        "checker": "Lean 4 kernel",
        "errors": errors,
        "stdout_tail": proc.stdout.strip().splitlines()[-3:] if proc.stdout else [],
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
