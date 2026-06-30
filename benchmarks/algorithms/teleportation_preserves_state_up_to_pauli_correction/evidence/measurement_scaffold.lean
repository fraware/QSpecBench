/- QSpecBench evidence: measurement semantics scaffold anchor (not full reference_claim).

benchmark_id = "teleportation_preserves_state_up_to_pauli_correction"
obligation_id = "idealized_measurement_semantics"
status = "scaffold"

Links to `QSpecBench.Quantum.Measurement` for Fin 4/8 Z-basis projective updates,
Pauli X/Z correction table, and basis-state teleportation lemma chains.
-/

import QSpecBench.Quantum.Measurement

#check QSpecBench.Quantum.Measurement.teleport_basis00_lemma_chain
#check QSpecBench.Quantum.Measurement.teleport_basis01_lemma_chain
#check QSpecBench.Quantum.Measurement.teleport_basis000_lemma_chain
#check QSpecBench.Quantum.Measurement.teleport_basis001_lemma_chain
#check QSpecBench.Quantum.Measurement.measureZ8
#check QSpecBench.Quantum.Measurement.applyPauliCorrection8
#check QSpecBench.Quantum.Measurement.measurementTrustBoundaryNote

/-- Basis-state input |0⟩ yields Z-outcome zero on qubit 0 (Fin 8 scaffold). -/
example : QSpecBench.Quantum.Measurement.measureZOutcomeQ QSpecBench.Quantum.Measurement.state000 0 =
    QSpecBench.Quantum.Measurement.ZOutcome.zero := by
  exact QSpecBench.Quantum.Measurement.measure_state000_q0_zero

/-- Basis-state input |1⟩ on wire 0 yields Z-outcome one (Fin 8 scaffold). -/
example : QSpecBench.Quantum.Measurement.measureZOutcomeQ QSpecBench.Quantum.Measurement.state001 0 =
    QSpecBench.Quantum.Measurement.ZOutcome.one := by
  exact QSpecBench.Quantum.Measurement.measure_state001_q0_one

/-- Fin 8 measureZ branch weight + X correction for syndrome (0,1). -/
example :
    (QSpecBench.Quantum.Measurement.measureZ8 QSpecBench.Quantum.Measurement.state001 0).weightOne = 1 ∧
      QSpecBench.Quantum.Measurement.applyPauliCorrection8
          QSpecBench.Quantum.Measurement.ZOutcome.zero
          QSpecBench.Quantum.Measurement.ZOutcome.one
          QSpecBench.Quantum.Measurement.state001 =
        QSpecBench.Quantum.Measurement.state101 := by
  exact QSpecBench.Quantum.Measurement.teleport_basis001_lemma_chain

/-- Fin 8 identity correction preserves |000⟩ after measureZ. -/
example :
    (QSpecBench.Quantum.Measurement.measureZ8 QSpecBench.Quantum.Measurement.state000 0).weightZero = 1 ∧
      QSpecBench.Quantum.Measurement.applyPauliCorrection8
          QSpecBench.Quantum.Measurement.ZOutcome.zero
          QSpecBench.Quantum.Measurement.ZOutcome.zero
          QSpecBench.Quantum.Measurement.state000 =
        QSpecBench.Quantum.Measurement.state000 := by
  exact ⟨QSpecBench.Quantum.Measurement.measureZ8_state000_branch_weights.1,
    QSpecBench.Quantum.Measurement.pauli_correction8_I_state000⟩
