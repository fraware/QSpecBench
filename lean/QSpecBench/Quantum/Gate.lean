import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.Matrix

/-!
# Single-qubit gates matching OpenQASM `stdgates` integer scaffold.
-/


namespace QSpecBench.Quantum

open QSpecBench (Matrix2)

def identityGate : Matrix2 := id2
def pauliX : Matrix2 := pauliX2
def pauliY (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨1, _⟩ => -1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | _, _ => 0
def pauliZ : Matrix2 := pauliZ2
def hadamard : Matrix2 := hadamard2

end QSpecBench.Quantum
