# Reference benchmark governance (Layer 3)

Reference levels are **scoped**. A benchmark may have reproducible checked evidence for *part* of its
claim (`reference_scaffold`, `reference_contract`, `reference_artifact`) while the full informal
headline claim is still unproved. The headline claim is only considered a **gold**
`reference_claim` / `artifact_bound_reference_claim` when required evidence **and** authenticated
independent review are present.

## v1 promotion freeze

Owner decision: authentic independent reviewers will not exist in time for v1.
See [promotion_freeze.md](promotion_freeze.md) and [governance_verification.md](governance_verification.md).

| Label | v1 status |
|-------|-----------|
| `reference_claim` | **Unreachable** — inventory empty |
| `artifact_bound_reference_claim` | **Unreachable** — inventory empty |
| `experimental_closed` | Allowed for machine closure without independent review |

Do not invent reviewer identities. Do not treat `unauthenticated_legacy_review` alias YAML as gold.

## Scoped maturity levels

| Level | Meaning |
|-------|---------|
| `reference_scaffold` | Passing evidence path for at least one checked obligation; headline only partially checked. |
| `reference_contract` | Checked evidence is a declared contract (resource/error bound) rather than a proof of a stronger bound. |
| `reference_artifact` | Checked evidence is artifact-structural (e.g. stabilizer commutation). |
| `experimental_closed` | Total required-obligation closure under declared semantics **without** authenticated independent review. |
| `reference_claim` | Headline claim fully proved **and** authentic independent review (frozen for v1). |
| `artifact_bound_reference_claim` | `reference_claim` plus explicit artifact SHA256 / checker-chain binding (frozen for v1). |

### Future `artifact_bound_reference_claim` checklist (post-freeze)

All items required before setting `status.maturity: artifact_bound_reference_claim` once real reviewers exist:

| Requirement | Validator gate |
|---|---|
| Dual authenticated reviews (`formal_evidence_review`, `domain_semantics_review`) under review-attestation v2 | Hard fail if missing, aliased, or bootstrap-only |
| `headline_claim_status.status: checked` | Hard fail |
| Empty `proved_scope.unproved_obligations` | Hard fail |
| `semantic_bridge.claimed_link` one of the registered kernel-checked links | Hard fail |
| Bridge hash anchors | Hard fail |
| Passing bridge verify evidence | Hard fail |
| Lean metadata literals match manifest | CI test |
| README documents artifact binding scope | Maintainer review |

**Assigned ABRC / RC inventory at v1:** **none**. Formerly listed pilots were demoted to
`experimental_closed` or lower. Regenerate live lists via the dashboard.

## Universal requirements (any scoped reference / machine-closure level)

- Honest `trust_boundary` with `assumptions_not_checked`
- README claim card documents scope limits
- Every `evidence.type` is declared in `acceptable_evidence`
- Observed CI state must be read from the workflow run for the exact commit

## Additional requirements for gold `reference_claim` (when unfrozen)

- `claim_scope` declared
- `proved_scope.checked_obligations` covers every required obligation
- `headline_claim_status.status: checked` with honest `checked_under` / `not_checked_under`
- Every `required_for_claim` evidence type has a passing entry
- Two authenticated, independent review-attestation v2 records

## Anti-patterns (do not promote)

- Simulation-only evidence labeled as checked proof
- `reference_claim` / ABRC while gold freeze is active
- Treating alias reviewers as authenticated independence
- `headline_claim_status: checked` on a scaffold-level benchmark
- Claiming unnormalized Toffoli pair equality or matrix KERNEL_BRIDGE for measure+if dynamics
- Calling `experimental_closed` “independently reviewed” or “community-grade”

## Promotion workflow (when gold is unfrozen)

1. Open a reference promotion proposal (issue template)
2. Add evidence until the track stack is satisfied
3. Collect authenticated review-attestation v2 records from distinct public identities
4. Run `qspecbench validate`, `qspecbench check-evidence`, `lake build`
5. Maintainer review of `trust_boundary` honesty

## Current corpus

Regenerate counts (do not hand-edit):

```bash
qspecbench dashboard benchmarks/ --out docs/status.md
python -c "from pathlib import Path; from qspecbench.generated_status import write_status_snapshot; write_status_snapshot(Path('benchmarks'), Path('docs/generated_status.md'))"
```

See [generated_status.md](generated_status.md) and [definition_of_completion.md](definition_of_completion.md).
