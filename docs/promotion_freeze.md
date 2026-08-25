# Promotion freeze (v1)

Owner decision: independent reviewers will not exist in time for v1. Do not fabricate identities.

## Frozen labels

The following labels require authentic, distinct, public reviewer identities bound by review-attestation v2:

- `reference_claim`
- `artifact_bound_reference_claim`

They are unreachable on the v1 path. Alias reviews (`rkothari-formal`, `mlewis-quant-sem`, `unsigned-corpus-v0.3-*`, bootstrap role names) are historical artifacts. They may be retained as `unauthenticated_legacy_review` and must not be interpreted as authenticated independent review.

## Allowed cached machine-closure label

`experimental_closed` means total required-obligation closure + bound artifacts + executable semantic profile, without authenticated independent review. It is machine closure, not gold promotion.

## Scripts

`scripts/promote_reference_benchmarks.py` must refuse to write RC/ABRC. New gold inventory remains empty until real reviewers exist.
