"""Review validation wiring (delegation to qspecbench.reviews)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qspecbench.reviews import validate_promotion_reviews


def validate_review_rules(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    return validate_promotion_reviews(spec, claim_dir)
