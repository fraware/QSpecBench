#!/usr/bin/env python3
"""Historical helper. v1 gold promotions are frozen; this script refuses to write RC/ABRC."""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "Promotion freeze: new reference_claim / artifact_bound_reference_claim "
        "labels are blocked until authentic independent reviewers exist. "
        "See docs/promotion_freeze.md."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
