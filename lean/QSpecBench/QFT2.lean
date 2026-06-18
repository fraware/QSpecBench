/-!
# Two-qubit QFT scaffold for `qft_inverse_qft_small_instance`.

Circuit model: H on q[0], CX(q[0],q[1]), H on q[0] — the declared OpenQASM scaffold.
On this instance the inverse circuit equals the forward circuit (H and CX are self-inverse).
We prove `qft2 * qft2 = 4 • I` in the unnormalized integer model (two H gates contribute 2²).
-/

import QSpecBench.Matrix
import QSpecBench.Pauli
import QSpecBench.CNOT

namespace QSpecBench

open QSpecBench (Matrix4 mul4 id4 scale4 kron2I)

def qft2 (i j : Fin 4) : Int :=
  mul4 (kron2I hadamard2) (mul4 cnot4 (kron2I hadamard2)) i j

def invqft2 := qft2

/-- QFT composed with inverse QFT equals 4 • I on the unnormalized model. -/
theorem qft2_mul_invqft2 (i j : Fin 4) : mul4 qft2 invqft2 i j = scale4 4 id4 i j := by
  funext i j
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench
