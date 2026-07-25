# qbricks adapter

External-tool adapter for ``qbricks_result`` evidence.

## Trust level

`externally_trusted` — requires a real QBricks binary (or a documented fixture
CLI for tests). Fail-closed when the tool is missing (`skipped`, never `ok`
without version + command + hashes). Bare success strings from the tool are
rejected; structured JSON output is required.

## Tool resolution

1. `QSPECBENCH_QBRICKS_BIN` — absolute path or name on PATH
2. else `qbricks` on PATH

## Evidence shapes

JSON certificate (`qspecbench.qbricks_result.v1`):

```json
{
  "schema_version": "qspecbench.qbricks_result.v1",
  "circuit": "source.qasm",
  "expected_verdict": "proved"
}
```

Or a raw circuit file (implicit `expected_verdict: proved`).

## Tool output contract

```json
{
  "schema_version": "qspecbench.qbricks_tool_output.v1",
  "verdict": "proved",
  "tool": "qbricks",
  "tool_version": "…"
}
```

## Fixture CLI

`examples/fake_qbricks_cli.py` implements the contract for adapter tests only.

## Limits

Adapters exist; this is **still not a complete FV standard**. Do not promote a
benchmark to ABRC solely on QBricks evidence.
