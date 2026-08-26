"""Generate the interoperability matrix from the typed adapter registry and CI metadata."""

from __future__ import annotations

from qspecbench.typed_adapter_registry import TYPED_ADAPTERS

CONTROLLED_STATUSES = (
    "active_default_ci",
    "active_conditional_ci",
    "active_manual",
    "integration_scaffold",
    "planned",
    "deprecated",
)

# Workflow/registry truth. Conditional means the expensive lane is path/schedule scoped; it does
# not mean the pinned theorem has never passed.
ECOSYSTEM_ROWS: tuple[tuple[str, str, str, str], ...] = (
    (
        "Lean 4 / Mathlib",
        "active_default_ci",
        "current repo toolchain; historical evidence pinned per release",
        "kernel_checked theorems under declared axioms/semantics",
    ),
    (
        "MQT QCEC",
        "active_default_ci",
        "historical corpus pinned to recorded mqt.qcec version",
        "externally_trusted supporting equivalence; not semantic authority",
    ),
    (
        "Stim / PyMatching",
        "active_conditional_ci",
        "pinned extras in pyproject.toml",
        "simulation/decoder evidence only for declared code/noise/round universes",
    ),
    (
        "Qiskit Optimize1qGates",
        "active_manual",
        "provenance records package version; regeneration when installed",
        "independently_checkable compiler provenance; not a general Qiskit theorem",
    ),
    (
        "QBricks",
        "integration_scaffold",
        "external binary identity recorded when executed",
        "externally_trusted",
    ),
    (
        "ZX",
        "integration_scaffold",
        "checker/version recorded on certificates",
        "independently_checkable only to the exact certificate proposition",
    ),
    (
        "Coq",
        "active_manual",
        "opt-in local/custom-job",
        "second-kernel evidence only when actually compiled",
    ),
    (
        "Rocq",
        "integration_scaffold",
        "no default passing path",
        "not checked unless a concrete executable integration exists",
    ),
    (
        "Isabelle",
        "integration_scaffold",
        "no default passing path",
        "not checked unless a concrete executable integration exists",
    ),
    (
        "Lean-QEC",
        "active_conditional_ci",
        "adapter qspecbench.lean_qec.distance.v1 v2.0.0; exact upstream commit/toolchain/LFS objects pinned",
        "distance-only (BB90_dist_10). The pinned upstream-default path has demonstrated cold native kernel acceptance with no fallback; every release candidate must rerun the lane at its own exact SHA. Authorized fallback remains explicit and fail-closed if ever needed.",
    ),
    (
        "Lean-Quantum / Lean-QIT",
        "planned",
        "version-isolated theorem/certificate import first",
        "preserve upstream proposition, semantics, and toolchain",
    ),
)


def generate_interoperability_matrix() -> str:
    registered = ", ".join(sorted(TYPED_ADAPTERS))
    lines = [
        "# Interoperability and compatibility matrix",
        "",
        "> Do not edit manually. Regenerate from `qspecbench.interoperability`.",
        "",
        "This matrix distinguishes evidence paths that ship today from optional, planned, or",
        "disabled integrations. Presence in this table is not evidence of theorem correctness,",
        "independent review, or unmodified upstream reproduction.",
        "",
        "Controlled statuses: `active_default_ci`, `active_conditional_ci`, `active_manual`,",
        "`integration_scaffold`, `planned`, `deprecated`.",
        "",
        "| Ecosystem | Status | Version policy | Trust / scope |",
        "|---|---|---|---|",
    ]
    for name, status, version, trust in ECOSYSTEM_ROWS:
        if status not in CONTROLLED_STATUSES:
            raise ValueError(f"uncontrolled interoperability status {status!r}")
        lines.append(f"| {name} | `{status}` | {version} | {trust} |")
    lines.extend(
        [
            "",
            "## Registered typed adapters",
            "",
            registered,
            "",
            "## Compatibility doctrine",
            "",
            "1. Never silently upgrade a tool version recorded in historical evidence.",
            "2. A newer compatibility lane does not rewrite the evidence identity of an older release.",
            "3. Bind exact external repository commit/toolchain when importing formal results.",
            "4. Record proposition relation. An instance or weakening is not an equivalent substitute.",
            "5. A registered adapter has an explicit trust ceiling; no adapter may promote itself.",
            "6. Lean-QEC cold acceptance is exact-SHA evidence: a prior passing run never substitutes for rerunning a later release candidate.",
            "",
        ]
    )
    return "\n".join(lines)


def write_interoperability_matrix(out) -> None:
    out.write_text(generate_interoperability_matrix(), encoding="utf-8")
