import QSpecBench.Legacy.CNOT
import QSpecBench.Quantum.Gate

/-!
# Two-qubit CNOT in the quantum gate library.
-/


namespace QSpecBench.Quantum

open QSpecBench (Matrix4 cnot4)

def cnot : Matrix4 := cnot4

theorem cnot_self_inverse (i j : Fin 4) : QSpecBench.mul4 cnot4 cnot4 i j = QSpecBench.id4 i j :=
  QSpecBench.cnot_mul_self i j

end QSpecBench.Quantum
