"""Generic typed-adapter conformance harness.

The harness covers identity, hashes, obligation subset, trust ceiling, malformed output,
timeout, missing executable, hostile paths, and repository-wide shipping-adapter integrity. It
never treats the descriptive ``checker`` field as an execution selector.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from qspecbench.adapter_protocol import validate_adapter_request, validate_adapter_result
from qspecbench.typed_adapter_registry import (
    TRUST_CLASS_RANK,
    TYPED_ADAPTERS,
    get_typed_adapter,
    proof_assistant_native_checked_is_kernel_subtype,
    validate_typed_adapter_identity,
)

TRUST_OVERCLAIM = "trust overclaim: result trust_class exceeds registry ceiling"
_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"
)


@dataclass(frozen=True)
class ConformanceCase:
    name: str
    request: dict[str, Any]
    result: dict[str, Any] | None = None
    expect_request_errors: tuple[str, ...] = ()
    expect_result_errors: tuple[str, ...] = ()


def _matches(errors: list[str], needles: tuple[str, ...]) -> bool:
    blob = " | ".join(errors)
    return all(needle in blob for needle in needles)


def evaluate_conformance_case(case: ConformanceCase, start: Path) -> list[str]:
    failures: list[str] = []
    request_errors = validate_adapter_request(case.request, start)
    identity_errors = validate_typed_adapter_identity(
        str(case.request.get("adapter_id") or ""),
        str(case.request.get("adapter_version") or ""),
        None,
    )
    request_errors.extend(identity_errors)

    if case.expect_request_errors:
        if not _matches(request_errors, case.expect_request_errors):
            failures.append(
                f"{case.name}: expected request errors {case.expect_request_errors}, "
                f"got {request_errors}"
            )
        return failures
    if request_errors:
        failures.append(f"{case.name}: unexpected request errors {request_errors}")
        return failures

    if case.result is None:
        failures.append(f"{case.name}: missing result payload")
        return failures

    result_errors = validate_adapter_result(case.result, start, request=case.request)
    result_errors.extend(trust_ceiling_errors(case.request, case.result))
    if case.expect_result_errors:
        if not _matches(result_errors, case.expect_result_errors):
            failures.append(
                f"{case.name}: expected result errors {case.expect_result_errors}, "
                f"got {result_errors}"
            )
        return failures
    if result_errors:
        failures.append(f"{case.name}: unexpected result errors {result_errors}")
    return failures


def trust_ceiling_errors(request: dict[str, Any], result: dict[str, Any]) -> list[str]:
    spec = get_typed_adapter(str(request.get("adapter_id") or ""))
    if spec is None:
        return [f"unknown typed adapter id {request.get('adapter_id')!r}"]
    claimed = str(result.get("trust_class") or "")
    ceiling = spec.trust_ceiling
    if claimed == ceiling:
        return []
    if proof_assistant_native_checked_is_kernel_subtype(claimed, ceiling):
        return []
    claimed_rank = TRUST_CLASS_RANK.get(claimed)
    ceiling_rank = TRUST_CLASS_RANK.get(ceiling)
    if claimed_rank is None:
        return [f"unknown result trust_class {claimed!r}"]
    if ceiling_rank is None:
        return [f"unknown registry trust ceiling {ceiling!r}"]
    if claimed_rank > ceiling_rank:
        return [f"{TRUST_OVERCLAIM} ({claimed} > {ceiling})"]
    return [f"adapter result trust_class {claimed!r} does not match registry {ceiling!r}"]


def hostile_path_errors(path: str) -> list[str]:
    errors: list[str] = []
    probe = Path(path)
    if probe.is_absolute() or ".." in probe.parts:
        errors.append(f"hostile adapter input path rejected: {path!r}")
    return errors


def missing_executable_errors(implementation: Path) -> list[str]:
    if implementation.is_file():
        return []
    return [f"adapter implementation missing: {implementation}"]


def malformed_output_errors(raw: str) -> list[str]:
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"malformed adapter output: {exc}"]
    return []


def timeout_errors(timed_out: bool, *, timeout_seconds: int) -> list[str]:
    if timed_out:
        return [f"adapter timed out after {timeout_seconds}s"]
    return []


def shipping_adapter_conformance_errors(repo_root: Path) -> list[str]:
    """Validate every built-in typed adapter and its repository layout fail-closed."""
    root = repo_root.resolve()
    adapters_root = (root / "adapters").resolve()
    errors: list[str] = []
    implementation_dirs: set[str] = set()

    for adapter_id, spec in sorted(TYPED_ADAPTERS.items()):
        if adapter_id != spec.adapter_id:
            errors.append(
                f"registry key {adapter_id!r} disagrees with spec id {spec.adapter_id!r}"
            )
        if not _SEMVER.fullmatch(spec.adapter_version):
            errors.append(f"{adapter_id}: adapter_version is not semantic-version shaped")
        if spec.trust_ceiling not in TRUST_CLASS_RANK:
            errors.append(f"{adapter_id}: unknown trust ceiling {spec.trust_ceiling!r}")
        if not spec.supported_evidence_types:
            errors.append(f"{adapter_id}: no supported evidence types")
        if spec.execution_kind != "repo_python":
            errors.append(f"{adapter_id}: built-in execution_kind must be 'repo_python'")
            continue

        implementation = (adapters_root / spec.implementation).resolve()
        try:
            rel = implementation.relative_to(adapters_root)
        except ValueError:
            errors.append(f"{adapter_id}: implementation escapes adapters root")
            continue
        if not implementation.is_file():
            errors.append(f"{adapter_id}: missing implementation {rel.as_posix()}")
            continue
        if implementation.suffix != ".py":
            errors.append(f"{adapter_id}: implementation is not Python: {rel.as_posix()}")
        implementation_dirs.add(rel.parts[0])

    manifest_dirs = {
        path.parent.name
        for path in adapters_root.glob("*/adapter.yaml")
        if path.parent.is_dir()
    }
    for directory in sorted(manifest_dirs):
        if directory not in implementation_dirs:
            errors.append(
                f"adapters/{directory}/adapter.yaml has no registered typed implementation"
            )
        manifest_path = adapters_root / directory / "adapter.yaml"
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"adapters/{directory}/adapter.yaml cannot be parsed: {exc}")
            continue
        if not isinstance(manifest, dict):
            errors.append(f"adapters/{directory}/adapter.yaml must contain a mapping")
            continue
        declared_id = manifest.get("adapter_id")
        if declared_id:
            typed = TYPED_ADAPTERS.get(str(declared_id))
            if typed is None:
                errors.append(
                    f"adapters/{directory}/adapter.yaml declares unknown "
                    f"adapter_id {declared_id!r}"
                )
            else:
                declared_version = manifest.get("adapter_version")
                if str(declared_version or "") != typed.adapter_version:
                    errors.append(
                        f"adapters/{directory}/adapter.yaml version {declared_version!r} "
                        f"does not match registry {typed.adapter_version!r}"
                    )
                normalized = typed.implementation.replace("\\", "/")
                if not normalized.startswith(f"{directory}/"):
                    errors.append(
                        f"adapters/{directory}/adapter.yaml id {declared_id!r} "
                        "resolves outside its directory"
                    )

    for directory in sorted(implementation_dirs - manifest_dirs):
        errors.append(f"registered adapter directory adapters/{directory}/ lacks adapter.yaml")

    return errors


Runner = Callable[[dict[str, Any]], dict[str, Any]]


STANDARD_CASES: tuple[str, ...] = (
    "identity",
    "hashes",
    "obligation_subset",
    "trust_ceiling",
    "malformed_output",
    "timeout",
    "missing_executable",
    "hostile_path",
    "unknown_id",
    "unknown_version",
    "trust_overclaim",
)
