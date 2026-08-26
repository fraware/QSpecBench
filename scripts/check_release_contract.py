#!/usr/bin/env python3
"""Check the canonical v1 release contract against the repository tree."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from qspecbench.release_contract import validate_release_contract

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate QSpecBench v1 release contract")
    parser.add_argument(
        "--strict-qualification",
        action="store_true",
        help="Require assurance closure and fully qualified Level-C reference capabilities.",
    )
    args = parser.parse_args()
    report = validate_release_contract(REPO, strict_qualification=args.strict_qualification)
    if report.errors:
        for error in report.errors:
            print(f"release-contract error: {error}", file=sys.stderr)
        print(
            f"release-contract FAIL release={report.release_id} corpus={len(report.corpus)}",
            file=sys.stderr,
        )
        return 1
    print(f"release-contract OK release={report.release_id} corpus={len(report.corpus)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
