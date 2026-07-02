"""Benchmark discovery and artifact path helpers."""

from __future__ import annotations

from pathlib import Path

REQUIRED_DIRS = ("artifacts", "evidence", "expected", "notes")
FORBIDDEN_ROOT_ARTIFACTS = {".qasm", ".py", ".json", ".lean", ".v", ".smt2"}


def find_spec_files(root: Path) -> list[Path]:
    root = root.resolve()
    if root.is_file() and root.name == "spec.yaml":
        return [root]
    specs = []
    for path in sorted(root.rglob("spec.yaml")):
        if "_template" in path.parts:
            continue
        specs.append(path)
    return specs


def claim_dir_for_spec(spec_path: Path) -> Path:
    return spec_path.parent


def track_for_claim(claim_dir: Path, benchmarks_root: Path | None = None) -> str:
    if benchmarks_root is None:
        benchmarks_root = claim_dir
        while benchmarks_root.name != "benchmarks" and benchmarks_root.parent != benchmarks_root:
            benchmarks_root = benchmarks_root.parent
    return claim_dir.relative_to(benchmarks_root).parts[0]


def resolve_claim_path(claim_dir: Path, rel_path: str) -> Path:
    return (claim_dir / rel_path).resolve()


def claim_path_escape_error(claim_dir: Path, rel_path: str) -> str | None:
    """Return an error message if rel_path resolves outside claim_dir."""
    resolved = resolve_claim_path(claim_dir, rel_path)
    claim_root = claim_dir.resolve()
    if not resolved.is_relative_to(claim_root):
        return f"path escapes claim directory: {rel_path!r} -> {resolved}"
    return None


def check_layout(claim_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_DIRS:
        if not (claim_dir / name).is_dir():
            errors.append(f"Missing required directory: {claim_dir / name}")
    for child in claim_dir.iterdir():
        if not child.is_file():
            continue
        if child.suffix.lower() in FORBIDDEN_ROOT_ARTIFACTS:
            errors.append(f"Artifact/evidence file must not live in claim root: {child}")
    return errors
