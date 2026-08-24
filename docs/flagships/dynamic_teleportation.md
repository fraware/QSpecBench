# Flagship specification: arbitrary-input dynamic teleportation

Status: **required scientific target; not yet a completed proof.** See issue #17.

The current dynamic-circuit benchmarks are intentionally narrower than this target. This document prevents those narrower results from being rhetorically expanded.

## Proposition target

For an arbitrary single-qubit input state (pure-state formulation only if proved sufficient, otherwise density operator), executing the pinned dynamic teleportation artifact under a declared measurement/classical-control semantic profile yields an output subsystem equal to the input state after the protocol's classically controlled Pauli correction, with the declared treatment of classical outcomes and discarded subsystems.

## Required semantic objects

- arbitrary input state/domain and normalization assumptions;
- tensor/subsystem ordering;
- unitary gates;
- projective measurement or measurement instrument semantics;
- outcome probabilities and post-measurement states;
- classical register update semantics;
- `if`/feed-forward semantics;
- reset semantics if reset is used;
- partial trace/discard semantics;
- final output-subsystem equality or declared metric.

## Required obligations

1. `artifact_parse_dynamic` — artifact parses fail-closed into the declared dynamic AST.
2. `dynamic_ast_semantics` — every used dynamic construct has formal semantics.
3. `measurement_instrument_valid` — measurement branches/probabilities/post-states are well defined.
4. `classical_register_semantics` — measurement results bind the correct classical bits.
5. `feedforward_branch_semantics` — each classical branch applies the intended correction.
6. `branch_completeness` — all possible measurement outcomes are covered.
7. `output_subsystem_relation` — after correction, the output subsystem equals the arbitrary input state/channel according to the exact proposition.
8. `artifact_to_theorem_binding` — the theorem is about the pinned artifact, not only a hand-authored nearby circuit term.

## Non-substitutes

The following do not satisfy the flagship by themselves:
- computational-basis-only cases;
- a measure-free unitary prefix theorem;
- matrix equality that omits measurement and classical control;
- finite simulation of selected input states;
- syntax parsing alone.

## Promotion gate

A promoted flagship requires closed assurance graph, executable dynamic semantic profile, artifact binding, kernel-checked core theorem, residual assumptions, authenticated dual review, and exact-head release verification.
