"""Every adapter directory must expose the standard layout."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ADAPTERS = REPO / "adapters"

REQUIRED = {"README.md", "adapter.yaml", "check.sh", "parse_result.py"}


def test_adapter_layout():
    missing: list[str] = []
    for adapter_dir in sorted(p for p in ADAPTERS.iterdir() if p.is_dir()):
        for name in REQUIRED:
            if not (adapter_dir / name).is_file():
                missing.append(f"{adapter_dir.name}: missing {name}")
        if not (adapter_dir / "examples").is_dir():
            missing.append(f"{adapter_dir.name}: missing examples/")
    assert not missing, "adapter layout gaps:\n" + "\n".join(missing)
