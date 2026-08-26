# QSpecBench v1 release criteria

A `v1.0` tag is a claim about integrity and scientific/governance readiness, not merely a version number.

The canonical machine-readable qualification policy is [`release_v1_contract.yaml`](release_v1_contract.yaml), validated by `schema/release_contract.schema.json` and `scripts/check_release_contract.py`. Human documentation must not weaken that contract.

## Identity

A v1 release must bind:
- exact Git commit SHA;
- schema/tooling/corpus versions;
- immutable release tag;
- release-bundle SHA-256;
- archive/DOI or equivalent durable identifier once deposited.

## Non-vacuous release corpus

Strict release qualification is evaluated over the corpus selected by `docs/release_v1_contract.yaml`. The baseline selector includes `experimental_closed`, `reference_claim`, and `artifact_bound_reference_claim` packages and is required to be non-empty.

This is intentionally broader than the promoted-reference inventory. An empty gold/reference inventory therefore cannot make assurance migration or release qualification pass by empty-set logic.

Every selected release-corpus package must bind an explicit proposition identity and have a closed `assurance_graph.yaml` before strict qualification can succeed.

## Required bundle contents

- all benchmark specifications and concrete artifacts;
- artifact SHA-256 manifest;
- registered semantic profiles;
- all release-corpus assurance graphs;
- proposition and obligation identifiers;
- proof/theorem/elaborator exports used for promotion;
- typed adapter request/result records for executed external evidence;
- exact tool versions/digests and dependency lockfiles;
- authenticated review-attestation v2 records for promoted claims;
- generated corpus status and maturity listings;
- SBOM and reproducibility metadata;
- release provenance/attestation metadata.

## Verification

From a clean checkout/bundle, verification must fail closed on:
- wrong commit identity;
- empty or invalid release-corpus selection;
- artifact hash drift;
- semantic-profile mismatch;
- orphan required obligation;
- missing/failing evidence edge;
- adapter proposition/semantic/input-hash mismatch;
- missing required review role or reviewer conflict for reference qualification;
- stale generated status;
- theorem/bridge metadata mismatch;
- any required Level-C capability lacking a genuinely qualified benchmark.

`scripts/release_verify.py` must invoke strict release-contract qualification on the candidate SHA; ordinary PR CI may use structural contract validation so research can progress before the five reference capabilities are complete.

## Scientific gate

Before `v1.0`, the scientific-reference-suite criteria in `definition_of_completion.md` must be met without broadening narrow existing theorems by description. In particular, the release needs the real compiler-transformation, arbitrary-input dynamic-protocol, operator-level Hamiltonian, meaningful QEC assurance, and semantically adjudicated AI targets.

A benchmark only satisfies one of those five required capabilities when it is explicitly assigned in the canonical contract **and** strict qualification verifies that it belongs to the release corpus, has reference maturity, and satisfies the configured independent-review policy.

## Governance gate

Before `v1.0`, community-grade governance requires actual independent maintainers/reviewers, protected promotion workflow, and authenticated review records. A sole interim owner does not satisfy the gate.

## Reproducibility boundary

The repository release workflow should prove that the exact release commit produced and verifies the bundle. The external reproduction program is explicitly excluded from the current execution request and is not silently claimed here.

Issue #23 tracks completion and archival publication. Issue #13 tracks non-vacuous release-corpus assurance closure.
