import QSpecBench.Teleportation
import QSpecBench.Quantum.BridgeMetadata

/-!
Denotation-bound ABRC evidence anchor (`kernel_checked_dynamic_denotation`): the on-disk
`teleportation_with_feedforward.qasm` measure/if CanonicalAst is bound to
`Measurement.writeZOutcome` / `ClassicalReg` denotation, not a bare AST-hash pin and not
gate-matrix codegen. Distinct from `evidence/dynamic_feedforward_bridge.lean`, which anchors
the weaker `kernel_checked_dynamic_ast_semantics` framing of the same theorem.
-/

#check QSpecBench.teleport_dynamic_feedforward_artifact_protocol_linked
#check QSpecBench.denoteCanonicalMeasures
#check QSpecBench.canonicalControlsToStmts
#check QSpecBench.denoteCanonicalMeasures_teleport_eq_classical
#check QSpecBench.canonicalControlsToStmts_teleport_feedforward
#check QSpecBench.Quantum.BridgeMetadata.bridge_teleport_dynamic_denotation_metadata
