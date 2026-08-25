from pathlib import Path

from qspecbench.generated_status import generate_status_snapshot
from qspecbench.interoperability import generate_interoperability_matrix


def test_generated_status_is_in_sync() -> None:
    expected = Path("docs/generated_status.md").read_text(encoding="utf-8")
    actual = generate_status_snapshot(Path("benchmarks"))
    assert actual == expected, (
        "docs/generated_status.md is stale; regenerate it from the corpus/tooling source of truth"
    )


def test_interoperability_matrix_is_in_sync() -> None:
    expected = Path("docs/interoperability_matrix.md").read_text(encoding="utf-8")
    actual = generate_interoperability_matrix()
    assert actual == expected, "docs/interoperability_matrix.md is stale; regenerate from qspecbench.interoperability"
