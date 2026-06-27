# Pull request checklist

Use this checklist when changing benchmarks, schema, or promotion-related tooling.

## All benchmark PRs

- [ ] `qspecbench validate benchmarks/<your_claim>/` passes locally
- [ ] `qspecbench claim-diff benchmarks/<your_claim>/` reviewed; `evidence/claim_diff.md` updated if scope changed
- [ ] Trust boundary and `headline_claim_status` are honest (no overclaim)
- [ ] Artifact `provenance` SHA256 entries match on-disk files
- [ ] README **Current maturity** matches `spec.yaml` (`python scripts/sync_readme_maturity.py`)

## Reference promotion (`reference_scaffold` → `reference_claim`)

- [ ] `claim_scope.required_obligations` ⊆ `proved_scope.checked_obligations`
- [ ] `headline_claim_status.status` is `checked` with explicit `checked_under` / `not_checked_under`
- [ ] Required evidence types pass (`qspecbench check-evidence`)
- [ ] **Dual review** recorded in `status.reviews`:
  - [ ] `formal_evidence_review` — status `approved` or `required`
  - [ ] `domain_semantics_review` — status `approved` or `required`
- [ ] No maintainer self-merge without a second reviewer (see [GOVERNANCE.md](../GOVERNANCE.md))
- [ ] Open or use the [Reference promotion](../.github/ISSUE_TEMPLATE/reference_promotion.yml) issue template

## Schema / tooling PRs

- [ ] Schema version bump and migration notes if breaking
- [ ] `pytest` and CI workflows green
- [ ] Dashboard regenerated if corpus counts change: `qspecbench dashboard benchmarks/ --out docs/status.md`
