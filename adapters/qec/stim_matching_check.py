"""Dispatch wrapper for Stim/PyMatching-family ``qec_verifier_result`` evidence.

``qec_verifier_result`` evidence in this corpus covers several distinct
checker-specific verifiers beyond the generic stabilizer-code JSON validator in
``adapters/qec/parse_result.py`` (that adapter validates ``code.json``-shaped
stabilizer codes -- it does not know how to invoke Stim or PyMatching). This
wrapper re-dispatches to the correct already-implemented, already-tested
verifier function based on the on-disk (corpus-trusted, reviewed) evidence
result JSON's own ``schema``/``command`` fields, so ``check-evidence`` exercises
the same function the review/promotion relied on instead of silently
mis-routing to the wrong checker.

Input artifact filenames (``--dem``/``--table``/``--graph``) are recovered from
the existing result JSON's self-recorded ``command`` string -- never from
untrusted external input -- and are then resolved and path-jailed under the
claim's ``artifacts/`` directory before use. Nothing here is executed as a
shell command; only the imported Python verifier functions are called
directly. Any failure (including a verifier raising its own fail-closed error)
is reported as ``ok: false`` -- never silently swallowed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_DEM_RE = re.compile(r"--dem\s+(\S+)")
_TABLE_RE = re.compile(r"--table\s+(\S+)")
_GRAPH_RE = re.compile(r"--graph\s+(\S+)")


class StimMatchingCheckError(ValueError):
    pass


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

    # Fall back to the fail-closed DEM schema+hash validator (no Stim/PyMatching
    # invocation): re-validate the same on-disk artifact this evidence pins.
    from qspecbench.stim_dem_adapter import validate_stim_compatible_dem

    artifact = Path(existing.get("path") or "")
    if not artifact.is_absolute():
        artifact = claim_dir / artifact
    try:
        artifact.relative_to(claim_dir.resolve())
    except ValueError as exc:
        raise StimMatchingCheckError(f"DEM artifact path escapes claim dir: {artifact}") from exc
    if not artifact.is_file():
        raise StimMatchingCheckError(f"stim DEM artifact missing: {artifact}")
    result = validate_stim_compatible_dem(artifact)
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
