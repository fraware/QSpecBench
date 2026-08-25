# Governance verification (v1)

Queried 25 Aug 2026 against this working tree. Live GitHub repository administration cannot be changed from this code PR.

## CODEOWNERS

`.github/CODEOWNERS` contains only the real GitHub handle `@fraware`. No placeholder reviewers.

CODEOWNER approval is **not** two-person independence. GATE-G03/G06 are not satisfied.

## Review attestation v2

The v2 validator rejects:

- duplicate reviewer `github_user_id`
- author-as-reviewer
- hash mismatch
- missing required promotion roles
- alias identities (`rkothari-formal`, `mlewis-quant-sem`, `unsigned-corpus-*`, bootstrap role names) for any `reference_claim` / `artifact_bound_reference_claim`

Alias YAML remaining in demoted packages is labeled `unauthenticated_legacy_review` in assurance-graph assumptions. It is not a v2 attestation.

## Branch protection (admin residual)

Live `main` protection (PR required, required checks, no force-push, no branch deletion) is a repository-admin step. This file does not claim those settings are enabled. Query GitHub Settings → Branches to confirm.

Required checks when protection is enabled should include Validate, Lint, Promotion Check, and Lean-QEC when Lean-QEC paths change.

## Gold inventory

v1 gold/reference inventory is empty. `experimental_closed` is machine closure, not independent review.

## Issue #9

Independent third-party cold-host reproduction remains out of scope / `post-v1`.
