# Adapter protocol

Adapters connect external tools to QSpecBench evidence checks. They are evidence producers; they are not semantic authorities by default.

## Typed exchange contract

The execution contract is a transport-neutral, versioned exchange:

`AdapterRequest -> AdapterResult`

Schemas:
- `schema/adapter_request.schema.json`
- `schema/adapter_result.schema.json`

Validators and conformance harness:
- `qspecbench.adapter_protocol`
- `qspecbench.adapter_conformance`

An `AdapterRequest` binds a stable adapter identity/version, benchmark ID, proposition ID, semantic-profile ID, exact input paths and SHA-256 hashes, requested obligation IDs, declared dependencies/expected outputs, tool identity, configuration, and resource limits.

An `AdapterResult` binds the same adapter/benchmark/proposition/semantics, exact input hashes, pass/fail/partial/not-checked status, the subset of requested obligations actually supported, trust class, tool identity, result/certificate hashes where material, and QSpecBench-owned runner execution metadata when the core runner executed the adapter.

Fail-closed invariants:
- a result may not change adapter, benchmark, proposition, or semantic profile identity;
- a result may not support an obligation that was not requested;
- input hashes must match the request exactly;
- a passing result must support at least one obligation;
- the result's trust class is explicit and cannot be inferred from a display-oriented checker string;
- runner-observed resource-limit keys and requested values must exactly match the originating request;
- adapter subprocesses may not assert QSpecBench-owned `runner_execution` metadata;
- legacy JSON normalized by the runner receives a deterministic SHA-256 of the exact observed adapter payload; certificate/tool digests are preserved only when actually supplied.

Free-form `checker` strings remain legacy display metadata during schema-0.3 migration. They do **not** select privileged execution paths. Historical `adapter.yaml` fields such as `check_command` are descriptive/backward-compatibility metadata only; executable identity comes from the versioned typed registry.

## Execution identity and registry

Built-in execution is selected by exact typed IDs such as `qspecbench.lean.kernel.v1` and `qspecbench.qec.stim_matching.v1`. Legacy schema-0.3 directory aliases may canonicalize at the spec input boundary, but assurance graphs and typed sidecars require exact typed IDs. Directory names themselves never become executable authority.

The shipping-adapter conformance gate verifies:
- stable typed ID/version shape;
- declared trust ceiling and supported evidence types;
- repository-owned implementation paths remain under `adapters/`;
- implementation files exist and are Python entry points expected by the runner;
- every shipping adapter directory with `adapter.yaml` has a registered typed implementation;
- any manifest that declares `adapter_id`/`adapter_version` agrees with the typed registry.

This lets legacy manifests remain readable without granting their free-form command strings execution authority.

## Third-party adapters

A separately installed Python package may expose a typed adapter specification through the `qspecbench.adapters` Python entry-point group. External discovery is disabled by default and requires explicit operator opt-in:

```bash
export QSPECBENCH_ENABLE_ADAPTER_PLUGINS=1
```

External implementations are addressed as Python modules, not benchmark-supplied filesystem paths or shell commands. A third-party adapter therefore can be added without editing core dispatch logic while benchmark content remains unable to nominate arbitrary executable code.

**Trust boundary:** enabling an installed adapter plugin is an operator trust decision. The plugin package executes as local Python code and is not a multi-tenant sandbox. A plugin cannot shadow a built-in adapter ID, and its registry trust ceiling cannot exceed `externally_trusted`; an independently-checkable or kernel-grade path must be reviewed and incorporated as a repository-owned integration with its actual verification mechanism. Plugin installation alone is never evidence that a scientific proposition is true.

## Resource metadata

Wall-clock timeout is enforced by the parent runner and reported as `enforced`. On POSIX hosts the sandbox attempts `RLIMIT_CPU` and `RLIMIT_AS`, but the parent process cannot independently observe whether each pre-exec `setrlimit` call succeeded. Those limits are therefore reported honestly as `attempted`; unsupported platforms report `unavailable`.

QSpecBench does not upgrade `attempted` to `enforced` merely because a subprocess completed successfully.

## Trust classes

- `kernel_checked`: the stated formal proposition edge is accepted by the declared trusted kernel. This does **not** establish that the formal proposition faithfully captures the intended scientific claim.
- `proof_assistant_native_checked`: native proof-assistant acceptance used by the Lean-QEC lane; treated as a subtype of `kernel_checked`, not as a stronger class.
- `independently_checkable`: a certificate/object can be checked separately from the producer.
- `externally_trusted`: correctness depends materially on the external tool implementation.
- `simulation`: empirical/numerical evidence over the explicitly declared finite regime.
- `human_review`: review judgment; promoted use must bind an authenticated review attestation.
- `heuristic`: supporting evidence only; it cannot silently satisfy a stronger trust requirement.
- `untrusted`: draft/supporting material with no proof authority.

