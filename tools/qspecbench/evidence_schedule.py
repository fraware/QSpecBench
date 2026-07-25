"""Evidence scheduling: classify, bound concurrency, deterministic order."""

from __future__ import annotations

import concurrent.futures
import os
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


class EvidenceClass(str, Enum):
    LIGHTWEIGHT = "lightweight"
    PYTHON = "python"
    LEAN = "lean"
    QCEC = "qcec"
    SMT = "smt"
    EXTERNAL = "external"


# Deterministic class order for scheduling.
CLASS_ORDER = (
    EvidenceClass.LIGHTWEIGHT,
    EvidenceClass.PYTHON,
    EvidenceClass.LEAN,
    EvidenceClass.QCEC,
    EvidenceClass.SMT,
    EvidenceClass.EXTERNAL,
)

# Evidence type → class.
EVIDENCE_TYPE_CLASS: dict[str, EvidenceClass] = {
    "qasm_parse": EvidenceClass.LIGHTWEIGHT,
    "human_review": EvidenceClass.LIGHTWEIGHT,
    "matrix_certificate": EvidenceClass.LIGHTWEIGHT,
    "sat_certificate": EvidenceClass.LIGHTWEIGHT,
    "internal_denotation_consistency": EvidenceClass.PYTHON,
    "python_denotation_consistency_check": EvidenceClass.PYTHON,
    "bridge_verify": EvidenceClass.PYTHON,
    "simulation": EvidenceClass.PYTHON,
    "lean_proof": EvidenceClass.LEAN,
    "coq_proof": EvidenceClass.LEAN,
    "rocq_proof": EvidenceClass.LEAN,
    "isabelle_proof": EvidenceClass.LEAN,
    "proof_assistant_proof": EvidenceClass.LEAN,
    "qcec_result": EvidenceClass.QCEC,
    "smt_certificate": EvidenceClass.SMT,
    "qec_verifier_result": EvidenceClass.EXTERNAL,
    "ai_draft": EvidenceClass.EXTERNAL,
}


def classify_evidence_type(evidence_type: str) -> EvidenceClass:
    return EVIDENCE_TYPE_CLASS.get(evidence_type, EvidenceClass.EXTERNAL)


def max_workers_for(cls: EvidenceClass) -> int:
    if cls == EvidenceClass.LIGHTWEIGHT:
        raw = os.environ.get("QSPECBENCH_LIGHTWEIGHT_WORKERS", "4")
        return max(1, int(raw))
    if cls == EvidenceClass.PYTHON:
        raw = os.environ.get("QSPECBENCH_PYTHON_WORKERS", "2")
        return max(1, int(raw))
    # Lean serialized; QCEC/SMT/external limited.
    if cls in {EvidenceClass.QCEC, EvidenceClass.SMT}:
        return 1
    return 1


@dataclass(frozen=True)
class ScheduledItem:
    evidence_id: str
    evidence_type: str
    evidence_class: EvidenceClass
    index: int  # original order for stable tie-break


def schedule_evidence(entries: Iterable[dict]) -> list[ScheduledItem]:
    items: list[ScheduledItem] = []
    for idx, entry in enumerate(entries):
        etype = str(entry.get("type") or "")
        items.append(
            ScheduledItem(
                evidence_id=str(entry.get("id") or f"idx{idx}"),
                evidence_type=etype,
                evidence_class=classify_evidence_type(etype),
                index=idx,
            )
        )
    class_rank = {c: i for i, c in enumerate(CLASS_ORDER)}
    items.sort(key=lambda it: (class_rank[it.evidence_class], it.index))
    return items


def batches_by_class(
    scheduled: list[ScheduledItem],
) -> list[tuple[EvidenceClass, list[ScheduledItem]]]:
    """Group scheduled items into class-major batches (deterministic CLASS_ORDER)."""
    buckets: dict[EvidenceClass, list[ScheduledItem]] = {c: [] for c in CLASS_ORDER}
    for item in scheduled:
        buckets.setdefault(item.evidence_class, []).append(item)
    return [(cls, buckets[cls]) for cls in CLASS_ORDER if buckets.get(cls)]


def run_bounded(
    items: list[T],
    worker: Callable[[T], object],
    *,
    max_workers: int,
    timeout_s: float | None = None,
) -> list[object]:
    """Run workers with a hard concurrency bound. Fail-closed on timeout."""
    if max_workers <= 1 or len(items) <= 1:
        results: list[object] = []
        for item in items:
            results.append(worker(item))
        return results
    results_map: dict[int, object] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(worker, item): i for i, item in enumerate(items)}
        try:
            for fut in concurrent.futures.as_completed(futures, timeout=timeout_s):
                idx = futures[fut]
                results_map[idx] = fut.result(timeout=0)
        except concurrent.futures.TimeoutError as exc:
            for fut in futures:
                fut.cancel()
            raise TimeoutError(
                f"evidence schedule exceeded timeout ({timeout_s}s); fail-closed"
            ) from exc
    return [results_map[i] for i in range(len(items))]
