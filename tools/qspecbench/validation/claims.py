"""Claim coherence / claim-diff validation wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_claim_rules(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    # Lazy imports avoid circular import with claim_diff → validate.load_spec.
    from qspecbench.claim_coherence import validate_claim_coherence
    from qspecbench.claim_diff import validate_claim_diff

    errors: list[str] = []
    errors.extend(validate_claim_diff(claim_dir))
    errors.extend(validate_claim_coherence(spec, claim_dir))
    return errors
