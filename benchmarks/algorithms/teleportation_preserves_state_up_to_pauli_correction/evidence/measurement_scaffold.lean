/- QSpecBench evidence: measurement semantics scaffold anchor (not kernel-checked).

benchmark_id = "teleportation_preserves_state_up_to_pauli_correction"
obligation_id = "idealized_measurement_semantics"
status = "scaffold"

Links to `QSpecBench.Quantum.Measurement` for Fin 4 Z-basis / Z⊗Z branch checks and
Fin 8 basis-state Z outcomes on the input wire (q0). Full projective update on
arbitrary amplitudes remains operational in Python.
-/

import QSpecBench.Quantum.Measurement

#check QSpecBench.Quantum.Measurement.measure_state00_q0_zero
#check QSpecBench.Quantum.Measurement.joint_state00_zz
#check QSpecBench.Quantum.Measurement.syndrome00_from_state00
#check QSpecBench.Quantum.Measurement.measure_state000_q0_zero
#check QSpecBench.Quantum.Measurement.measure_state001_q0_one
#check QSpecBench.Quantum.Measurement.measurementTrustBoundaryNote

/-- Basis-state input |0⟩ yields Z-outcome zero on qubit 0 (Fin 8 scaffold). -/
example : QSpecBench.Quantum.Measurement.measureZOutcomeQ QSpecBench.Quantum.Measurement.state000 0 =
    QSpecBench.Quantum.Measurement.ZOutcome.zero := by
  exact QSpecBench.Quantum.Measurement.measure_state000_q0_zero

/-- Basis-state input |1⟩ on wire 0 yields Z-outcome one (Fin 8 scaffold). -/
example : QSpecBench.Quantum.Measurement.measureZOutcomeQ QSpecBench.Quantum.Measurement.state001 0 =
    QSpecBench.Quantum.Measurement.ZOutcome.one := by
  exact QSpecBench.Quantum.Measurement.measure_state001_q0_one
