#!/usr/bin/env python3
"""Export kernel bridge theorem type hashes for manifest / semantic_bridge pinning (v0.3)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.bridge_codegen import (  # noqa: E402
    GENERATED_MODULE_MAP,
    KERNEL_CHECKED_THEOREMS,
    THEOREM_ELABORATOR_TYPES_CACHE,
    _normalize_theorem_statement,
    theorem_elaborator_hash,
    theorem_source_statement_hash,
    write_elaborator_types_cache,
)

CHECK_LEAN = REPO / "lean" / "QSpecBench" / "ExportTheoremTypesCheck.lean"
_CHECK_LINE = re.compile(
    r"^QSpecBench\.Quantum\.OpenQASM3\.(bridge_\w+)\s*(.*)$"
)


def _parse_check_output(stdout: str) -> dict[str, str]:
    short_to_bid = {
        full.split(".")[-1]: bid for bid, full in KERNEL_CHECKED_THEOREMS.items()
    }
    out: dict[str, str] = {}
    pending: str | None = None
    type_lines: list[str] = []

    def flush() -> None:
        nonlocal pending, type_lines
        if pending and type_lines:
            out[pending] = _normalize_theorem_statement(" ".join(type_lines))
        pending = None
        type_lines = []

    for raw in stdout.splitlines():
        line = raw.strip()
        if not line or line.startswith("info:"):
            continue
        match = _CHECK_LINE.match(line)
        if match:
            flush()
            thm_short = match.group(1)
            pending = short_to_bid.get(thm_short)
            rest = match.group(2).strip()
            type_lines = [rest] if rest else []
            continue
        if pending:
            type_lines.append(line)
    flush()
    return out
def _run_lake_check_export() -> dict[str, str]:
    lean_dir = REPO / "lean"
    if not CHECK_LEAN.is_file():
        raise FileNotFoundError(CHECK_LEAN)
    proc = subprocess.run(
        ["lake", "env", "lean", str(CHECK_LEAN.relative_to(lean_dir))],
        cwd=lean_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "lake env lean ExportTheoremTypesCheck.lean failed:\n"
            + (proc.stderr or proc.stdout or "(no output)")
        )
    out = _parse_check_output(proc.stdout)
    if not out:
        raise RuntimeError("no theorem types parsed from ExportTheoremTypesCheck.lean output")
    return out


def _run_lake_exe_export() -> dict[str, str]:
    lean_dir = REPO / "lean"
    proc = subprocess.run(
        ["lake", "exe", "exportTheoremTypes"],
        cwd=lean_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "lake exe exportTheoremTypes failed")
    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "\t" not in line:
            continue
        bid, ty = line.split("\t", 1)
        out[bid.strip()] = _normalize_theorem_statement(ty.strip())
    return out


def export_elaborator_types() -> dict[str, str]:
    env = os.environ.get("QSPECBENCH_LEAN_ELABORATOR", "").strip().lower()
    if env in {"0", "false", "no"}:
        return {}
    try:
        return _run_lake_check_export()
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError):
        return _run_lake_exe_export()


def main() -> None:
    try:
        exported = export_elaborator_types()
        write_elaborator_types_cache(exported)
    except (RuntimeError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"warning: elaborator export unavailable ({exc}); using regex fallback only", file=sys.stderr)
        exported = {}

    out: dict[str, dict[str, str | None]] = {}
    for benchmark_id in sorted(GENERATED_MODULE_MAP):
        if benchmark_id.endswith("_target"):
            continue
        out[benchmark_id] = {
            "theorem_source_statement_hash": theorem_source_statement_hash(benchmark_id),
            "theorem_elaborator_hash": theorem_elaborator_hash(benchmark_id),
            "elaborator_type": exported.get(benchmark_id),
        }
    print(json.dumps(out, indent=2, sort_keys=True))
    if exported:
        print(f"wrote {THEOREM_ELABORATOR_TYPES_CACHE.relative_to(REPO)}", file=sys.stderr)


if __name__ == "__main__":
    main()
