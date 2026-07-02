"""Compile Lean evidence files directly via `lake env lean`."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEAN_ROOT = REPO_ROOT / "lean"
PACKAGE_LEAN_ROOT = LEAN_ROOT / "QSpecBench"
LEAN_COMPILE_TIMEOUT = 300


def _lake_exe() -> str | None:
    lake = shutil.which("lake")
    if lake:
        return lake
    elan = Path.home() / ".elan" / "bin" / "lake"
    if elan.is_file():
        return str(elan)
    return None


def _evidence_relative_to_lean(evidence_file: Path) -> str:
    return os.path.relpath(evidence_file.resolve(), LEAN_ROOT)


def _lean_source_has_sorry(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("/-"):
            continue
        if "sorry" in stripped:
            return True
    return False


def _evidence_has_sorry(evidence_text: str) -> bool:
    return _lean_source_has_sorry(evidence_text)


def _package_sorry_scan_mtime(root: Path) -> float:
    if not root.is_dir():
        return 0.0
    mtimes = [path.stat().st_mtime for path in root.rglob("*.lean")]
    return max(mtimes) if mtimes else 0.0


@lru_cache(maxsize=4)
def _cached_package_sorry_paths(scan_root: str, mtime_key: float) -> tuple[str, ...]:
    root = Path(scan_root)
    if not root.is_dir():
        return ()
    hits: list[str] = []
    for path in sorted(root.rglob("*.lean")):
        if _lean_source_has_sorry(path.read_text(encoding="utf-8")):
            hits.append(str(path.relative_to(LEAN_ROOT)))
    return tuple(hits)


def scan_lean_package_for_sorry(root: Path | None = None) -> list[str]:
    """Return relative paths under lean/QSpecBench that contain sorry (non-comment)."""
    scan_root = root or PACKAGE_LEAN_ROOT
    mtime_key = _package_sorry_scan_mtime(scan_root)
    return list(_cached_package_sorry_paths(str(scan_root.resolve()), mtime_key))


def _required_import_present(evidence_text: str) -> bool:
    """Evidence must import the module it #checks (not rely on lake build alone)."""
    for line in evidence_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#check"):
            continue
        target = stripped[len("#check") :].strip()
        if not target:
            continue
        module = target.rsplit(".", 1)[0] if "." in target else target
        if f"import {module}" not in evidence_text:
            return False
    return True


def _ensure_elan_toolchain(toolchain: str, env: dict[str, str]) -> None:
    list_proc = subprocess.run(
        ["elan", "toolchain", "list"],
        cwd=str(LEAN_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if list_proc.returncode == 0 and toolchain in list_proc.stdout:
        return
    subprocess.run(
        ["elan", "toolchain", "install", toolchain],
        cwd=str(LEAN_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def check(evidence_file: Path) -> dict:
    errors: list[str] = []
    if not evidence_file.is_file():
        return {"ok": False, "adapter": "lean_proof", "errors": ["evidence file missing"]}

    evidence_text = evidence_file.read_text(encoding="utf-8")
    if _evidence_has_sorry(evidence_text):
        errors.append(f"sorry found in evidence file: {evidence_file}")

    package_sorry = scan_lean_package_for_sorry()
    if package_sorry:
        preview = ", ".join(package_sorry[:3])
        suffix = "…" if len(package_sorry) > 3 else ""
        errors.append(
            f"sorry found in lean package ({len(package_sorry)} file(s)): {preview}{suffix}"
        )

    if "#check" in evidence_text and not _required_import_present(evidence_text):
        errors.append(
            "evidence file must import the exact module for each #check anchor "
            "(e.g. import QSpecBench.Quantum.OpenQASM3 before "
            "#check QSpecBench.Quantum.OpenQASM3.my_theorem)"
        )

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
        _ensure_elan_toolchain(toolchain_file.read_text(encoding="utf-8").strip(), env)

    rel_evidence = _evidence_relative_to_lean(evidence_file)
    try:
        proc = subprocess.run(
            [lake, "env", "lean", rel_evidence],
            cwd=str(LEAN_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=LEAN_COMPILE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "adapter": "lean_proof",
            "path": str(evidence_file),
            "trust_level": "checked",
            "checker": "Lean 4 kernel",
            "command": f"lake env lean {rel_evidence}",
            "errors": [f"lake env lean timed out after {LEAN_COMPILE_TIMEOUT}s for {rel_evidence}"],
        }
    if proc.returncode != 0:
        errors.append(f"lake env lean failed for {rel_evidence}")
        if proc.stderr:
            errors.append(proc.stderr.strip()[:500])

    return {
        "ok": proc.returncode == 0 and not errors,
        "adapter": "lean_proof",
        "path": str(evidence_file),
        "trust_level": "checked",
        "checker": "Lean 4 kernel",
        "command": f"lake env lean {rel_evidence}",
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
