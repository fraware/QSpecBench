"""Run declared evidence checks for a benchmark claim."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from qspecbench.schema import REPO_ROOT
from qspecbench.validate import load_spec

ADAPTERS_ROOT = REPO_ROOT / "adapters"

EVIDENCE_TYPE_ADAPTERS: dict[str, str] = {
    "qasm_parse": "qasm",
    "qec_verifier_result": "qec",
    "simulation": "python",
    "ai_draft": "ai_formalization",
    "lean_proof": "lean",
    "coq_proof": "coq",
    "rocq_proof": "rocq",
    "isabelle_proof": "isabelle",
    "proof_assistant_proof": "lean",
    "sat_certificate": "sat_certificate",
    "smt_certificate": "smt",
    "qcec_result": "qcec",
    "human_review": "human_review",
    "bridge_verify": "bridge",
    "python_denotation_consistency_check": "bridge",
}


@dataclass
class EvidenceRunResult:
    evidence_id: str
    path: str
    command: str | None
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    skipped: bool = False
    skip_reason: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.skipped and self.exit_code == 0


def _allow_raw_commands() -> bool:
    return os.environ.get("QSPECBENCH_ALLOW_RAW_COMMANDS") == "1"


def _resolve_command(
    command: str,
    claim_dir: Path,
    artifact: Path | None,
    secondary: Path | None = None,
) -> list[str]:
    cmd = command
    uses_placeholders = "{path}" in command or "{path2}" in command
    if artifact:
        cmd = cmd.replace("{path}", str(artifact))
        if not uses_placeholders:
            rel = str(artifact.relative_to(claim_dir)) if artifact.is_relative_to(claim_dir) else str(artifact)
            cmd = cmd.replace(rel, str(artifact))
    if secondary:
        cmd = cmd.replace("{path2}", str(secondary))
        if not uses_placeholders:
            rel2 = (
                str(secondary.relative_to(claim_dir))
                if secondary.is_relative_to(claim_dir)
                else str(secondary)
            )
            cmd = cmd.replace(rel2, str(secondary))
    parts = shlex.split(cmd, posix=(sys.platform != "win32"))
    resolved: list[str] = []
    for part in parts:
        p = Path(part)
        if p.is_absolute():
            resolved.append(str(p))
        elif part.startswith("adapters/"):
            resolved.append(str((REPO_ROOT / part).resolve()))
        elif (claim_dir / part).exists():
            resolved.append(str((claim_dir / part).resolve()))
        else:
            resolved.append(part)
    return resolved


def _adapter_command(
    adapter_name: str,
    *,
    secondary: Path | None = None,
) -> str:
    script = ADAPTERS_ROOT / adapter_name / "parse_result.py"
    cmd = f"{sys.executable} {script} {{path}}"
    if secondary is not None:
        cmd = f"{cmd} {{path2}}"
    return cmd


def _default_adapter_command(
    evidence_type: str,
    artifact_path: Path,
    *,
    adapter_override: str | None = None,
    secondary: Path | None = None,
) -> str | None:
    adapter_name = adapter_override
    if adapter_name is None:
        if evidence_type == "simulation" and artifact_path.suffix.lower() == ".json":
            adapter_name = "dynamic_simulation"
        else:
            adapter_name = EVIDENCE_TYPE_ADAPTERS.get(evidence_type)
    if not adapter_name:
        return None
    return _adapter_command(adapter_name, secondary=secondary)


def _resolve_secondary_path(entry: dict, claim_dir: Path) -> Path | None:
    rel = entry.get("secondary_path")
    if not rel:
        return None
    return (claim_dir / rel).resolve()


def run_evidence_checks(claim_dir: Path, dry_run: bool = False) -> list[EvidenceRunResult]:
    claim_dir = claim_dir.resolve()
    spec = load_spec(claim_dir / "spec.yaml")
    results: list[EvidenceRunResult] = []

    for entry in spec.get("evidence", []):
        eid = entry.get("id", "?")
        rel_path = entry.get("path", "")
        artifact = (claim_dir / rel_path).resolve() if rel_path else None
        secondary = _resolve_secondary_path(entry, claim_dir)
        raw_command = entry.get("command")
        adapter_name = entry.get("adapter")
        etype = entry.get("type", "")

        command: str | None = None
        if adapter_name and artifact:
            command = _default_adapter_command(etype, artifact, adapter_override=adapter_name, secondary=secondary)
        elif not raw_command and artifact and entry.get("status") == "passing":
            command = _default_adapter_command(etype, artifact, secondary=secondary)
        elif raw_command:
            if not _allow_raw_commands():
                results.append(
                    EvidenceRunResult(
                        evidence_id=eid,
                        path=rel_path,
                        command=raw_command,
                        exit_code=1,
                        errors=[
                            "raw command: disallowed; use adapter: field or set "
                            "QSPECBENCH_ALLOW_RAW_COMMANDS=1 (maintainer only)"
                        ],
                    )
                )
                continue
            command = raw_command

        if not command:
            results.append(
                EvidenceRunResult(
                    evidence_id=eid,
                    path=rel_path,
                    command=None,
                    exit_code=None,
                    skipped=True,
                    skip_reason="no adapter or command declared",
                )
            )
            continue

        if entry.get("status") in ("draft", "not_checked"):
            results.append(
                EvidenceRunResult(
                    evidence_id=eid,
                    path=rel_path,
                    command=command,
                    exit_code=None,
                    skipped=True,
                    skip_reason=f"status is {entry.get('status')}",
                )
            )
            continue

        cmd = _resolve_command(command, claim_dir, artifact, secondary)
        if dry_run:
            results.append(
                EvidenceRunResult(
                    evidence_id=eid,
                    path=rel_path,
                    command=" ".join(cmd),
                    exit_code=0,
                    stdout="(dry run)",
                )
            )
            continue

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32" and cmd[0].endswith(".sh")),
            )
            result = EvidenceRunResult(
                evidence_id=eid,
                path=rel_path,
                command=" ".join(cmd),
                exit_code=proc.returncode,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
            )
            if proc.returncode != 0:
                result.errors.append(f"command failed with exit {proc.returncode}")
            else:
                try:
                    payload = json.loads(proc.stdout.splitlines()[-1]) if proc.stdout.strip() else {}
                    if payload.get("skipped"):
                        result.skipped = True
                        result.skip_reason = payload.get("notes") or payload.get("skip_reason") or "adapter skipped"
                        result.exit_code = 0
                    elif payload.get("ok") is False:
                        detail = payload.get("errors")
                        if isinstance(detail, list) and detail:
                            result.errors.extend(str(e) for e in detail)
                        else:
                            result.errors.append(payload.get("error", "adapter reported ok=false"))
                        result.exit_code = 1
                except json.JSONDecodeError:
                    pass
            results.append(result)
        except OSError as exc:
            results.append(
                EvidenceRunResult(
                    evidence_id=eid,
                    path=rel_path,
                    command=" ".join(cmd),
                    exit_code=1,
                    errors=[str(exc)],
                )
            )
    return results
