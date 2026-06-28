import Mathlib.Data.Real.Basic

namespace QSpecBench.Quantum.QasmOp

inductive SingleGate where
  | I | X | Y | Z | H | S | T | Sdg | Tdg
  deriving DecidableEq, Repr

inductive QasmOp where
  | gate (g : SingleGate) (q : Nat)
  | cx (control target : Nat)
  | rx (θ : ℝ) (q : Nat)
  | ccx (c0 c1 target : Nat)
  | swap (a b : Nat)

end QSpecBench.Quantum.QasmOp
