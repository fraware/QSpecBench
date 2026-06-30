#!/usr/bin/env python3
"""Sync on-disk kernel QASM bytes into Lean ``*KernelArtifactSource`` defs.

Reads each kernel artifact with LF normalization (see docs/bridge_codegen_design.md)
and updates ``lean/QSpecBench/Quantum/OpenQASM3Parser.lean`` embedded string literals.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from qspecbench.bridge_codegen import (  # noqa: E402
    KERNEL_ARTIFACT_QASM_REL,
    KERNEL_ARTIFACT_SOURCE_DEF,
    KERNEL_BRIDGE_IDS,
    KERNEL_TARGET_ARTIFACT_QASM_REL,
    KERNEL_TARGET_ARTIFACT_SOURCE_DEF,
    read_kernel_qasm_lf_normalized,
    update_lean_kernel_artifact_source_def,
)


def sync_one(benchmark_id: str, *, dry_run: bool = False) -> bool:
    def_name = KERNEL_ARTIFACT_SOURCE_DEF.get(benchmark_id)
    qasm_rel = KERNEL_ARTIFACT_QASM_REL.get(benchmark_id)
    if not def_name or not qasm_rel:
        raise KeyError(f"no kernel artifact mapping for {benchmark_id!r}")
    source = read_kernel_qasm_lf_normalized(REPO / qasm_rel)
    if dry_run:
        return True
    return update_lean_kernel_artifact_source_def(def_name, source)


def sync_target(benchmark_id: str, *, dry_run: bool = False) -> bool:
    def_name = KERNEL_TARGET_ARTIFACT_SOURCE_DEF.get(benchmark_id)
    qasm_rel = KERNEL_TARGET_ARTIFACT_QASM_REL.get(benchmark_id)
    if not def_name or not qasm_rel:
        raise KeyError(f"no target kernel artifact mapping for {benchmark_id!r}")
    source = read_kernel_qasm_lf_normalized(REPO / qasm_rel)
    if dry_run:
        return True
    return update_lean_kernel_artifact_source_def(def_name, source)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate mappings without writing OpenQASM3Parser.lean",
    )
    parser.add_argument(
        "--include-target",
        action="store_true",
        help="Also sync toffoli target kernel artifact source when mapped",
    )
    args = parser.parse_args()
    changed = 0
    for benchmark_id in sorted(KERNEL_BRIDGE_IDS):
        if sync_one(benchmark_id, dry_run=args.dry_run):
            changed += 1
            print(f"synced {benchmark_id} -> {KERNEL_ARTIFACT_SOURCE_DEF[benchmark_id]}")
    if args.include_target:
        for benchmark_id in sorted(KERNEL_TARGET_ARTIFACT_SOURCE_DEF):
            if sync_target(benchmark_id, dry_run=args.dry_run):
                changed += 1
                print(
                    f"synced target {benchmark_id} -> "
                    f"{KERNEL_TARGET_ARTIFACT_SOURCE_DEF[benchmark_id]}"
                )
    if args.dry_run:
        print(f"dry-run OK ({len(KERNEL_BRIDGE_IDS)} kernel artifacts)")
    else:
        print(f"done ({changed} definitions updated)")


if __name__ == "__main__":
    main()
