#!/usr/bin/env python3
"""Fixture QBricks CLI for adapter tests only (not a real verifier)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOOL_NAME = "qbricks-fixture"
TOOL_VERSION = "0.0.1-fixture"
TOOL_OUTPUT_SCHEMA = "qspecbench.qbricks_tool_output.v1"


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print("usage: fake_qbricks_cli.py (--version | verify <circuit>)", file=sys.stderr)
        sys.exit(2)
    if argv[0] == "--version":
        print(f"{TOOL_NAME} {TOOL_VERSION}")
        sys.exit(0)
    if argv[0] == "verify":
        if len(argv) < 2:
            print("verify requires a circuit path", file=sys.stderr)
            sys.exit(2)
        circuit = Path(argv[1])
        if not circuit.is_file():
            print(json.dumps({
                "schema_version": TOOL_OUTPUT_SCHEMA,
                "verdict": "unknown",
                "tool": TOOL_NAME,
                "tool_version": TOOL_VERSION,
                "errors": [f"missing circuit: {circuit}"],
            }))
            sys.exit(1)
        print(
            json.dumps(
                {
                    "schema_version": TOOL_OUTPUT_SCHEMA,
                    "verdict": "proved",
                    "tool": TOOL_NAME,
                    "tool_version": TOOL_VERSION,
                    "circuit": str(circuit),
                }
            )
        )
        sys.exit(0)
    print(f"unknown command: {argv[0]}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