## Active adapters (Lean-only default proof-assistant policy)

| Adapter | Evidence types | Trust |
|---------|----------------|-------|
| `lean/` | `lean_proof`, `proof_assistant_proof` | `kernel_checked` |
| `lean_qec/` | scoped QEC distance evidence | `kernel_checked` ceiling; native acceptance may report subtype `proof_assistant_native_checked` |
| `bridge/` | bridge/internal denotation checks | adapter-specific; never infer hardware semantics |
| `compiler_peephole/` | internal denotation consistency | `independently_checkable` |
| `qiskit_compiler/` | exact compiler transformation instance | `independently_checkable` |
| `sat_certificate/` | `sat_certificate` | `independently_checkable` |
| `smt/` | `smt_certificate` | `independently_checkable` |
| `qasm/` | `qasm_parse` | syntax/external parser trust only |
| `qec/` | `qec_verifier_result` | adapter-specific scoped evidence |
| `python/` | `simulation` | `heuristic` |
| `dynamic_simulation/` | `simulation` | `simulation` |
| `qcec/` | `qcec_result` | `externally_trusted` |
| `qbricks/` | `qbricks_result` | `externally_trusted` |
| `zx/` | `zx_certificate` | `independently_checkable` |
| `matrix_certificate/` | `matrix_certificate` | `independently_checkable` |
| `human_review/` | `human_review` | externally supplied judgment; authenticated attestation required for promotion |
| `ai_formalization/` | `ai_draft` | `untrusted` as proof |

Coq/Rocq/Isabelle adapters exist for optional second-assistant evidence but are **not** in default CI; see [Optional second-assistant adapters](#optional-second-assistant-adapters).

## Directory layout

```text
adapters/<adapter_name>/
  README.md
  adapter.yaml
  check.sh                 # optional/legacy convenience; not execution identity
  parse_result.py          # common built-in implementation shape
  examples/
```

Some adapters use a different registered Python implementation filename. The typed registry, not this illustrative layout, is authoritative.

## Rules

- Adapters must not silently pass.
- Distinguish syntax/parse success from semantic verification.
- Do not upgrade trust level beyond checker capability.
- Bind exact artifact hashes and proposition/semantic identity.
- Report precisely which obligation IDs are supported.
- Preserve historical evidence tool versions; a later compatibility lane must not reinterpret old evidence.
- Report result/certificate/tool digests only when they correspond to actual observed objects; do not manufacture missing certificate identity.
- Preserve QSpecBench-owned runner metadata separately from adapter-authored output.
- Third-party adapters must pass the same typed protocol/conformance invariants and must not require benchmark-controlled paths or core checker-string dispatch.

## Version-isolated interoperability

For external ecosystems whose Lean/tool versions do not match the repository's current environment, prefer a version-isolated theorem/certificate adapter first. An adapter should preserve:
- external repository and exact commit;
- external toolchain/compiler/prover version;
- theorem/certificate identifier and artifact hash;
- proposition relation and semantic assumptions;
- the exact obligations the imported result supports.

This is the preferred first integration path for Lean-QEC, Lean-Quantum/Lean-QIT exports, QCEC compatibility lanes, QBricks, ZX tooling, Coq/Rocq, and Isabelle. Do not force toolchain unification merely to claim interoperability.

## Optional second-assistant adapters

Lean 4 is the only kernel-checked proof assistant in **default CI**. Coq, Rocq, and Isabelle stub adapters live under `adapters/coq/`, `adapters/rocq/`, and `adapters/isabelle/` (required by `tests/test_repo_policy.py`) for optional evidence when their respective toolchains are explicitly available locally or in a custom CI job. They are not invoked by the ordinary validation/lint lanes as proof-assistant substitutes for Lean.

- Coq adapter: real `coqc` checks when enabled; see `adapters/coq/README.md`.
- Rocq/Isabelle: fail-closed stubs unless a driving benchmark/toolchain explicitly enables real checking.
- QBricks/ZX adapter existence is not a badge of full-vision completeness and must not trigger automatic gold promotion.

See [Lean setup](lean_setup.md) for proof assistant installation.
