# Schema migration guide (0.2 → 0.3)

QSpecBench schema **0.3** adds artifact-bound maturity, elaborator/AST authority
anchors, and hash-bound promotion review artifacts.

## Version field

Set `qspecbench_version: "0.3"` on active benchmarks.

## Dialect enforcement

| Version | Allowed | Forbidden |
|---------|---------|-----------|
| `0.1` | legacy fields (`seed`/`usable`) | scoped maturity, `claim_scope`, elaborator/AST anchors, review artifact fields |
| `0.2` | scoped maturity through `reference_claim` | `artifact_bound_reference_claim`, `theorem_elaborator_hash`, `ast_authority`, `lean_ast_sha256`, review artifact fields, `claim_identity` |
| `0.3` | all of the above when maturity requires them | — |

A `0.2` file containing `artifact_bound_reference_claim` **must fail** validation.

## New / required for artifact-bound claims

- `status.maturity: artifact_bound_reference_claim`
- `semantic_bridge.theorem_elaborator_hash` (primary theorem authority)
- `semantic_bridge.ast_authority: lean_mirror`
- `semantic_bridge.lean_ast_sha256`
- Dual `status.reviews.*` at `approved` with:
  - named non-bootstrap reviewers
  - `review_artifact_path` / `review_artifact_sha256` / `review_commit`
- Optional `claim_identity.proposition_id` and `authorship` for review separation

## Migration checklist

1. Bump `qspecbench_version` to `"0.3"`.
2. Remove stale 0.2 promotion comments.
3. For ABRC pilots: confirm elaborator + AST anchors and review artifacts.
4. Run `qspecbench validate benchmarks/`.

See also [schema_migration_0.2.md](schema_migration_0.2.md) and [versioning.md](versioning.md).
