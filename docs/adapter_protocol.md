# Adapter protocol

Adapters connect external tools to QSpecBench evidence checks. They are evidence producers; they are not semantic authorities by default.

## Typed exchange contract

The migration target is a transport-neutral, versioned exchange:

`AdapterRequest -> AdapterResult`

Schemas:
- `schema/adapter_request.schema.json`
- `schema/adapter_result.schema.json`

Validator:
- `qspecbench.adapter_protocol`

An `AdapterRequest` binds a stable adapter identity/version, benchmark ID, proposition ID, semantic-profile ID, exact input paths and SHA-256 hashes, requested obligation IDs, tool identity, configuration, and resource limits.

An `AdapterResult` binds the same adapter/benchmark/proposition/semantics, exact input hashes, pass/fail/partial/not-checked status, the subset of requested obligations actually supported, trust class, tool identity, and result/certificate hashes where material.

Fail-closed invariants:
- a result may not change adapter, benchmark, proposition, or semantic profile identity;
- a result may not support an obligation that was not requested;
- input hashes must match the request exactly;
- a passing result must support at least one obligation;
- the result's trust class is explicit and cannot be inferred from a display-oriented checker string.

Free-form `checker` strings remain legacy display metadata during schema-0.3 migration. They must not select privileged execution paths in the final protocol. Special checker-string dispatch in the evidence runner is tracked for removal in issue #15.

## Trust classes

- `kernel_checked`: the stated formal proposition edge is accepted by the declared trusted kernel. This does **not** establish that the formal proposition faithfully captures the intended scientific claim.
- `independently_checkable`: a certificate/object can be checked separately from the producer.
- `externally_trusted`: correctness depends materially on the external tool implementation.
- `simulation`: empirical/numerical evidence over the explicitly declared finite regime.
- `human_review`: review judgment; promoted use must bind an authenticated review attestation.
- `heuristic`: supporting evidence only; it cannot silently satisfy a stronger trust requirement.

## Active adapters (Lean-only proof assistant policy)

| Adapter | Evidence types | Trust |
|---------|----------------|-------|
| `lean/` | `lean_proof` | checked (Lean 4 kernel) |
| `bridge/` | `bridge_verify` | checked/heuristic according to declared bridge claim and TCB; never infer hardware semantics |
| `sat_certificate/` | `sat_certificate` | independently_checkable |
| `smt/` | `smt_certificate` | independently_checkable |
| `qasm/` | `qasm_parse` | syntax only |
| `qec/` | `qec_verifier_result` | tool-checked within declared QEC scope |
| `python/` | `simulation` | heuristic/simulation |
| `qcec/` | `qcec_result` | externally_trusted (MQT QCEC or CLI) |
| `qbricks/` | `qbricks_result` | externally_trusted (external QBricks binary; fail-closed if missing) |
| `zx/` | `zx_certificate` | independently_checkable (normal-form certificate; no bare success) |
| `matrix_certificate/` | `matrix_certificate` | independently_checkable (standalone matrix equality; no `qasm_matrix`/`denotate`/`bridge_codegen` imports) |
| `human_review/` | `human_review` | human review; authenticated attestation required for promotion target |
| `ai_formalization/` | `ai_draft` rubric | untrusted as proof; semantic adjudication is separate |

Coq/Rocq/Isabelle stub adapters exist for optional second-assistant evidence but are **not** in default CI (see [Optional second-assistant adapters](#optional-second-assistant-adapters)).

## Directory layout

```text
adapters/<adapter_name>/
  README.md
  adapter.yaml
  check.sh
  parse_result.py
  examples/
```

## Rules

- Adapters must not silently pass.
- Distinguish syntax/parse success from semantic verification.
- Do not upgrade trust level beyond checker capability.
- Bind exact artifact hashes and proposition/semantic identity.
- Report precisely which obligation IDs are supported.
- Preserve historical tool versions in recorded evidence; a later compatibility lane must not reinterpret old evidence.
- Be callable from CI or explicitly documented as manual.
- Third-party adapters should eventually pass a conformance suite without requiring edits to the core runner.

## Version-isolated interoperability

For external ecosystems whose Lean/tool versions do not match the repository's current environment, prefer a version-isolated theorem/certificate adapter first. An adapter should preserve:
- external repository and exact commit;
- external toolchain/compiler/prover version;
- theorem/certificate identifier and artifact hash;
- proposition relation and semantic assumptions;
- the exact obligations the imported result supports.

This is the preferred first integration path for Lean-QEC, Lean-Quantum/Lean-QIT exports, QCEC compatibility lanes, QBricks, ZX tooling, Coq/Rocq, and Isabelle. Do not force toolchain unification merely to claim interoperability.

## Optional second-assistant adapters

Lean 4 is the only kernel-checked proof assistant in **default CI**. Coq, Rocq, and Isabelle stub adapters live under `adapters/coq/`, `adapters/rocq/`, and `adapters/isabelle/` (required by `tests/test_repo_policy.py`) for optional evidence when `QSPECBENCH_COQ=1` and `coqc` are available locally or in a custom CI job. They are not invoked by `.github/workflows/validate.yml` or `lint.yml`.

- Coq adapter: real `coqc` checks when enabled; see `adapters/coq/README.md`.
- Rocq/Isabelle: fail-closed stubs (`skipped: true`) until a driving benchmark needs them.
- Evidence types `qbricks_result` and `zx_certificate` are registered with shipping adapters (`adapters/qbricks/`, `adapters/zx/`). **Adapters exist; still not a complete full-vision standard** — do not auto-promote ABRC solely on QBricks/ZX evidence.

See [Lean setup](lean_setup.md) for proof assistant installation.
