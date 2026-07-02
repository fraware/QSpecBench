.PHONY: install validate status dashboard test lint check-evidence bridge lean

install:
	@echo "Prefer: uv sync --frozen --extra dev (matches CI); fallback: pip install -e '.[dev]'"
	@command -v uv >/dev/null 2>&1 && uv sync --frozen --extra dev || python -m pip install -e ".[dev]"

validate:
	qspecbench validate benchmarks/

status:
	qspecbench status benchmarks/

dashboard:
	qspecbench dashboard benchmarks/ --out docs/status.md

check-evidence:
	qspecbench check-evidence benchmarks/

bridge:
	qspecbench verify-bridge benchmarks/equivalence/cnot_self_inverse_cancellation

lean:
	cd lean && lake build

test:
	pytest

lint:
	ruff check tools tests adapters scripts
