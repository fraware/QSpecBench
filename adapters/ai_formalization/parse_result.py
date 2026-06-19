"""Validate AI formalization rubrics and optional Lean draft syntax."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCORE_RE = re.compile(r"(?:^|\n)\s*(?:##\s*)?[Ss]core\s*:\s*([0-5])\b", re.MULTILINE)
REVIEWER_RE = re.compile(
    r"(?:^|\n)\s*(?:##\s*)?[Rr]eviewer\s+role\s*\n+([^\n#]+)",
    re.MULTILINE,
)
ASSUMPTION_LINE_RE = re.compile(r"^\s*[-*]\s*(.+)$", re.MULTILINE)


def _parse_rubric_markdown(text: str) -> dict[str, Any]:
    score_match = SCORE_RE.search(text)
    reviewer_match = REVIEWER_RE.search(text)
    assumptions: list[str] = []
    if "## Assumptions" in text or "## assumptions" in text.lower():
        section = re.split(r"##\s+[Aa]ssumptions", text, maxsplit=1)
        if len(section) > 1:
            for line in section[1].splitlines():
                m = re.match(r"^\s*[-*]\s*(.+)$", line)
                if m:
                    assumptions.append(m.group(1).strip())
    if not assumptions:
        checklist = re.search(
            r"##\s+[Rr]ubric checklist\s*\n(.*?)(?:\n##|\Z)",
            text,
            re.DOTALL,
        )
        if checklist:
            for m in ASSUMPTION_LINE_RE.finditer(checklist.group(1)):
                item = m.group(1).strip()
                if item and not item.startswith("[ ]") and not item.startswith("[x]"):
                    assumptions.append(item)
    return {
        "score": int(score_match.group(1)) if score_match else None,
        "reviewer_role": reviewer_match.group(1).strip() if reviewer_match else None,
        "assumptions": assumptions,
    }


def _load_rubric(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("rubric JSON must be an object")
        return data
    parsed = _parse_rubric_markdown(text)
    if "rubric" not in text.lower() and "semantic" not in text.lower():
        parsed.setdefault("_warnings", []).append("missing rubric heading")
    return parsed


def validate_rubric_data(data: dict[str, Any], *, min_score_for_reference: int | None = None) -> list[str]:
    errors: list[str] = []
    score = data.get("score")
    if score is None:
        errors.append("missing score field (0-5)")
    elif not isinstance(score, int) or score < 0 or score > 5:
        errors.append("score must be integer 0-5")
    elif min_score_for_reference is not None and score < min_score_for_reference:
        errors.append(f"reference maturity requires rubric score >= {min_score_for_reference}")

    reviewer = data.get("reviewer_role")
    if not reviewer or not str(reviewer).strip():
        errors.append("missing reviewer_role")
    elif not isinstance(reviewer, str):
        errors.append("reviewer_role must be a string")

    assumptions = data.get("assumptions")
    if assumptions is None:
        errors.append("missing assumptions list")
    elif not isinstance(assumptions, list):
        errors.append("assumptions must be a list")
    elif not all(isinstance(a, str) and a.strip() for a in assumptions):
        errors.append("assumptions must be non-empty strings")
    return errors


def _lean_syntax_check(draft_path: Path) -> dict[str, Any]:
    if not draft_path.is_file():
        return {
            "syntactically_valid": None,
            "lean_check": "skipped",
            "lean_errors": [f"draft not found: {draft_path}"],
        }
    lean = shutil.which("lean")
    if not lean:
        return {
            "syntactically_valid": None,
            "lean_check": "skipped",
            "lean_errors": ["lean not in PATH"],
        }
    proc = subprocess.run(
        [lean, str(draft_path)],
        capture_output=True,
        text=True,
    )
    combined = (proc.stderr or "") + (proc.stdout or "")
    if proc.returncode != 0:
        lowered = combined.lower()
        if any(
            token in lowered
            for token in ("ssl", "download", "certificate", "revocation", "network", "connect error")
        ):
            return {
                "syntactically_valid": None,
                "lean_check": "skipped",
                "lean_errors": [combined.strip() or "lean environment error"],
            }
    ok = proc.returncode == 0
    return {
        "syntactically_valid": ok,
        "lean_check": "parse_only",
        "lean_errors": [proc.stderr.strip()] if proc.stderr.strip() and not ok else [],
    }


def check(path: Path, draft_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    try:
        data = _load_rubric(path)
    except (json.JSONDecodeError, ValueError) as exc:
        return {
            "ok": False,
            "adapter": "ai_formalization_rubric",
            "path": str(path),
            "trust_level": "untrusted",
            "errors": [str(exc)],
            "score": None,
        }

    claim_dir = path.parent.parent if path.parent.name in ("notes", "evidence", "artifacts") else path.parent
    min_score: int | None = None
    spec_path = claim_dir / "spec.yaml"
    if spec_path.is_file():
        import yaml

        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if spec.get("status", {}).get("maturity") == "reference":
            min_score = 4

    errors.extend(validate_rubric_data(data, min_score_for_reference=min_score))
    for warning in data.get("_warnings", []):
        errors.append(warning)

    lean_info: dict[str, Any] = {}
    if draft_path:
        lean_info = _lean_syntax_check(draft_path)
        if lean_info.get("syntactically_valid") is False:
            errors.extend(lean_info["lean_errors"])

    claim_dir = path.parent.parent if path.parent.name in ("notes", "evidence", "artifacts") else path.parent
    out_path = claim_dir / "evidence" / "rubric_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "score": data.get("score"),
        "reviewer_role": data.get("reviewer_role"),
        "assumptions": data.get("assumptions", []),
        "source_rubric": str(path.relative_to(claim_dir)) if path.is_relative_to(claim_dir) else str(path),
        "draft_lean": str(draft_path.relative_to(claim_dir)) if draft_path and draft_path.is_relative_to(claim_dir) else (
            str(draft_path) if draft_path else None
        ),
        **lean_info,
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": not errors,
        "adapter": "ai_formalization_rubric",
        "path": str(path),
        "trust_level": "untrusted",
        "errors": errors,
        "score": data.get("score"),
        "rubric_result": str(out_path),
        **lean_info,
    }


def main() -> None:
    path = Path(sys.argv[1])
    draft = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    result = check(path, draft)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
