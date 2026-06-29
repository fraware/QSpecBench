"""Verify Lean-side BridgeMetadata against bridge_theorem_manifest.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from qspecbench.bridge_manifest import load_manifest
from qspecbench.schema import REPO_ROOT

OPENQASM3_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "OpenQASM3.lean"

_BRIDGE_METADATA_RE = re.compile(
    r"def\s+bridge_cnot_metadata\s*:\s*BridgeMetadata\s*:=\s*\{(.*?)\}",
    re.DOTALL,
)
_FIELD_RES: dict[str, re.Pattern[str]] = {
    "benchmarkId": re.compile(r'benchmarkId\s*:=\s*"([^"]+)"'),
    "claimedLink": re.compile(r'claimedLink\s*:=\s*"([^"]+)"'),
    "artifactSha256": re.compile(r'artifactSha256\s*:=\s*"([a-f0-9]{64})"'),
    "astSha256": re.compile(r'astSha256\s*:=\s*"([a-f0-9]{64})"'),
    "generatedLeanSha256": re.compile(r'generatedLeanSha256\s*:=\s*"([a-f0-9]{64})"'),
    "theoremIdentifierSha256": re.compile(r'theoremIdentifierSha256\s*:=\s*"([a-f0-9]{64})"'),
    "theoremSourceStatementHash": re.compile(
        r'theoremSourceStatementHash\s*:=\s*"([a-f0-9]{64})"'
    ),
    "packageLeanSha256": re.compile(r'packageLeanSha256\s*:=\s*"([a-f0-9]{64})"'),
}

_LEAN_TO_MANIFEST: dict[str, str] = {
    "benchmarkId": "benchmark_id",
    "artifactSha256": "artifact_sha256",
    "astSha256": "ast_sha256",
    "generatedLeanSha256": "generated_lean_sha256",
    "theoremIdentifierSha256": "theorem_identifier_sha256",
    "theoremSourceStatementHash": "theorem_source_statement_hash",
    "packageLeanSha256": "package_lean_sha256",
}


def extract_bridge_cnot_metadata(path: Path = OPENQASM3_LEAN) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    block = _BRIDGE_METADATA_RE.search(text)
    if not block:
        raise ValueError(f"bridge_cnot_metadata not found in {path}")
    body = block.group(1)
    out: dict[str, str] = {}
    for lean_key, pattern in _FIELD_RES.items():
        match = pattern.search(body)
        if not match:
            raise ValueError(f"BridgeMetadata field {lean_key!r} missing in bridge_cnot_metadata")
        out[lean_key] = match.group(1)
    return out


def verify_bridge_cnot_metadata_against_manifest() -> list[str]:
    errors: list[str] = []
    lean_meta = extract_bridge_cnot_metadata()
    if lean_meta.get("claimedLink") != "kernel_checked_codegen_trace":
        errors.append("bridge_cnot_metadata.claimedLink must be kernel_checked_codegen_trace")
    entry = next(
        (
            e
            for e in load_manifest()["entries"]
            if e.get("benchmark_id") == lean_meta.get("benchmarkId")
        ),
        None,
    )
    if entry is None:
        errors.append("bridge_cnot_metadata.benchmarkId not found in bridge_theorem_manifest.json")
        return errors
    for lean_key, manifest_key in _LEAN_TO_MANIFEST.items():
        lean_val = lean_meta.get(lean_key)
        manifest_val = entry.get(manifest_key)
        legacy = entry.get("theorem_content_sha256")
        if manifest_key == "theorem_source_statement_hash" and not manifest_val:
            manifest_val = legacy
        if lean_val and manifest_val and lean_val != manifest_val:
            errors.append(
                f"bridge_cnot_metadata.{lean_key} ({lean_val[:12]}…) "
                f"!= manifest {manifest_key} ({str(manifest_val)[:12]}…)"
            )
    return errors
