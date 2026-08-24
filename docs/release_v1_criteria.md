# QSpecBench v1 release criteria

A `v1.0` tag is a claim about integrity and scientific/governance readiness, not merely a version number.

## Identity

A v1 release must bind:
- exact Git commit SHA;
- schema/tooling/corpus versions;
- immutable release tag;
- release-bundle SHA-256;
- archive/DOI or equivalent durable identifier once deposited.

## Required bundle contents

- all benchmark specifications and concrete artifacts;
- artifact SHA-256 manifest;
- registered semantic profiles;
- all assurance graphs;
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
- artifact hash drift;
- semantic-profile mismatch;
- orphan required obligation;
- missing/failing evidence edge;
- adapter proposition/semantic/input-hash mismatch;
- missing required review role or reviewer conflict;
- stale generated status;
- theorem/bridge metadata mismatch.

## Scientific gate

Before `v1.0`, the scientific-reference-suite criteria in `definition_of_completion.md` must be met without broadening narrow existing theorems by description. In particular, the release needs the real compiler-transformation, arbitrary-input dynamic-protocol, operator-level Hamiltonian, meaningful QEC assurance, and semantically adjudicated AI targets.

## Governance gate

Before `v1.0`, community-grade governance requires actual independent maintainers/reviewers, protected promotion workflow, and authenticated review records. A sole interim owner does not satisfy the gate.

## Reproducibility boundary

The repository release workflow should prove that the exact release commit produced and verifies the bundle. The external reproduction program is explicitly excluded from the current execution request and is not silently claimed here.

Issue #23 tracks completion and archival publication.
