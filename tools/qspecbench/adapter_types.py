"""Shared adapter request/result types (CLI adapters remain subprocess-first)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AdapterRequest:
    """Normalized adapter invocation."""

    path: Path
    path2: Path | None = None
    evidence_type: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Standard adapter outcome (JSON-serializable)."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    skipped: bool = False
    trust_level: str | None = None
    checker: str | None = None
    tool_version: str | None = None
    command: str | None = None
    input_hashes: dict[str, str] = field(default_factory=dict)
    output_hash: str | None = None
    notes: str | None = None
    adapter: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        # Drop empty optional containers for compact adapter stdout.
        if not payload["input_hashes"]:
            del payload["input_hashes"]
        if not payload["metadata"]:
            del payload["metadata"]
        if payload["notes"] is None:
            del payload["notes"]
        if payload["tool_version"] is None:
            del payload["tool_version"]
        if payload["command"] is None:
            del payload["command"]
        if payload["output_hash"] is None:
            del payload["output_hash"]
        if payload["checker"] is None:
            del payload["checker"]
        if payload["adapter"] is None:
            del payload["adapter"]
        if payload["trust_level"] is None:
            del payload["trust_level"]
        return payload


def result_from_legacy_dict(data: dict[str, Any], *, adapter: str | None = None) -> AdapterResult:
    """Adapt existing adapter JSON payloads into AdapterResult."""
    return AdapterResult(
        ok=bool(data.get("ok")),
        errors=[str(e) for e in (data.get("errors") or [])],
        skipped=bool(data.get("skipped")),
        trust_level=data.get("trust_level"),
        checker=data.get("checker"),
        tool_version=data.get("tool_version"),
        command=data.get("command"),
        input_hashes=dict(data.get("input_hashes") or {}),
        output_hash=data.get("output_hash"),
        notes=data.get("notes") or data.get("skip_reason"),
        adapter=data.get("adapter") or adapter,
        metadata={
            k: v
            for k, v in data.items()
            if k
            not in {
                "ok",
                "errors",
                "skipped",
                "trust_level",
                "checker",
                "tool_version",
                "command",
                "input_hashes",
                "output_hash",
                "notes",
                "skip_reason",
                "adapter",
            }
        },
    )
