import QSpecBench.Teleportation

/-!
# Arbitrary pure-state dynamic teleportation contract

This module deliberately stops short of a density-operator / arbitrary mixed-state channel theorem.
It packages the strongest theorem already justified by the QSpecBench amplitude semantics:

* the input is an arbitrary normalized pure qubit `α|0⟩ + β|1⟩` over `ℂ`;
* all four Alice outcomes have probability `1/4` and their probabilities sum to `1`;
* after the declared Pauli feed-forward correction and branch renormalization, Bob recovers
  exactly the input amplitudes for every outcome.

The result closes the basis-state/coherence gap while keeping the representation boundary explicit.
-/

namespace QSpecBench.Research.DynamicTeleportation

open QSpecBench
open QSpecBench.Quantum.Measurement

/-- Pure-state teleportation instrument correctness under the normalized-H amplitude semantics.

This theorem is intentionally an instrument-level pure-state result.  It does **not** state a
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

/-- Explicit scope boundary used by benchmark/trust-boundary documentation. -/
def scopeNote : String :=
  "arbitrary normalized pure qubit amplitudes over Complex; four-outcome projective instrument; " ++
  "declared Pauli feed-forward; not a mixed-state density-operator/CPTP channel theorem"

end QSpecBench.Research.DynamicTeleportation
