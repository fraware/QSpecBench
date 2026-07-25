# kernel_checked_dynamic_denotation promotion history

## Resolved (2026-07-25)

This benchmark's `claimed_link` is now `kernel_checked_dynamic_denotation`. A dedicated
`formal_evidence_review` and `domain_semantics_review` were filed specifically evaluating the
denotation framing (distinct reviewed artifacts, commands, and accepted obligations from the
prior AST-semantics review; see `reviews/formal_review.json` / `reviews/domain_review.json`,
each hash-bound in `spec.yaml`). `expected/semantic_bridge.json` now pins
`claimed_link: kernel_checked_dynamic_denotation`, and
`evidence/dynamic_denotation_bridge_verify.result.json` (from
`write_dynamic_denotation_bridge_result`) is attached as passing evidence
(`ok: true`, `denotation_match: true`, `matrix_match: false`). The remainder of this note is
retained as the historical record of what blocked promotion before the new reviews landed.

## What is proved today

`QSpecBench.teleport_dynamic_feedforward_artifact_protocol_linked`
(`lean/QSpecBench/Teleportation.lean`) already proves, on the on-disk
`teleportation_with_feedforward.qasm` artifact:

- `ast.measurements` and `ast.controls` are hash-bound to the parsed CanonicalAst
  (`teleport_dynamic_feedforward_artifact_canonical_ast_bound`).
- `denoteCanonicalMeasures ast.measurements st (emptyClassicalReg 2) =
  teleportClassicalFromOutcomes c0 c1` — the parsed `measure` AST nodes denote the same
  `ClassicalReg` (`Measurement.writeZOutcome`) update as the relational teleportation model.
- `canonicalControlsToStmts ast.controls = some teleportFeedForwardIfStmts` — the parsed `if`
  AST nodes denote the same feed-forward Pauli-correction statements as the relational model.
- Composing both with the renormalized Bob-recovery theorems recovers the input state exactly.

This is substantively a measure/if-to-`Measurement`/`ClassicalReg` denotation binding, not a
bare CanonicalAst hash pin, and not gate-matrix codegen. `lean/QSpecBench/Quantum/
BridgeMetadata.lean` pins this as `bridge_teleport_dynamic_denotation_metadata`
(`claimedLink := "kernel_checked_dynamic_denotation"`), and `qspecbench.bridge_metadata.
verify_dynamic_denotation_bridge_metadata` / `qspecbench.verify_dynamic_ast_bridge.
verify_dynamic_denotation_bridge` mechanically check that pin (hash anchors, structural
"does the theorem statement actually invoke `denoteCanonicalMeasures`/`ClassicalReg`" markers,
and fail-closed AST retention of measurements/controls). Both pass today.

## Why `spec.yaml` still declares `kernel_checked_dynamic_ast_semantics`

`status.reviews.formal_evidence_review` and `status.reviews.domain_semantics_review` on this
benchmark are hash-bound (`review_artifact_sha256`) approvals of the **AST-semantics** framing
("Dynamic AST ABRC path — fail-closed mirror, DynamicAstBridgeMetadata, protocol-linked
theorem; matrix_match intentionally false"). They do not attest the stronger claim that the
CanonicalAst is bound to `Measurement`/`ClassicalReg` denotation specifically. Promoting the
`claimed_link` here to `kernel_checked_dynamic_denotation` would silently widen what the
existing reviewer sign-off is understood to cover.

Per repository policy (`.cursor` rule: never fake promotions), this claim label is not switched
until a **new** formal-evidence review and a **new** domain-semantics review are filed
specifically evaluating the denotation framing, each independently hash-bound to its own
review artifact. This is the same pattern documented in
`benchmarks/ai_formalization/notes/dual_review_blocker.md`: infrastructure and evidence being
honestly ready is not sufficient by itself to promote a claim — only new, real reviewer
sign-off is.

## What would unblock promotion

1. A `formal_evidence_review` from an independent formal reviewer confirming
   `teleport_dynamic_feedforward_artifact_protocol_linked` is the correct denotation witness
   (not just an AST-hash witness) for the on-disk artifact.
2. A `domain_semantics_review` from an independent domain reviewer confirming the
   `Measurement.writeZOutcome` / `ClassicalReg` model is the intended semantics for
   `measure`/`if` in this fragment, and that `matrix_match` remaining `false` is correctly
   documented.
3. Once both are `approved` and hash-bound, `spec.yaml.expected/semantic_bridge.json.
   claimed_link` may be changed to `kernel_checked_dynamic_denotation`, with
   `headline_claim_status.checked_under` updated accordingly and
   `evidence/dynamic_denotation_bridge_verify.result.json` (from
   `write_dynamic_denotation_bridge_result`) attached as passing evidence.

Until then this note documents the blocker; the underlying Lean proof and Python verification
machinery are both already fail-closed and available for use.
