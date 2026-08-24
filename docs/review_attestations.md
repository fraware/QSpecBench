# Authenticated review attestations

Promoted QSpecBench claims require review of two different things: formal evidence and domain semantics. A reviewer label inside a YAML/JSON file is not, by itself, evidence of an independent human review.

## Migration target

`schema/review_attestation_v2.schema.json` defines the authenticated review record. A v2 attestation binds:
- benchmark and proposition ID;
- reviewer name, GitHub login and durable numeric GitHub user ID;
- review role;
- exact reviewed commit;
- public pull-request/review event when available;
- exact reviewed artifact paths and SHA-256 hashes;
- accepted and rejected obligation IDs;
- residual assumptions;
- conflict declarations;
- decision;
- attestation method/reference.

## Independence requirements

For `reference_claim` and `artifact_bound_reference_claim` promotion:
- formal-evidence and domain-semantics reviews must be performed by distinct reviewers;
- neither independent reviewer may be the claim author or merging maintainer;
- a bootstrap alias or corpus-only nickname is insufficient proof of identity;
- review must bind the exact commit/artifact versions being promoted;
- later artifact/proposition/semantic changes invalidate the earlier attestation unless the review explicitly covers them.

## Current state

Legacy review artifacts remain part of schema-0.3 historical evidence. They are not automatically upgraded to v2 and must not be described as authenticated merely because the files validate structurally.

Issue #12 tracks re-attestation of promoted claims. Until that work is complete, new high-maturity promotions should remain frozen. Existing maturity labels should be interpreted with their recorded historical trust boundary, not retroactively strengthened.

## What validation can and cannot establish

Repository validation can check attestation schema, claim/proposition binding, exact reviewed artifact hashes, distinct reviewer IDs, role coverage and author/merger conflicts. A repository-local validator cannot independently prove that a human controls a GitHub identity or that a public review event is genuine without querying GitHub. Release/audit tooling should therefore verify public review references against GitHub when network access is available and record the result.

No tooling should invent missing identities, infer independence from a display name, or silently convert a legacy reviewer string into an authenticated reviewer record.
