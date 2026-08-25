"""Run declared evidence checks for a benchmark claim.

Execution routing is deliberately independent of the human-readable ``checker`` field.
A stable typed adapter id, when present, selects the implementation. Evidence types with one
ordinary repository-wide interpretation may use the typed default registry. Legacy directory
adapter names remain accepted only as a compatibility surface while specs migrate.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from qspecbench.adapter_registry import validate_adapter_name
from qspecbench.adapter_runtime import (
    AdapterRuntimeError,
    assurance_edge_for_evidence,
    build_adapter_request,
    normalize_adapter_result,
)
from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path
from qspecbench.evidence_adapter_bindings import bound_adapter_id
from qspecbench.evidence_sandbox import run_sandboxed, uses_evidence_sandbox
from qspecbench.evidence_schedule import (
    EvidenceClass,
    batches_by_class,
    max_workers_for,
    run_bounded,
    schedule_evidence,
)
from qspecbench.schema import REPO_ROOT
from qspecbench.typed_adapter_registry import default_typed_adapter, get_typed_adapter
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
    adapter_request: dict[str, Any] | None = None
    adapter_result: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not self.errors and not self.skipped and self.exit_code == 0


def _allow_raw_commands() -> bool:
    return os.environ.get("QSPECBENCH_ALLOW_RAW_COMMANDS") == "1"


def _raw_command_errors(claim_dir: Path) -> list[str]:
    """Fail-closed authorization for raw evidence commands (env alone is insufficient)."""
    errors: list[str] = []
    if os.environ.get("CI", "").strip() in {"1", "true", "TRUE", "yes"}:
        errors.append("raw command: disallowed in CI")
    if os.environ.get("QSPECBENCH_TRUSTED_LOCAL", "").strip() not in {"1", "true", "yes"}:
        errors.append(
            "raw command: requires QSPECBENCH_TRUSTED_LOCAL=1 and "
            "QSPECBENCH_ALLOW_RAW_COMMANDS=1 (maintainer escape hatch)"
        )
    if not _allow_raw_commands():
        errors.append(
            "raw command: disallowed; use adapter: field or set "
            "QSPECBENCH_ALLOW_RAW_COMMANDS=1 (maintainer only)"
        )
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            errors.append("raw command: requires a clean git working tree")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    _ = claim_dir
    return errors


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
            rel = (
                str(artifact.relative_to(claim_dir))
                if artifact.is_relative_to(claim_dir)
                else str(artifact)
            )
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
        else:
            try:
                candidate = resolve_claim_path(claim_dir, part)
            except ValueError:
                candidate = None
            if candidate is not None and candidate.exists():
                resolved.append(str(candidate.resolve()))
            elif (claim_dir / part).exists():
                escape = claim_path_escape_error(claim_dir, part)
                if escape:
                    raise ValueError(escape)
                resolved.append(str((claim_dir / part).resolve()))
            else:
                resolved.append(part)
    return resolved


def _adapter_command(
    adapter_name: str,
    *,
    evidence_type: str | None = None,
    secondary: Path | None = None,
) -> str:
    """Resolve a typed adapter id (preferred) or legacy directory adapter name.

    ``checker`` is intentionally absent from this function: prose metadata has no execution
    authority.
    """
    typed = get_typed_adapter(adapter_name)
    if typed is not None:
        if evidence_type is not None and evidence_type not in typed.supported_evidence_types:
            raise ValueError(
                f"typed adapter {adapter_name!r} does not support evidence type {evidence_type!r}"
            )
        script = ADAPTERS_ROOT / typed.implementation
    elif adapter_name.startswith("qspecbench."):
        raise ValueError(f"unknown typed adapter id {adapter_name!r}")
    else:
        errors = validate_adapter_name(adapter_name)
        if errors:
            raise ValueError("; ".join(errors))
        script = ADAPTERS_ROOT / adapter_name / "parse_result.py"

    if not script.is_file():
        raise ValueError(f"adapter implementation does not exist: {script.relative_to(REPO_ROOT)}")
    cmd = f"{sys.executable} {script} {{path}}"
    if secondary is not None:
        cmd = f"{cmd} {{path2}}"
    return cmd


def _default_adapter_id(evidence_type: str, artifact_path: Path) -> str | None:
    if evidence_type == "simulation":
        name = artifact_path.name
        if name.endswith(".result.json"):
            script = artifact_path.with_name(name[: -len(".result.json")] + ".py")
            if script.is_file():
                return "qspecbench.python.simulation.v1"
        if artifact_path.suffix.lower() == ".json":
            return "qspecbench.dynamic_simulation.v1"
    typed = default_typed_adapter(evidence_type)
    return typed.adapter_id if typed is not None else None


def _default_adapter_command(
    evidence_type: str,
    artifact_path: Path,
    *,
    adapter_override: str | None = None,
    secondary: Path | None = None,
) -> str | None:
    adapter_name = adapter_override or _default_adapter_id(evidence_type, artifact_path)
    if not adapter_name:
        return None
    return _adapter_command(
        adapter_name,
        evidence_type=evidence_type,
        secondary=secondary,
    )


def _resolve_secondary_path(entry: dict, claim_dir: Path) -> Path | None:
    rel = entry.get("secondary_path")
    if not rel:
        return None
    escape = claim_path_escape_error(claim_dir, rel)
    if escape:
        raise ValueError(escape)
    return resolve_claim_path(claim_dir, rel)


def _evidence_timeout(evidence_type: str, cmd: list[str]) -> int:
    cmd_text = " ".join(cmd)
    if (
        evidence_type == "lean_proof"
        or "adapters/lean" in cmd_text
        or "adapters\\lean" in cmd_text
    ):
        return 600
    if evidence_type == "coq_proof" or "adapters/coq" in cmd_text or "adapters\\coq" in cmd_text:
        return 300
    if evidence_type == "qcec_result" or "adapters/qcec" in cmd_text or "adapters\\qcec" in cmd_text:
        return 300
    if (
        evidence_type in {"smt_certificate", "sat_certificate"}
        or "adapters/smt" in cmd_text
        or "adapters\\smt" in cmd_text
        or "adapters/sat_certificate" in cmd_text
        or "adapters\\sat_certificate" in cmd_text
    ):
        return 120
    return 120


def _result_error(
    evidence_id: str,
    path: str,
    error: str,
    command: str | None = None,
) -> EvidenceRunResult:
    return EvidenceRunResult(
        evidence_id=evidence_id,
        path=path,
        command=command,
        exit_code=1,
        errors=[error],
    )


def _check_one_entry(entry: dict, claim_dir: Path, dry_run: bool) -> EvidenceRunResult:
    """Execute one evidence entry using graph/sidecar/default typed adapter identity."""
    eid = str(entry.get("id", "?"))
    rel_path = str(entry.get("path", ""))
    artifact: Path | None = None
    if rel_path:
        escape = claim_path_escape_error(claim_dir, rel_path)
        if escape:
            return _result_error(eid, rel_path, escape)
        artifact = resolve_claim_path(claim_dir, rel_path)

    try:
        secondary = _resolve_secondary_path(entry, claim_dir)
    except ValueError as exc:
        return _result_error(eid, rel_path, str(exc))

    raw_command = entry.get("command")
    try:
        explicit_adapter = bound_adapter_id(entry, claim_dir)
        assurance_edge = assurance_edge_for_evidence(claim_dir, eid)
    except (OSError, json.JSONDecodeError, ValueError, AdapterRuntimeError) as exc:
        return _result_error(eid, rel_path, f"typed adapter binding: {exc}")

    evidence_type = str(entry.get("type", ""))
    execution_adapter: str | None = None
    runtime_request: dict[str, Any] | None = None
    command: str | None = None

    if raw_command:
        if assurance_edge is not None:
            return _result_error(
                eid,
                rel_path,
                "assurance-edge evidence cannot execute an untyped raw command",
                str(raw_command),
            )
        if explicit_adapter is not None:
            return _result_error(
                eid,
                rel_path,
                "raw command cannot be combined with an explicit typed adapter",
                str(raw_command),
            )
        raw_errors = _raw_command_errors(claim_dir)
        if raw_errors:
            return EvidenceRunResult(
                evidence_id=eid,
                path=rel_path,
                command=str(raw_command),
                exit_code=1,
                errors=raw_errors + ["warning: raw commands are a maintainer escape hatch only"],
            )
        command = str(raw_command)
    else:
        execution_adapter = explicit_adapter
        if assurance_edge is not None:
            graph_adapter = assurance_edge.get("adapter_id")
            if not graph_adapter:
                return _result_error(
                    eid,
                    rel_path,
                    f"assurance edge {eid!r} must declare adapter_id",
                )
            if explicit_adapter is not None and explicit_adapter != graph_adapter:
                return _result_error(
                    eid,
                    rel_path,
                    f"typed sidecar/entry adapter {explicit_adapter!r} contradicts assurance edge "
                    f"adapter {graph_adapter!r}",
                )
            execution_adapter = str(graph_adapter)
        elif execution_adapter is None and artifact is not None and entry.get("status") == "passing":
            execution_adapter = _default_adapter_id(evidence_type, artifact)

        if execution_adapter is not None:
            try:
                runtime_request = build_adapter_request(
                    entry,
                    claim_dir,
                    adapter_id=str(execution_adapter),
                    artifact=artifact,
                    secondary=secondary,
                )
            except AdapterRuntimeError as exc:
                return _result_error(eid, rel_path, f"adapter request: {exc}")

        if execution_adapter and artifact:
            try:
                command = _default_adapter_command(
                    evidence_type,
                    artifact,
                    adapter_override=str(execution_adapter),
                    secondary=secondary,
                )
            except ValueError as exc:
                return _result_error(eid, rel_path, str(exc))

    if not command:
        return EvidenceRunResult(
            evidence_id=eid,
            path=rel_path,
            command=None,
            exit_code=None,
            skipped=True,
            skip_reason="no adapter or command declared",
            adapter_request=runtime_request,
        )

    if entry.get("status") in ("draft", "not_checked"):
        return EvidenceRunResult(
            evidence_id=eid,
            path=rel_path,
            command=command,
            exit_code=None,
            skipped=True,
            skip_reason=f"status is {entry.get('status')}",
            adapter_request=runtime_request,
        )

    try:
        cmd = _resolve_command(command, claim_dir, artifact, secondary)
    except ValueError as exc:
        return _result_error(eid, rel_path, str(exc), command)

    if dry_run:
        return EvidenceRunResult(
            evidence_id=eid,
            path=rel_path,
            command=" ".join(cmd),
            exit_code=0,
            stdout="(dry run)",
            adapter_request=runtime_request,
        )

    try:
        timeout = _evidence_timeout(evidence_type, cmd)
        if uses_evidence_sandbox(evidence_type):
            proc = run_sandboxed(cmd, claim_dir=claim_dir, timeout=timeout)
        else:
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32" and cmd[0].endswith(".sh")),
                timeout=timeout,
            )
        result = EvidenceRunResult(
            evidence_id=eid,
            path=rel_path,
            command=" ".join(cmd),
            exit_code=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            adapter_request=runtime_request,
        )
        if proc.returncode != 0:
            result.errors.append(f"command failed with exit {proc.returncode}")
            return result

        try:
            payload = json.loads(proc.stdout.splitlines()[-1]) if proc.stdout.strip() else {}
        except json.JSONDecodeError as exc:
            result.errors.append(f"adapter stdout is not valid JSON: {exc}")
            result.exit_code = 1
            return result

        if runtime_request is not None:
            try:
                typed_result = normalize_adapter_result(
                    payload,
                    claim_dir,
                    request=runtime_request,
                )
            except AdapterRuntimeError as exc:
                result.errors.append(f"adapter result: {exc}")
                result.exit_code = 1
                return result
            result.adapter_result = typed_result
            typed_status = typed_result.get("status")
            if typed_status == "not_checked":
                result.skipped = True
                result.skip_reason = (
                    payload.get("notes") or payload.get("skip_reason") or "adapter skipped"
                )
                result.exit_code = 0
            elif typed_status != "passing":
                result.errors.append(f"typed adapter result status is {typed_status!r}")
                result.exit_code = 1
            return result

        if payload.get("skipped"):
            result.skipped = True
            result.skip_reason = payload.get("notes") or payload.get("skip_reason") or "adapter skipped"
            result.exit_code = 0
        elif payload.get("ok") is False:
            detail = payload.get("errors")
            if isinstance(detail, list) and detail:
                result.errors.extend(str(item) for item in detail)
            else:
                result.errors.append(str(payload.get("error", "adapter reported ok=false")))
            result.exit_code = 1
        return result
    except subprocess.TimeoutExpired:
        timeout = _evidence_timeout(evidence_type, cmd)
        return _result_error(eid, rel_path, f"command timed out after {timeout}s", " ".join(cmd))
    except (ValueError, OSError) as exc:
        return _result_error(eid, rel_path, str(exc), " ".join(cmd))


def run_evidence_checks(claim_dir: Path, dry_run: bool = False) -> list[EvidenceRunResult]:
    """Run evidence in class-major bounded batches with deterministic output ordering."""
    claim_dir = claim_dir.resolve()
    spec = load_spec(claim_dir / "spec.yaml")
    evidence_entries = list(spec.get("evidence", []) or [])
    scheduled = schedule_evidence(evidence_entries)
    by_id = {str(entry.get("id")): entry for entry in evidence_entries}

    ordered_items = [item for item in scheduled if item.evidence_id in by_id]
    seen = {item.evidence_id for item in ordered_items}
    orphan_entries: list[dict] = []
    for entry in evidence_entries:
        eid = str(entry.get("id"))
        if eid not in seen:
            orphan_entries.append(entry)
            seen.add(eid)

    results: list[EvidenceRunResult] = []
    for evidence_class, batch_items in batches_by_class(ordered_items):
        batch_entries = [by_id[item.evidence_id] for item in batch_items]
        workers = max_workers_for(evidence_class)
        if evidence_class == EvidenceClass.LEAN:
            workers = 1
        batch_results = run_bounded(
            batch_entries,
            lambda entry, _cd=claim_dir, _dr=dry_run: _check_one_entry(entry, _cd, _dr),
            max_workers=workers,
        )
        results.extend(item for item in batch_results if isinstance(item, EvidenceRunResult))

    for entry in orphan_entries:
        results.append(_check_one_entry(entry, claim_dir, dry_run))
    return results
