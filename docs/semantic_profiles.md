# Semantic profile authority

QSpecBench treats a semantic profile as part of the claim, not as descriptive metadata.
A promoted claim is meaningful only relative to one executable interpretation of its
artifacts. The profile therefore fixes the language/version, supported grammar,
semantic conventions, parser or interpreter implementation, and unsupported-syntax
behavior that participate in the evidence chain.

## Immutability and versioning

Published profile identifiers are immutable contracts. If an implementation,
wire-order convention, gate meaning, parameter grammar, include policy, measurement
model, or trust boundary changes, the change requires a new profile identifier or
version. Historical profiles remain registered so old evidence can still be
reproduced; they are not silently reinterpreted under newer semantics.

Two historical profiles are intentionally reproducibility-only for future promotion:

- `qspecbench.openqasm3.unitary.v1` records the legacy matrix path, including its
  `legacy_kron_order` convention. Existing hash-bound evidence keeps that meaning.
- `qspecbench.dynamic_quantum.instrument_feedforward.v1` is a declarative historical
  profile and is not sufficiently executable to support new promoted claims.

The validator rejects either profile if a package attempts promotion to
`reference_claim` or `artifact_bound_reference_claim`.

## Canonical static unitary profile

`qspecbench.openqasm3.unitary_lsb.v2` is the canonical Python unitary profile for new
promotable evidence. Its executable interpreter is
`qspecbench.canonical_qasm.extract_lsb_unitary`.

The contract is deliberately narrow:

- exact upstream header: OpenQASM 3.0;
- include statements are skipped syntactically and are not interpreted as library
  semantics;
- vector `qubit[n]` declarations only;
- an explicit finite gate subset and restricted angle grammar;
- `q[i]` is basis-index bit weight `2^i` (little-endian/LSB);
- Hadamard is normalized by `1/sqrt(2)`;
- unitary equality uses exact global phase;
- measurement, reset, and classical control are rejected;
- unsupported executable syntax fails closed.

The legacy matrix extractor remains available for historical artifacts. It is not the
canonical v2 interpreter.

## Bounded dynamic-instrument profile

`qspecbench.dynamic_quantum.instrument_feedforward.v2` is a separate operational
profile. Its interpreter is
`qspecbench.dynamic_profile.simulate_instrument_feedforward_v2`.

It models only a bounded deterministic execution fragment:

- exact OpenQASM 3.0 header;
- vector qubit and bit declarations;
- the registered bounded gate subset under the same LSB wire convention as the
  canonical static interpreter;
- computational-basis projective measurements with state collapse;
- indexed or scalar measured-bit predicates of the form `<bit> == 1`;
- supported gate actions in the conditional body;
- optional explicit Pauli X/Z correction tables;
- at most four qubits;
- no reset, loops, `else`, arbitrary classical expressions, full branch enumeration,
  density-operator/channel semantics, or hardware semantics;
- nondeterministic measurement at the single-execution entry point fails closed.

This profile does not prove arbitrary-input teleportation correctness. A benchmark
must still discharge the proposition-specific mathematical and assurance obligations
required for promotion.

## Promotion invariants

For a promoted package, the following must be mutually consistent:

1. `spec.yaml` semantic profile selection;
2. `assurance_graph.yaml` `semantic_profile.id`;
3. the registered profile content and version;
4. parser/interpreter capability and fail-closed behavior;
5. semantic-bridge wire order;
6. semantic-bridge phase policy when the profile is unitary and phase policy applies.

A spec/assurance-profile disagreement is a hard promotion error. A bridge/profile
wire-order or phase contradiction is also a hard promotion error. Experimental
packages may expose migration warnings so the corpus can be upgraded incrementally,
but those warnings identify packages that are not promotion-safe.

Every profile identifier used by a benchmark spec or assurance graph must resolve to
`schema/profiles/<id>.json`. Repository tests check this registry property over the
entire benchmark corpus.

## Toffoli

`toffoli_decomposition_equivalence` is already bound in both its spec and assurance
graph to `qspecbench.openqasm3.clifford_t_normalized.v1`, the normalized Clifford+T
profile introduced before this hardening pass. Its bridge declares
`openqasm_little_endian_wire_order` and exact phase normalization. This hardening work
preserves that binding rather than migrating it to the broader Python unitary v2
profile.

## Trust boundary

Executable profile conformance is necessary but not sufficient for a scientific
claim. It establishes which interpretation the evidence is about. It does not by
itself establish specification adequacy, theorem adequacy, external validity,
independent review, or reference-level maturity. Those remain separate obligations
in the assurance graph and promotion policy.
