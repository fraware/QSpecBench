"""Fail-closed check that committed schema examples validate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[1]
SCHEMA = REPO / "schema"


def main() -> int:
    errors: list[str] = []
    review_schema = json.loads((SCHEMA / "review_artifact.schema.json").read_text(encoding="utf-8"))
    # Validate one corpus review as the example surface.
    sample = next((REPO / "benchmarks").rglob("reviews/formal_review.json"))
    try:
        jsonschema.Draft202012Validator(review_schema).validate(
            json.loads(sample.read_text(encoding="utf-8"))
        )
    except jsonschema.ValidationError as exc:
        errors.append(f"review artifact example invalid: {exc.message}")

    profile_schema = json.loads((SCHEMA / "openqasm_profile.schema.json").read_text(encoding="utf-8"))
    for path in (SCHEMA / "profiles").glob("*.json"):
        try:
            jsonschema.Draft202012Validator(profile_schema).validate(
                json.loads(path.read_text(encoding="utf-8"))
            )
        except jsonschema.ValidationError as exc:
            errors.append(f"{path.name}: {exc.message}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("schema examples ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
