from pathlib import Path

from qspecbench.generated_status import generate_status_snapshot


def test_generated_status_is_in_sync() -> None:
    expected = Path("docs/generated_status.md").read_text(encoding="utf-8")
    actual = generate_status_snapshot(Path("benchmarks"))
    assert actual == expected, (
        "docs/generated_status.md is stale; regenerate it from the corpus/tooling source of truth"
    )
