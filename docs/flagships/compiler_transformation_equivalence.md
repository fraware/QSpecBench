# Flagship specification: real compiler transformation equivalence

Status: **required scientific target; not yet a completed proof.** See issue #17.

## Proposition target

For one real, reproducibly generated compiler transformation, prove that a pinned source artifact and its pinned compiler-produced target artifact have equivalent denotations under one explicitly versioned semantic profile, subject only to declared ancilla/wire/global-phase policies.

The proposition must identify:
- compiler/project name;
- compiler version or exact commit;
- transformation pass/pipeline and configuration;
- source artifact SHA-256;
- target artifact SHA-256;
- semantic profile ID;
- equivalence relation (exact or explicitly up to global phase);
- wire/register/ancilla policy.

## Required obligations

1. `compiler_provenance_bound` — target is reproducibly generated from the source by the declared compiler/configuration.
2. `source_artifact_parse` — source parses fail-closed under the declared profile.
3. `target_artifact_parse` — target parses fail-closed under the same declared profile or a declared relation between source/target profiles.
4. `source_denotation` — source artifact is bound to its formal denotation.
5. `target_denotation` — target artifact is bound to its formal denotation.
6. `wire_ancilla_alignment` — register mapping and ancilla assumptions are explicit and checked.
7. `phase_policy` — exact/global-phase relation is explicit and checked.
8. `source_target_equivalence` — formal equality/equivalence theorem for the pinned artifact pair.

## Evidence target

Primary evidence should be kernel-checked source/target parsing/denotation/equivalence where feasible. MQT QCEC should be an independent supporting checker with its exact version/configuration recorded, not the definition of the semantic proposition.

The assurance graph must bind every required obligation to explicit evidence edges. A handcrafted identity may remain a useful benchmark but does not satisfy the “real compiler transformation” flagship.

## Promotion gate

Do not promote the flagship until:
- the compiler output is generated reproducibly from the recorded source/config;
- all required obligations are closed;
- semantic profile(s) are authoritative and cross-consistent;
- exact artifacts and evidence are hash-bound;
- two authenticated independent reviews cover formal evidence and domain semantics;
- exact-head CI/release verification passes.
