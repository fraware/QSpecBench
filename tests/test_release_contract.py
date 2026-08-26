from __future__ import annotations

import copy
import shutil
from pathlib import Path

import yaml

from qspecbench.release_contract import DEFAULT_CONTRACT, DEFAULT_SCHEMA, validate_release_contract

REPO = Path(__file__).resolve().parents[1]


def _write_fixture_repo(tmp_path: Path, *, maturity: str, selectors: list[str]) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "schema").mkdir()
    package = tmp_path / "benchmarks" / "algorithm" / "fixture"
    package.mkdir(parents=True)
    shutil.copy(REPO / DEFAULT_SCHEMA, tmp_path / DEFAULT_SCHEMA)

    contract = yaml.safe_load((REPO / DEFAULT_CONTRACT).read_text(encoding="utf-8"))
    contract = copy.deepcopy(contract)
    contract["release_corpus"]["maturity_selectors"] = selectors
    (tmp_path / DEFAULT_CONTRACT).write_text(
        yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
    )
    (package / "spec.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "fixture_benchmark",
                "track": "algorithm",
                "status": {"maturity": maturity},
                "claim_identity": {"proposition_id": "fixture_v1"},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_live_release_contract_selects_nonempty_corpus() -> None:
    report = validate_release_contract(REPO)
    assert report.ok, report.errors
    assert report.corpus, "canonical v1 release corpus must never be empty"


def test_reference_only_selector_cannot_pass_vacuously(tmp_path: Path) -> None:
    repo = _write_fixture_repo(
        tmp_path,
        maturity="experimental_closed",
        selectors=["reference_claim", "artifact_bound_reference_claim"],
    )
    report = validate_release_contract(repo)
    assert not report.ok
    assert any("release corpus is empty" in error for error in report.errors)


def test_strict_qualification_rejects_unfilled_reference_suite(tmp_path: Path) -> None:
    repo = _write_fixture_repo(
        tmp_path,
        maturity="experimental_closed",
        selectors=["experimental_closed"],
    )
    report = validate_release_contract(repo, strict_qualification=True)
    assert not report.ok
    assert any("missing assurance_graph.yaml" in error for error in report.errors)
    for capability in (
        "compiler_transformation_equivalence",
        "arbitrary_input_dynamic_protocol",
        "operator_level_hamiltonian_approximation",
        "meaningful_qec_assurance",
        "externally_adjudicated_ai_formalization",
    ):
        assert any(capability in error for error in report.errors)
