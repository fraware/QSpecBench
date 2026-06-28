/- QSpecBench evidence: measurement semantics scaffold anchor (not kernel-checked).

benchmark_id = "teleportation_preserves_state_up_to_pauli_correction"
obligation_id = "idealized_measurement_semantics"
status = "scaffold"

Links to `QSpecBench.Quantum.Measurement` for Fin 4 Z-basis / Z⊗Z branch checks.
Full projective update on arbitrary amplitudes remains operational in Python.
-/

import QSpecBench.Quantum.Measurement

#check QSpecBench.Quantum.Measurement.measure_state00_q0_zero
#check QSpecBench.Quantum.Measurement.joint_state00_zz
#check QSpecBench.Quantum.Measurement.syndrome00_from_state00
#check QSpecBench.Quantum.Measurement.measurementTrustBoundaryNote
