"""Run declared evidence checks for a benchmark claim."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from qspecbench.schema import REPO_ROOT
from qspecbench.validate import load_spec

ADAPTERS_ROOT = REPO_ROOT / "adapters"


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
        if part.startswith("adapters/"):
            resolved.append(str((REPO_ROOT / part).resolve()))
        elif (claim_dir / part).exists():
            resolved.append(str((claim_dir / part).resolve()))
        else:
            resolved.append(part)
    return resolved


def _default_adapter_command(evidence_type: str, artifact_path: Path) -> str | None:
    mapping = {
        "qasm_parse": f"python {ADAPTERS_ROOT / 'qasm' / 'parse_result.py'}",
        "qec_verifier_result": f"python {ADAPTERS_ROOT / 'qec' / 'parse_result.py'}",
        "simulation": f"python {ADAPTERS_ROOT / 'python' / 'parse_result.py'}",
        "ai_draft": f"python {ADAPTERS_ROOT / 'ai_formalization' / 'parse_result.py'}",
        "lean_proof": f"python {ADAPTERS_ROOT / 'lean' / 'parse_result.py'}",
        "sat_certificate": f"python {ADAPTERS_ROOT / 'sat_certificate' / 'parse_result.py'}",
        "smt_certificate": f"python {ADAPTERS_ROOT / 'smt' / 'parse_result.py'}",
        "qcec_result": f"python {ADAPTERS_ROOT / 'qcec' / 'parse_result.py'}",
        "human_review": f"python {ADAPTERS_ROOT / 'human_review' / 'parse_result.py'}",
        "bridge_verify": f"python {ADAPTERS_ROOT / 'bridge' / 'parse_result.py'}",
    }
    template = mapping.get(evidence_type)
    if not template:
        return None
    return f"{template} {{path}}"


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
        command = entry.get("command")
        etype = entry.get("type", "")

        if not command and artifact and entry.get("status") == "passing":
            command = _default_adapter_command(etype, artifact)
            if command:
                command = command.replace("{path}", str(artifact))
                if secondary and etype == "qcec_result":
                    command = f"{command} {{path2}}"

        if not command:
            results.append(
                EvidenceRunResult(
                    evidence_id=eid,
                    path=rel_path,
                    command=None,
                    exit_code=None,
                    skipped=True,
                    skip_reason="no command declared",
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
                    if payload.get("ok") is False:
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
