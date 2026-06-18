.PHONY: install validate status dashboard test lint

install:
	python -m pip install -e ".[dev]"

validate:
	qspecbench validate benchmarks/

status:
	qspecbench status benchmarks/

dashboard:
	qspecbench dashboard benchmarks/ --out docs/status.md

test:
	pytest

lint:
	ruff check tools tests
