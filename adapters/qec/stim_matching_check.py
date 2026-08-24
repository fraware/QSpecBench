"""Dispatch wrapper for Stim/PyMatching-family ``qec_verifier_result`` evidence.

``qec_verifier_result`` evidence in this corpus covers several distinct
checker-specific verifiers beyond the generic stabilizer-code JSON validator in
``adapters/qec/parse_result.py``. This wrapper dispatches by the on-disk result
JSON's declared schema/command and invokes only registered verifier functions.

Historical result files may contain host-specific absolute artifact paths. Such
paths are never trusted for replay. When a portable claim-relative path is not
available, the wrapper resolves the artifact from the claim's ``artifacts/``
directory by the result's recorded SHA-256 and requires exactly one match. This
keeps replay content-addressed and independent of the machine that produced the
historical result.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PureWindowsPath

REPO_ROOT = Path(__file__).resolve().parents[2]

_DEM_RE = re.compile(r"--dem\s+(\S+)")
_TABLE_RE = re.compile(r"--table\s+(\S+)")
_GRAPH_RE = re.compile(r"--graph\s+(\S+)")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class StimMatchingCheckError(ValueError):
    pass


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_artifact_path(claim_dir: Path, filename: str) -> Path:
    from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path

    rel = f"artifacts/{filename}"
    escape = claim_path_escape_error(claim_dir, rel)
    if escape:
        raise StimMatchingCheckError(escape)
    path = resolve_claim_path(claim_dir, rel)
    if not path.is_file():
        raise StimMatchingCheckError(f"artifact missing: {rel}")
    return path


def _resolve_recorded_artifact(existing: dict, claim_dir: Path) -> tuple[Path, str]:
    """Resolve a historical result's artifact without trusting host-specific paths.

    A portable relative path is accepted only if it stays inside the claim and its
    bytes match the recorded SHA-256. Absolute POSIX/Windows paths are ignored for
    replay and resolved by content hash under ``artifacts/`` instead. Hash fallback
    requires exactly one matching file, preventing ambiguous rebinding.
    """
    from qspecbench.artifacts import resolve_claim_path

    digest = str(existing.get("sha256") or "")
    if _SHA256_RE.fullmatch(digest) is None:
        raise StimMatchingCheckError("historical DEM result must record a lowercase SHA-256")

    raw = str(existing.get("path") or "")
    is_host_absolute = bool(raw) and (Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute())
    if raw and not is_host_absolute:
        try:
            candidate = resolve_claim_path(claim_dir, raw)
        except ValueError as exc:
            raise StimMatchingCheckError(str(exc)) from exc
        if candidate.is_file():
            actual = _sha256_file(candidate)
            if actual != digest:
                raise StimMatchingCheckError(
                    f"recorded artifact SHA-256 mismatch: expected {digest}, got {actual}"
                )
            return candidate, digest

    artifacts_root = (claim_dir / "artifacts").resolve()
    if not artifacts_root.is_dir():
        raise StimMatchingCheckError("claim artifacts directory is missing")

    matches: list[Path] = []
    for item in sorted(artifacts_root.rglob("*")):
        if not item.is_file():
            continue
        resolved = item.resolve()
        if not resolved.is_relative_to(artifacts_root):
            continue
        if _sha256_file(resolved) == digest:
            matches.append(resolved)

    if not matches:
        raise StimMatchingCheckError(
            f"no claim artifact matches recorded SHA-256 {digest}"
        )
    if len(matches) != 1:
        rels = [str(path.relative_to(claim_dir.resolve())) for path in matches]
        raise StimMatchingCheckError(
            "recorded SHA-256 resolves ambiguously to multiple claim artifacts: "
            + ", ".join(rels)
        )
    return matches[0], digest


def _check(evidence_path: Path) -> tuple[bool, str, list[str]]:
    claim_dir = evidence_path.parent.parent
    existing = json.loads(evidence_path.read_text(encoding="utf-8"))
    schema = existing.get("schema")
    command = existing.get("command", "")

    if schema == "qspecbench.stim_pymatching_dem.v1" or "stim_pymatching_adapter" in command:
        from qspecbench.stim_pymatching_adapter import verify_stim_pymatching_dem

        dem_m = _DEM_RE.search(command)
        table_m = _TABLE_RE.search(command)
        if not dem_m or not table_m:
            raise StimMatchingCheckError(f"cannot recover --dem/--table from command: {command!r}")
        dem = _safe_artifact_path(claim_dir, dem_m.group(1))
        table = _safe_artifact_path(claim_dir, table_m.group(1))
        result = verify_stim_pymatching_dem(dem, table)
        return bool(result.get("ok", False)), "stim_pymatching_adapter", []

    if schema == "qspecbench.external_matching_agree.v1" or "pymatching_fixture_adapter" in command:
        from qspecbench.pymatching_fixture_adapter import verify_fixture_agreement

        graph_m = _GRAPH_RE.search(command)
        table_m = _TABLE_RE.search(command)
        if not graph_m or not table_m:
            raise StimMatchingCheckError(f"cannot recover --graph/--table from command: {command!r}")
        graph = _safe_artifact_path(claim_dir, graph_m.group(1))
        table = _safe_artifact_path(claim_dir, table_m.group(1))
        result = verify_fixture_agreement(graph, table)
        return bool(result.get("ok", False)), "pymatching_fixture_adapter", []

    if schema == "qspecbench.stim_declared_repetition_universe.v1":
        from qspecbench.stim_declared_universe_adapter import (
            verify_declared_repetition_universe,
        )

        result = verify_declared_repetition_universe(claim_dir / "artifacts")
        return bool(result.get("ok", False)), "stim_declared_universe_adapter", []

    if schema == "qspecbench.stim_declared_surface_universe.v1":
        from qspecbench.stim_declared_universe_adapter import (
            verify_declared_surface_universe,
        )

        result = verify_declared_surface_universe(claim_dir / "artifacts")
        return bool(result.get("ok", False)), "stim_declared_universe_adapter", []

    # Historical DEM result: replay the content-addressed artifact under this claim.
    from qspecbench.stim_dem_adapter import validate_stim_compatible_dem

    artifact, expected_sha256 = _resolve_recorded_artifact(existing, claim_dir)
    result = validate_stim_compatible_dem(artifact, expected_sha256=expected_sha256)
    return bool(result.get("ok", False)), "stim_dem_adapter", []


def check(evidence_path: Path) -> dict:
    try:
        ok, checker, errors = _check(evidence_path)
    except Exception as exc:  # noqa: BLE001 - any verifier failure is fail-closed here
        ok, checker, errors = False, "qec_stim_matching_dispatch", [str(exc)]
    return {
        "ok": ok,
        "adapter": "qec_stim_matching_dispatch",
        "path": str(evidence_path),
        "trust_level": "tool_checked",
        "checker": checker,
        "errors": errors,
    }


def main() -> None:
    path = Path(sys.argv[1]).resolve()
    result = check(path)
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
