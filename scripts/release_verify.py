#!/usr/bin/env python3
"""Exact-head release verifier.

Refuses CI evidence from any SHA other than the candidate. Orchestrates schema,
promotion policy, generated-doc drift, and optional SBOM/manifest checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=REPO)


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def write_file_manifest(out: Path) -> dict:
    """Hash the release tree using git-visible paths (tracked + untracked, not ignored)."""
    listed = subprocess.check_output(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=REPO,
    )
    rels = [item.decode("utf-8") for item in listed.split(b"\0") if item]
    files: list[dict[str, str]] = []
    for rel in sorted(rels):
        path = REPO / rel
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": rel.replace("\\", "/"), "sha256": digest})
    payload = {
        "schema": "qspecbench.release_manifest.v1",
        "head": _git_head(),
        "files": files,
        "file_count": len(files),
    }
    blob = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    payload["bundle_hash"] = hashlib.sha256(blob).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def write_sbom_stub(out: Path, head: str) -> None:
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "QSpecBench",
                "version": "1.0.0-candidate",
                "bom-ref": head,
            }
        },
        "components": [
            {"type": "library", "name": "pydantic", "version": ">=2.0"},
            {"type": "library", "name": "pyyaml", "version": ">=6.0"},
            {"type": "library", "name": "jsonschema", "version": ">=4.0"},
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exact-head release verify")
    parser.add_argument("--candidate-sha", required=True, help="Exact git SHA being verified")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    head = _git_head()
    if head != args.candidate_sha:
        print(
            f"release_verify refused: HEAD {head} is not candidate {args.candidate_sha}",
            file=sys.stderr,
        )
        return 2
    steps = [
        [sys.executable, "scripts/check_release_contract.py", "--strict-qualification"],
        [sys.executable, "-m", "qspecbench", "validate", "benchmarks/", "--strict-all", "--audit-graph"],
        [sys.executable, "-c", "from qspecbench.generated_status import generate_status_snapshot; from pathlib import Path; expected=Path('docs/generated_status.md').read_text(encoding='utf-8'); actual=generate_status_snapshot(Path('benchmarks')); assert actual==expected, 'generated_status drift'"],
        [sys.executable, "-c", "from qspecbench.interoperability import generate_interoperability_matrix; from pathlib import Path; expected=Path('docs/interoperability_matrix.md').read_text(encoding='utf-8'); actual=generate_interoperability_matrix(); assert actual==expected, 'interoperability_matrix drift'"],
        [sys.executable, "-c", (
            "from pathlib import Path; from qspecbench.migration_report import formerly_promoted_inventory, report_digest; "
            "rows=formerly_promoted_inventory(Path('benchmarks')); "
            "expected=Path('docs/audits/migration_report.sha256').read_text(encoding='utf-8').strip(); "
            "actual=report_digest(rows); "
            "assert actual==expected, f'migration_report drift: {actual} != {expected}'"
        )],
    ]
    if not args.skip_tests:
        steps.append(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_v1_substrate.py",
                "tests/test_typed_adapter_execution.py",
                "tests/test_lean_qec_fsm.py",
                "tests/test_release_contract.py",
                "-q",
            ]
        )
    for cmd in steps:
        code = _run(cmd)
        if code != 0:
            return code
    manifest = write_file_manifest(REPO / "docs" / "release" / "manifest.json")
    write_sbom_stub(REPO / "docs" / "release" / "sbom.cdx.json", head)
    print(f"release_verify ok head={head} files={manifest['file_count']}")
    print(
        "note: Lean-QEC cold acceptance is not asserted here; see docs/release_audit_v1.md "
        "and .github/workflows/lean-qec.yml for the live CI gate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
