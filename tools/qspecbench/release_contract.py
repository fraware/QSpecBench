"""Machine-enforced release-corpus and reference-suite policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

DEFAULT_CONTRACT = Path("docs/release_v1_contract.yaml")
DEFAULT_SCHEMA = Path("schema/release_contract.schema.json")
REQUIRED_CAPABILITIES = frozenset(
    {
        "compiler_transformation_equivalence",
        "arbitrary_input_dynamic_protocol",
        "operator_level_hamiltonian_approximation",
        "meaningful_qec_assurance",
        "externally_adjudicated_ai_formalization",
    }
)


@dataclass(frozen=True)
class BenchmarkRecord:
    """Minimal release-policy view of a benchmark package."""

    benchmark_id: str
    track: str
    maturity: str
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class ReleaseContractReport:
    """Result of checking a release contract against a repository tree."""

    release_id: str
    corpus: tuple[BenchmarkRecord, ...]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def _yaml_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data


def _schema_sort_key(error: Any) -> tuple[str, ...]:
    return tuple(str(part) for part in error.absolute_path)


def _schema_errors(contract: dict[str, Any], schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(contract), key=_schema_sort_key):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"release contract schema: {location}: {error.message}")
    return errors


def load_benchmarks(root: Path) -> dict[str, BenchmarkRecord]:
    """Load benchmark specs and reject duplicate ids."""
    records: dict[str, BenchmarkRecord] = {}
    for spec_path in sorted(root.rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        data = _yaml_mapping(spec_path)
        status = data.get("status")
        values = (
            data.get("id"),
            data.get("track"),
            status.get("maturity") if isinstance(status, dict) else None,
        )
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError(f"{spec_path}: id, track, and status.maturity must be strings")
        benchmark_id, track, maturity = values
        assert isinstance(benchmark_id, str)
        assert isinstance(track, str)
        assert isinstance(maturity, str)
        if benchmark_id in records:
            raise ValueError(f"duplicate benchmark id {benchmark_id!r}")
        records[benchmark_id] = BenchmarkRecord(
            benchmark_id=benchmark_id,
            track=track,
            maturity=maturity,
            path=spec_path.parent,
            data=data,
        )
    return records


def select_release_corpus(
    contract: dict[str, Any], records: dict[str, BenchmarkRecord]
) -> tuple[BenchmarkRecord, ...]:
    """Resolve maturity-selected packages plus explicit overrides."""
    policy = contract["release_corpus"]
    maturities = set(policy["maturity_selectors"])
    selected = {
        benchmark_id for benchmark_id, record in records.items() if record.maturity in maturities
    }
    selected.update(policy["include_benchmark_ids"])
    selected.difference_update(policy["exclude_benchmark_ids"])
    return tuple(records[item] for item in sorted(selected) if item in records)


def _review_errors(record: BenchmarkRecord, required: int, distinct: bool) -> list[str]:
    status = record.data.get("status", {})
    reviews = status.get("reviews") if isinstance(status, dict) else None
    if not isinstance(reviews, dict):
        return [f"{record.benchmark_id}: missing status.reviews"]
    approved = []
    for name in ("formal_evidence_review", "domain_semantics_review"):
        review = reviews.get(name)
        if isinstance(review, dict) and review.get("status") == "approved":
            approved.append(review)
    if len(approved) < required:
        return [
            f"{record.benchmark_id}: requires {required} approved reviews; found {len(approved)}"
        ]
    errors = []
    reviewers = [review.get("reviewer") for review in approved]
    if any(not isinstance(item, str) or not item.strip() for item in reviewers):
        errors.append(f"{record.benchmark_id}: every approved review must identify a reviewer")
    elif distinct and len(set(reviewers)) != len(reviewers):
        errors.append(f"{record.benchmark_id}: approved reviews must have distinct reviewers")
    for review in approved:
        if not review.get("review_artifact_path") or not review.get("review_artifact_sha256"):
            errors.append(f"{record.benchmark_id}: approved review must bind artifact path and digest")
    return errors


def validate_release_contract(
    repo_root: Path,
    *,
    strict_qualification: bool = False,
) -> ReleaseContractReport:
    """Validate release structure; optionally enforce fail-closed v1 qualification."""
    contract = _yaml_mapping(repo_root / DEFAULT_CONTRACT)
    errors = _schema_errors(contract, repo_root / DEFAULT_SCHEMA)
    release_id = str(contract.get("release_id", "<invalid>"))
    if errors:
        return ReleaseContractReport(release_id, (), tuple(errors))

    records = load_benchmarks(repo_root / "benchmarks")
    policy = contract["release_corpus"]
    include_ids = set(policy["include_benchmark_ids"])
    exclude_ids = set(policy["exclude_benchmark_ids"])
    overlap = include_ids & exclude_ids
    if overlap:
        errors.append("ids both included and excluded: " + ", ".join(sorted(overlap)))
    unknown = (include_ids | exclude_ids) - records.keys()
    if unknown:
        errors.append("unknown benchmark override ids: " + ", ".join(sorted(unknown)))

    corpus = select_release_corpus(contract, records)
    if policy["require_nonempty"] and not corpus:
        errors.append("release corpus is empty; qualification cannot be vacuous")

    capabilities = contract["reference_suite"]["required_capabilities"]
    missing = REQUIRED_CAPABILITIES - capabilities.keys()
    extra = capabilities.keys() - REQUIRED_CAPABILITIES
    if missing:
        errors.append("missing Level-C capabilities: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unrecognized Level-C capabilities: " + ", ".join(sorted(extra)))

    if not strict_qualification:
        return ReleaseContractReport(release_id, corpus, tuple(errors))

    reference_maturities = set(contract["promotion"]["reference_maturities"])
    review_count = contract["promotion"]["independent_review_attestations_required"]
    distinct = contract["promotion"]["require_distinct_reviewers"]
    corpus_ids = {record.benchmark_id for record in corpus}

    for record in corpus:
        identity = record.data.get("claim_identity")
        proposition_id = identity.get("proposition_id") if isinstance(identity, dict) else None
        if not isinstance(proposition_id, str) or not proposition_id.strip():
            errors.append(f"{record.benchmark_id}: missing claim_identity.proposition_id")
        graph_path = record.path / "assurance_graph.yaml"
        if policy["require_assurance_graph"] and not graph_path.is_file():
            errors.append(f"{record.benchmark_id}: missing assurance_graph.yaml")

    assigned: set[str] = set()
    for capability_name, capability in capabilities.items():
        qualified = capability["qualified_benchmark_ids"]
        minimum = capability["minimum_qualified"]
        if len(qualified) < minimum:
            errors.append(
                f"reference capability {capability_name}: requires {minimum}; found {len(qualified)}"
            )
        for benchmark_id in qualified:
            if benchmark_id in assigned:
                errors.append(f"reference suite: {benchmark_id} assigned to multiple capabilities")
            assigned.add(benchmark_id)
            record = records.get(benchmark_id)
            if record is None:
                errors.append(f"reference capability {capability_name}: unknown id {benchmark_id}")
                continue
            if record.track != capability["track"]:
                errors.append(
                    f"reference capability {capability_name}: {benchmark_id} track mismatch"
                )
            if benchmark_id not in corpus_ids:
                errors.append(f"reference capability {capability_name}: {benchmark_id} outside corpus")
            if record.maturity not in reference_maturities:
                errors.append(
                    f"reference capability {capability_name}: {benchmark_id} is not reference maturity"
                )
            errors.extend(_review_errors(record, review_count, distinct))

    return ReleaseContractReport(release_id, corpus, tuple(errors))
