"""Markdown dashboard generation."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from qspecbench import CORPUS_VERSION, RELEASE_TAG, SCHEMA_VERSION, TOOLING_VERSION
from qspecbench.models import ALL_REFERENCE_LEVELS, REFERENCE_CLAIM_LEVEL
from qspecbench.status import collect_statuses
from qspecbench.trust import CHECKED_EVIDENCE_TYPES

REPO_ROOT = Path(__file__).resolve().parents[2]
COQ_SMOKE_V = (
    REPO_ROOT
    / "benchmarks/equivalence/cnot_self_inverse_cancellation/evidence/cnot_coq_smoke.v"
)


def _coq_smoke_status() -> str:
    """Return passing | failed | unknown for default-CI Coq smoke compile."""
    if os.environ.get("QSPECBENCH_COQ_SMOKE_CI", "").lower() in {"1", "true", "pass", "passed"}:
        return "passing"
    coqc = shutil.which("coqc")
    if not coqc or not COQ_SMOKE_V.is_file():
        return "unknown"
    try:
        subprocess.run(
            [coqc, str(COQ_SMOKE_V.name)],
            cwd=COQ_SMOKE_V.parent,
            check=True,
            capture_output=True,
        )
        return "passing"
    except (subprocess.CalledProcessError, OSError):
        return "failed"


def _coq_dashboard_lines() -> list[str]:
    if _coq_smoke_status() == "passing":
        return [
            "- **Coq smoke (`cnot_coq_smoke.v`):** 1 (passing in default CI)",
            "- **Coq/Rocq/Isabelle full adapter:** optional job only "
            "(`QSPECBENCH_COQ=1`; see `adapters/coq/README.md`)",
        ]
    return [
        "- **Coq/Rocq/Isabelle second-assistant evidence:** excluded from default maturity "
        "counts until optional CI job passes (`QSPECBENCH_COQ=1`; see `adapters/coq/README.md`). "
        "`coq_smoke` compiles `cnot_coq_smoke.v` on every push when `coqc` is installed.",
    ]


def _has_checked_evidence(spec: dict[str, Any]) -> bool:
    return any(
        e.get("status") == "passing" and e.get("type") in CHECKED_EVIDENCE_TYPES
        for e in spec.get("evidence", [])
    )


def _headline_checked(spec: dict[str, Any]) -> bool:
    """A headline claim counts as checked only for reference_claim or an explicit checked status."""
    if spec.get("status", {}).get("maturity") == REFERENCE_CLAIM_LEVEL:
        return True
    return (spec.get("headline_claim_status") or {}).get("status") == "checked"


def _has_unchecked_headline_assumptions(spec: dict[str, Any]) -> bool:
    if _headline_checked(spec):
        return False
    proved = spec.get("proved_scope") or {}
    unproved = proved.get("unproved_obligations") or []
    if unproved:
        return True
    headline = spec.get("headline_claim_status") or {}
    return headline.get("status") in {"unproved", "partially_checked"}


def _has_ai_draft(spec: dict[str, Any]) -> bool:
    return any(e.get("type") == "ai_draft" for e in spec.get("evidence", []))


def _has_approximate(spec: dict[str, Any]) -> bool:
    spec_block = spec.get("specification", {})
    return spec_block.get("mode") == "approximate" or spec_block.get("approximation", {}).get("enabled")


def _has_resource_contract(spec: dict[str, Any]) -> bool:
    return spec.get("specification", {}).get("resources", {}).get("enabled", False)


def _trust_level_for_type(spec: dict[str, Any], evidence_type: str) -> str | None:
    for entry in spec.get("acceptable_evidence", []):
        if entry.get("type") == evidence_type:
            return entry.get("trust_level")
    return None


def _count_passing_trust_levels(specs: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for spec in specs:
        for ev in spec.get("evidence", []):
            if ev.get("status") != "passing":
                continue
            level = _trust_level_for_type(spec, ev.get("type", ""))
            if level:
                counts[level] += 1
    return counts


def _load_bridge_claimed_link(claim_dir: Path, spec: dict[str, Any]) -> str | None:
    inline = spec.get("semantic_bridge")
    if isinstance(inline, dict):
        return inline.get("claimed_link")
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        try:
            payload = json.loads(bridge_path.read_text(encoding="utf-8"))
            return payload.get("claimed_link")
        except json.JSONDecodeError:
            return None
    return None


def _bridge_link_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        claim_dir = row.get("claim_dir") or Path(row.get("path", ""))
        link = _load_bridge_claimed_link(claim_dir, row["spec"])
        if link:
            counts[link] += 1
    return counts


def _reference_coverage_by_track(rows: list[dict[str, Any]]) -> dict[str, int]:
    refs = Counter(r["track"] for r in rows if r["maturity"] in ALL_REFERENCE_LEVELS)
    return dict(sorted(refs.items()))


def zero_evidence_count(root: Path) -> int:
    rows = collect_statuses(root)
    return sum(1 for r in rows if not r["spec"].get("evidence"))


def _count_qec_certificate_levels(rows: list[dict[str, Any]]) -> tuple[int, int]:
    small = 0
    external = 0
    for row in rows:
        if row.get("track") != "qec":
            continue
        scope = row["spec"].get("qec_claim_scope") or {}
        level = scope.get("qec_certificate_level")
        if level == "qec_small_code_checked":
            small += 1
        elif level == "qec_external_certificate_checked":
            external += 1
    return small, external


def collect_summary_metrics(root: Path) -> dict[str, int]:
    """Single source of truth for dashboard and README status sync."""
    rows = collect_statuses(root)
    specs = [r["spec"] for r in rows]
    bridge_links = _bridge_link_counts(rows)
    by_maturity = Counter(r["maturity"] for r in rows)
    ref_levels = sum(by_maturity.get(m, 0) for m in ALL_REFERENCE_LEVELS)
    qec_small, qec_external = _count_qec_certificate_levels(rows)
    return {
        "total_benchmarks": len(rows),
        "reference_scaffolds_any_level": ref_levels,
        "reference_claim": by_maturity.get(REFERENCE_CLAIM_LEVEL, 0),
        "headline_checked": sum(1 for s in specs if _headline_checked(s)),
        "with_checked_evidence": sum(1 for s in specs if _has_checked_evidence(s)),
        "manifest_checked_theorem_binding": bridge_links.get("manifest_checked_theorem_binding", 0),
        "python_denotation_consistency": bridge_links.get("python_denotation_consistency", 0),
        "kernel_checked_codegen_trace": bridge_links.get("kernel_checked_codegen_trace", 0),
        "kernel_checked_artifact_semantics": bridge_links.get("kernel_checked_artifact_semantics", 0),
        "qec_small_code_checked": qec_small,
        "qec_external_certificate_checked": qec_external,
        "coq_smoke_ci": 1 if _coq_smoke_status() == "passing" else 0,
    }


def generate_dashboard(root: Path) -> str:
    rows = collect_statuses(root)
    specs = [r["spec"] for r in rows]

    by_track = Counter(r["track"] for r in rows)
    by_maturity = Counter(r["maturity"] for r in rows)
    checked = sum(1 for s in specs if _has_checked_evidence(s))
    headline_checked = sum(1 for s in specs if _headline_checked(s))
    scaffold_only = sum(
        1 for s in specs if _has_checked_evidence(s) and not _headline_checked(s)
    )
    unchecked_headline = sum(1 for s in specs if _has_unchecked_headline_assumptions(s))
    partial = sum(1 for s in specs if s.get("evidence") and not _has_checked_evidence(s))
    no_ev = sum(1 for s in specs if not s.get("evidence"))
    ai_draft = sum(1 for s in specs if _has_ai_draft(s))
    approx = sum(1 for s in specs if _has_approximate(s))
    qec = sum(1 for s in specs if s.get("track") == "qec")
    resources = sum(1 for s in specs if _has_resource_contract(s))
    trust_levels = _count_passing_trust_levels(specs)
    bridge_links = _bridge_link_counts(rows)
    manifest_bridges = bridge_links.get("manifest_checked_theorem_binding", 0)
    python_bridges = bridge_links.get("python_denotation_consistency", 0)
    kernel_codegen = bridge_links.get("kernel_checked_codegen_trace", 0)
    kernel_semantics = bridge_links.get("kernel_checked_artifact_semantics", 0)
    documented_bridges = bridge_links.get("documented_not_proved", 0)
    ref_by_track = _reference_coverage_by_track(rows)
    qec_small, qec_external = _count_qec_certificate_levels(rows)

    lines = [
        "# QSpecBench Dashboard",
        "",
        "Auto-generated benchmark status overview.",
        "",
        "Evidence headline note: most reference-scaffold benchmarks demonstrate the QSpecBench "
        "evidence format and trust-boundary discipline; a checked headline claim is reserved for "
        "`reference_claim` benchmarks whose full informal claim is proved.",
        "",
        "## Versions",
        "",
        f"- **Schema:** {SCHEMA_VERSION}",
        f"- **Tooling:** {TOOLING_VERSION}",
        f"- **Corpus:** {CORPUS_VERSION}",
        f"- **Release tag:** {RELEASE_TAG}",
        "",
        "## Summary",
        "",
        f"- **Total benchmarks:** {len(rows)}",
        "- **By track:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_track.items())),
        "- **By maturity:** " + ", ".join(f"{k}: {v}" for k, v in sorted(by_maturity.items())),
        f"- **With any checked evidence:** {checked}",
        f"- **With headline claim checked (reference_claim or checked headline):** {headline_checked}",
        f"- **With scaffold-only checked evidence:** {scaffold_only}",
        f"- **With unchecked headline assumptions:** {unchecked_headline}",
        f"- **With partial (non-checked) evidence only:** {partial}",
        f"- **With no evidence:** {no_ev}",
        f"- **With AI draft evidence:** {ai_draft}",
        f"- **With approximate specifications:** {approx}",
        f"- **QEC claims:** {qec}",
        f"- **QEC small-code certificate level (`qec_small_code_checked`):** {qec_small}",
        f"- **QEC external certificate level (`qec_external_certificate_checked`):** {qec_external}",
        f"- **With resource contracts:** {resources}",
        f"- **Manifest-checked theorem bindings:** {manifest_bridges}",
        f"- **Python denotation consistency checks:** {python_bridges}",
        f"- **Kernel-checked codegen-trace bridges:** {kernel_codegen}",
        f"- **Kernel-checked artifact-semantics bridges (legacy label):** {kernel_semantics}",
        f"- **Documented (not proved) bridges:** {documented_bridges}",
    ]
    lines.extend(_coq_dashboard_lines())
    lines.extend(
        [
            "",
            "### Passing evidence by trust level",
            "",
        ]
    )
    for level in ("checked", "independently_checkable", "externally_trusted", "heuristic"):
        lines.append(f"- **{level}:** {trust_levels.get(level, 0)}")
    lines.extend(
        [
            "",
            "### Reference-scaffold coverage by track",
            "",
        ]
    )
    if ref_by_track:
        for track, count in ref_by_track.items():
            lines.append(f"- **{track}:** {count}")
    else:
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "## Benchmarks",
            "",
            "| ID | Track | Claim type | Difficulty | Maturity | Evidence | CI | Trust summary |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in sorted(rows, key=lambda r: (r["track"], r["id"])):
        lines.append(
            f"| {row['id']} | {row['track']} | {row['claim_type']} | {row['difficulty']} "
            f"| {row['maturity']} | {row['evidence']} | {row['ci']} | {row['trust']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_dashboard(root: Path, out_path: Path) -> None:
    content = generate_dashboard(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
