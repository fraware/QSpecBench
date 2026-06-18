# Schema reference (QSpecBench 0.1)

Specifications are YAML files validated by `schema/qspecbench.schema.json` and `qspecbench validate`.

## Root fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `qspecbench_version` | string | yes | Must be `"0.1"` |
| `id` | string | yes | Lowercase snake_case; must equal directory name |
| `title` | string | yes | Human title |
| `track` | enum | yes | `algorithm`, `equivalence`, `qec`, `hamiltonian`, `ai_formalization` |
| `domain` | string | yes | Free-form domain label |
| `claim_type` | string | yes | Track-specific classifier |
| `difficulty` | enum | yes | `introductory`, `intermediate`, `advanced`, `frontier` |
| `informal_claim` | object | yes | See below |
| `semantic_level` | object | yes | See below |
| `objects` | array | yes | Min 1 artifact entry |
| `specification` | object | yes | See below |
| `assumptions` | object | yes | See below |
| `acceptable_evidence` | array | yes | Min 1 entry |
| `evidence` | array | yes | May be empty |
| `trust_boundary` | object | yes | See below |
| `status` | object | yes | See below |
| `qec_status` | object | no | QEC sub-status |
| `references` | array | yes | Bibliography (may be empty) |

## `informal_claim`

| Field | Type | Required |
|-------|------|----------|
| `statement` | string | yes |
| `source` | string \| null | no |
| `reference_key` | string \| null | no |

## `semantic_level`

| Field | Type | Required |
|-------|------|----------|
| `primary` | enum | yes | `mathematical`, `algorithmic`, `circuit`, `compiler`, `qec`, `physical`, `protocol`, `ai_formalization` |
| `secondary` | string[] | no |

## `objects[]`

| Field | Type | Required |
|-------|------|----------|
| `name` | string | yes |
| `type` | enum | yes | `circuit`, `program`, `hamiltonian`, `stabilizer_code`, `protocol`, `theorem`, `channel`, `measurement`, `oracle`, `decoder`, `other` |
| `path` | string \| null | no | Relative path; if set, file must exist |
| `format` | enum | yes | `qasm2`, `qasm3`, `json`, `yaml`, `lean`, `python`, `markdown`, `latex`, `other` |
| `role` | enum | yes | `source`, `target`, `specification`, `witness`, `reference`, `generated` |

## `specification`

| Field | Type | Required |
|-------|------|----------|
| `mode` | enum | yes | `exact`, `approximate`, `relational`, `temporal`, `resource`, `negative`, `mixed` |
| `preconditions` | string[] | yes | At least one of pre/post required |
| `postconditions` | string[] | yes | |
| `invariants` | string[] | yes | |
| `approximation` | object | yes | See below |
| `resources` | object | yes | See below |

### `approximation`

| Field | Type | Notes |
|-------|------|-------|
| `enabled` | boolean | Must be true if `mode: approximate` |
| `metric` | enum \| null | Required when enabled |
| `bound` | string \| null | Required when enabled |

Metrics: `trace_distance`, `fidelity`, `diamond_norm`, `total_variation`, `operator_norm`, `logical_error_rate`, `other`.

### `resources`

| Field | Type | Notes |
|-------|------|-------|
| `enabled` | boolean | If true, at least one resource field non-null |
| `qubits`, `gates`, `depth`, `t_count`, `t_depth`, `ancilla`, `measurements` | string \| null | |
| `other` | string[] | |

## `assumptions`

Lists: `mathematical`, `physical`, `tool`, `artifact`, `unverified` (each string[]).

## `acceptable_evidence[]` / `evidence[]`

| Field | Type | Notes |
|-------|------|-------|
| `type` | enum | See evidence model |
| `checker` | string | Required for passing evidence |
| `path` | string \| null | |
| `required_for_claim` | boolean | acceptable only |
| `trust_level` | enum | `checked`, `independently_checkable`, `externally_trusted`, `heuristic`, `untrusted` |
| `id` | string | evidence only |
| `command` | string \| null | evidence only |
| `status` | enum | `passing`, `failing`, `partial`, `not_checked`, `draft` |
| `notes` | string \| null | evidence only |

## `trust_boundary`

| Field | Type |
|-------|------|
| `checked_by` | string[] |
| `trusted_kernels` | string[] |
| `trusted_external_tools` | string[] |
| `untrusted_components` | string[] |
| `assumptions_not_checked` | string[] |

At least one list must be non-empty.

## `status`

| Field | Enum values |
|-------|-------------|
| `informal_claim`, `machine_spec` | `missing`, `draft`, `complete` |
| `artifacts`, `evidence` | `missing`, `partial`, `complete` |
| `ci` | `not_applicable`, `failing`, `passing` |
| `maturity` | `seed`, `usable`, `reference`, `deprecated` |

Reference maturity requires `ci: passing` and passing checked evidence (`lean_proof`, `smt_certificate`, `sat_certificate`).

## `qec_status` (optional)

`code_definition`, `stabilizer_commutation`, `distance_claim`, `syndrome_extraction`, `decoder_claim`, `correction_claim`, `repeated_round_claim` — see `docs/qec_track.md`.

## Validation rules (summary)

- ID matches directory; track matches parent folder
- Approximate specs require metric and bound
- `ai_draft` must be untrusted; `simulation` cannot be checked
- Deprecated README must mention deprecation
- Artifacts/evidence paths must resolve

## Examples

### Minimal

```yaml
qspecbench_version: "0.1"
id: minimal_example
# see schema/examples/minimal.spec.yaml
```

### QEC

See `schema/examples/qec.spec.yaml` and `benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x/`.

### Approximate correctness

```yaml
specification:
  mode: approximate
  approximation:
    enabled: true
    metric: fidelity
    bound: "1e-6"
```

See `benchmarks/hamiltonian/single_trotter_step_declares_error_contract/`.
