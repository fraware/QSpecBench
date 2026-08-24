import QSpecBench.Teleportation

/-!
# Arbitrary pure-state dynamic teleportation contract

This module deliberately stops short of a density-operator / arbitrary mixed-state channel theorem.
It packages the strongest theorem justified by the QSpecBench amplitude semantics:

* the input is an arbitrary normalized pure qubit `α|0⟩ + β|1⟩` over `ℂ`;
* all four Alice outcomes have probability `1/4` and their probabilities sum to `1`;
* after the declared Pauli feed-forward correction and branch renormalization, Bob recovers
  exactly the input amplitudes for every outcome;
* the on-disk dynamic OpenQASM artifact is parsed by the fail-closed fragment parser into the
  declared gate, measurement, and classical-control AST, and the existing outcome semantics
  link those measurement/control nodes to the feed-forward model.

The result closes the basis-state/coherence gap while keeping the representation boundary explicit.
-/

namespace QSpecBench.Research.DynamicTeleportation

open QSpecBench
open QSpecBench.Quantum.Measurement
open QSpecBench.Quantum.OpenQASM3Parser

/-- Pure-state teleportation instrument correctness under the normalized-H amplitude semantics.

This theorem is intentionally an instrument-level pure-state result. It does **not** state a
mixed-state CPTP channel identity, complete positivity, or equality of arbitrary density operators.
-/
theorem arbitrary_pure_state_instrument_correct
    (α β : ℂ)
    (hN : Complex.normSq α + Complex.normSq β = 1) :
    (∀ c0 c1 : ZOutcome,
      aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) c0 c1 =
          (1 / 4 : ℝ) ∧
      (fun bit => (2 : ℂ) *
          bobAmpsC (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
        fun bit => if bit = 0 then α else β) ∧
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .one +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .one =
      (1 : ℝ) := by
  constructor
  · intro c0 c1
    exact ⟨
      teleport_normed_alice_povm_prob_quarter α β hN c0 c1,
      teleport_measure_correct_normed_renormalized α β c0 c1
    ⟩
  · exact teleport_normed_alice_povm_probs_sum_one α β hN

/-- Artifact-bound pure-state dynamic teleportation package.

The first conjunct binds the exact embedded bytes of the on-disk feed-forward artifact to the
fail-closed canonical AST expected by the dynamic semantics. The second and third conjuncts are
the arbitrary-pure-state instrument theorem. The final conjunct states the existing semantic link
for every declared measurement outcome: if the outcome stub returns `c0,c1`, the artifact's
measurement/control AST denotes the classical register and Pauli feed-forward used by the recovery
proof.

The measurement-outcome premise remains explicit because `measureZOutcomeAt8` is the project's
finite outcome stub, whereas the recovery/probability theorem is over arbitrary complex amplitudes.
This theorem therefore does not collapse those two representation layers into an unjustified
mixed-state measurement semantics.
-/
theorem artifact_bound_arbitrary_pure_state_instrument_correct
    (α β : ℂ)
    (hN : Complex.normSq α + Complex.normSq β = 1) :
    (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
      | .ok ast =>
          ast.gates =
              [{ op := "h", qubits := [1] },
               { op := "cx", qubits := [1, 2] },
               { op := "cx", qubits := [0, 1] },
               { op := "h", qubits := [0] }] ∧
            ast.measurements =
              [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
            ast.controls =
              [{ cIdx := 1, op := "x", qubits := [2] },
               { cIdx := 0, op := "z", qubits := [2] }] ∧
            ast.nQubits = 3
      | .error _ => False) ∧
    (∀ c0 c1 : ZOutcome,
      aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) c0 c1 =
          (1 / 4 : ℝ) ∧
      (fun bit => (2 : ℂ) *
          bobAmpsC (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
        fun bit => if bit = 0 then α else β) ∧
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .one +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .one =
      (1 : ℝ) ∧
    (∀ (c0 c1 : ZOutcome) (st : StateAmp8),
      measureZOutcomeAt8 st 0 = c0 →
      measureZOutcomeAt8 st 1 = c1 →
      (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
        | .ok ast =>
            ast.measurements =
                [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
              ast.controls =
                [{ cIdx := 1, op := "x", qubits := [2] },
                 { cIdx := 0, op := "z", qubits := [2] }] ∧
              denoteCanonicalMeasures ast.measurements st (emptyClassicalReg 2) =
                teleportClassicalFromOutcomes c0 c1 ∧
              canonicalControlsToStmts ast.controls = some teleportFeedForwardIfStmts
        | .error _ => False) ∧
        teleportMeasureCorrectViaFeedForward (embedTeleportInputC α β) c0 c1 =
          teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1 ∧
        ((fun bit => (2 : ℂ) * bobAmpsC
            (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
          fun bit => if bit = 0 then α else β)) := by
  have hInstrument := arbitrary_pure_state_instrument_correct α β hN
  refine ⟨teleport_dynamic_feedforward_artifact_canonical_ast_bound.1,
    hInstrument.1, hInstrument.2, ?_⟩
  intro c0 c1 st h0 h1
  exact teleport_dynamic_feedforward_artifact_protocol_linked α β c0 c1 st h0 h1

/-- Explicit scope boundary used by benchmark/trust-boundary documentation. -/
def scopeNote : String :=
  "arbitrary normalized pure qubit amplitudes over Complex; four-outcome projective instrument; " ++
  "on-disk dynamic OpenQASM AST bound to declared measurement/feed-forward semantics; " ++
  "not a mixed-state density-operator/CPTP channel theorem"

end QSpecBench.Research.DynamicTeleportation
