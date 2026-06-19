"""Pydantic models for trust-boundary pre-checks before jsonschema validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


EvidenceStatus = Literal["passing", "failing", "partial", "not_checked", "draft"]
TrustLevel = Literal[
    "checked",
    "independently_checkable",
    "externally_trusted",
    "heuristic",
    "untrusted",
]
Maturity = Literal["seed", "usable", "reference", "deprecated"]


class TrustBoundary(BaseModel):
    checked_by: list[str] = Field(default_factory=list)
    trusted_kernels: list[str] = Field(default_factory=list)
    trusted_external_tools: list[str] = Field(default_factory=list)
    untrusted_components: list[str] = Field(default_factory=list)
    assumptions_not_checked: list[str] = Field(default_factory=list)


class EvidenceEntry(BaseModel):
    id: str
    type: str
    path: str
    checker: str
    status: EvidenceStatus
    command: str | None = None
    secondary_path: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def evidence_rules(self) -> EvidenceEntry:
        if self.status == "passing" and not self.checker.strip():
            raise ValueError("passing evidence requires a checker")
        if self.type == "ai_draft" and self.status == "passing":
            raise ValueError("ai_draft evidence cannot be passing")
        return self


class StatusBlock(BaseModel):
    informal_claim: Literal["missing", "draft", "complete"]
    machine_spec: Literal["missing", "draft", "complete"]
    artifacts: Literal["missing", "partial", "complete"]
    evidence: Literal["missing", "partial", "complete"]
    ci: Literal["not_applicable", "failing", "passing"]
    maturity: Maturity

    @model_validator(mode="after")
    def reference_requires_passing_ci(self) -> StatusBlock:
        if self.maturity == "reference" and self.ci != "passing":
            raise ValueError("reference maturity requires ci: passing")
        return self


class SpecTrustSlice(BaseModel):
    """Subset of spec fields validated before jsonschema."""

    trust_boundary: TrustBoundary
    evidence: list[EvidenceEntry] = Field(default_factory=list)
    status: StatusBlock

    def pydantic_errors(self) -> list[str]:
        errors: list[str] = []
        if self.status.maturity == "reference":
            checked = {
                e.type
                for e in self.evidence
                if e.status == "passing" and e.type in {"lean_proof", "smt_certificate", "sat_certificate"}
            }
            if not checked:
                errors.append("reference maturity requires at least one passing checked evidence entry")
        return errors


def validate_spec_trust_slice(spec: dict) -> list[str]:
    """Return pydantic validation errors for trust-related spec fields."""
    try:
        slice_ = SpecTrustSlice.model_validate(
            {
                "trust_boundary": spec.get("trust_boundary", {}),
                "evidence": spec.get("evidence", []),
                "status": spec.get("status", {}),
            }
        )
    except Exception as exc:
        return [f"pydantic trust slice: {exc}"]
    return slice_.pydantic_errors()
