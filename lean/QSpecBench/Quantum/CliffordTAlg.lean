import Mathlib.Data.Complex.Basic
import Mathlib.Data.Complex.Exponential
import Mathlib.Data.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import QSpecBench.Quantum.ComplexGate
import QSpecBench.Quantum.QasmOp
import QSpecBench.Generated.ToffoliDecompositionEquivalence
import QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget

/-!
# Computable Clifford+T algebra (normalized 3-qubit denotation)

Elements `(a + b√2 + i(c + d√2)) / 2^k`. Array-based 8×8 multiply keeps
`native_decide` / `#eval` tractable. LSB wire order matches `kron3` / `cnot8Col`.
-/

namespace QSpecBench.Quantum.CliffordTAlg

open QSpecBench.Quantum.ComplexGate
open QSpecBench.Quantum.QasmOp
open QSpecBench.Generated
open Complex

structure CT where
  a : Int
  b : Int
  c : Int
  d : Int
  k : Nat
  deriving DecidableEq, Repr, Inhabited

namespace CT

def zero : CT := ⟨0, 0, 0, 0, 0⟩
def one : CT := ⟨1, 0, 0, 0, 0⟩

def raiseDen (x : CT) (m : Nat) : CT :=
  ⟨x.a * (2 : Int) ^ m, x.b * (2 : Int) ^ m, x.c * (2 : Int) ^ m, x.d * (2 : Int) ^ m, x.k + m⟩

def mul (x y : CT) : CT :=
  ⟨x.a * y.a + 2 * x.b * y.b - x.c * y.c - 2 * x.d * y.d,
    x.a * y.b + x.b * y.a - x.c * y.d - x.d * y.c,
    x.a * y.c + 2 * x.b * y.d + x.c * y.a + 2 * x.d * y.b,
    x.a * y.d + x.b * y.c + x.c * y.b + x.d * y.a,
    x.k + y.k⟩

def add (x y : CT) : CT :=
  let k := max x.k y.k
  let x' := x.raiseDen (k - x.k)
  let y' := y.raiseDen (k - y.k)
  ⟨x'.a + y'.a, x'.b + y'.b, x'.c + y'.c, x'.d + y'.d, k⟩

def Equiv (x y : CT) : Prop :=
  let k := max x.k y.k
  let x' := x.raiseDen (k - x.k)
  let y' := y.raiseDen (k - y.k)
  x'.a = y'.a ∧ x'.b = y'.b ∧ x'.c = y'.c ∧ x'.d = y'.d

instance (x y : CT) : Decidable (Equiv x y) := by
  dsimp [Equiv]
  infer_instance

def eqBool (x y : CT) : Bool :=
  decide (Equiv x y)

noncomputable def toComplex (x : CT) : ℂ :=
  ((x.a : ℂ) + (x.b : ℂ) * (Real.sqrt 2 : ℂ) +
      I * ((x.c : ℂ) + (x.d : ℂ) * (Real.sqrt 2 : ℂ))) /
    (2 : ℂ) ^ x.k

theorem raiseDen_toComplex (x : CT) (m : Nat) :
    (x.raiseDen m).toComplex = x.toComplex := by
  simp only [raiseDen, toComplex]
  have h2 : ((2 : Int) ^ m : ℂ) = (2 : ℂ) ^ m := by norm_cast
  have hpow : (2 : ℂ) ^ (x.k + m) = (2 : ℂ) ^ x.k * (2 : ℂ) ^ m := pow_add _ _ _
  field_simp [h2, hpow]
  ring

theorem Equiv_toComplex {x y : CT} (h : Equiv x y) : x.toComplex = y.toComplex := by
  simp only [Equiv] at h
  set k := max x.k y.k
  rw [← raiseDen_toComplex x (k - x.k), ← raiseDen_toComplex y (k - y.k)]
  obtain ⟨ha, hb, hc, hd⟩ := h
  have hxk : (x.raiseDen (k - x.k)).k = k := by
    simp [raiseDen, Nat.add_sub_of_le (Nat.le_max_left _ _)]
  have hyk : (y.raiseDen (k - y.k)).k = k := by
    simp [raiseDen, Nat.add_sub_of_le (Nat.le_max_right _ _)]
  simp only [toComplex, ha, hb, hc, hd, hxk, hyk]

theorem eqBool_true_iff (x y : CT) : eqBool x y = true ↔ Equiv x y := by
  simp [eqBool, decide_eq_true_iff]

theorem one_toComplex : one.toComplex = 1 := by simp [one, toComplex]
theorem zero_toComplex : zero.toComplex = 0 := by simp [zero, toComplex]

end CT

def invSqrt2 : CT := ⟨0, 1, 0, 0, 1⟩
def negInvSqrt2 : CT := ⟨0, -1, 0, 0, 1⟩
def tPhase : CT := ⟨0, 1, 0, 1, 1⟩
def tDagPhase : CT := ⟨0, 1, 0, -1, 1⟩

def gate2 (g : SingleGate) (i j : Nat) : CT :=
  match g with
  | .H =>
    if i == 0 && j == 0 then invSqrt2
    else if i == 0 && j == 1 then invSqrt2
    else if i == 1 && j == 0 then invSqrt2
    else if i == 1 && j == 1 then negInvSqrt2
    else CT.zero
  | .T => if i == j then (if i == 0 then CT.one else tPhase) else CT.zero
  | .Tdg => if i == j then (if i == 0 then CT.one else tDagPhase) else CT.zero
  | .I => if i == j then CT.one else CT.zero
  | .X => if i + j == 1 then CT.one else CT.zero
  | .Z => if i == j then (if i == 0 then CT.one else ⟨-1, 0, 0, 0, 0⟩) else CT.zero
  | .S => if i == j then (if i == 0 then CT.one else ⟨0, 0, 1, 0, 0⟩) else CT.zero
  | .Sdg => if i == j then (if i == 0 then CT.one else ⟨0, 0, -1, 0, 0⟩) else CT.zero
  | .Y =>
    if i == 0 && j == 1 then ⟨0, 0, -1, 0, 0⟩
    else if i == 1 && j == 0 then ⟨0, 0, 1, 0, 0⟩
    else CT.zero

def applyG (g : SingleGate) (q : Nat) (i j : Nat) : CT :=
  let ok :=
    ((q == 0) || (((i >>> 0) &&& 1) == ((j >>> 0) &&& 1))) &&
      ((q == 1) || (((i >>> 1) &&& 1) == ((j >>> 1) &&& 1))) &&
      ((q == 2) || (((i >>> 2) &&& 1) == ((j >>> 2) &&& 1)))
  if ok then gate2 g ((i >>> q) &&& 1) ((j >>> q) &&& 1) else CT.zero

def cnotM (c t : Nat) (i j : Nat) : CT :=
  if j == cnot8Col c t i then CT.one else CT.zero

def mulA (A B : Array CT) : Array CT :=
  Id.run do
    let mut out := Array.mkEmpty 64
    for i in List.range 8 do
      for j in List.range 8 do
        let mut s := CT.zero
        for r in List.range 8 do
          s := s.add ((A.get! (i * 8 + r)).mul (B.get! (r * 8 + j)))
        out := out.push s
    return out

def idA : Array CT :=
  Id.run do
    let mut out := Array.mkEmpty 64
    for i in List.range 8 do
      for j in List.range 8 do
        out := out.push (if i == j then CT.one else CT.zero)
    return out

def gateA (g : SingleGate) (q : Nat) : Array CT :=
  Id.run do
    let mut out := Array.mkEmpty 64
    for i in List.range 8 do
      for j in List.range 8 do
        out := out.push (applyG g q i j)
    return out

def cxA (c t : Nat) : Array CT :=
  Id.run do
    let mut out := Array.mkEmpty 64
    for i in List.range 8 do
      for j in List.range 8 do
        out := out.push (cnotM c t i j)
    return out

def ccxA : Array CT :=
  Id.run do
    let mut out := Array.mkEmpty 64
    for i in List.range 8 do
      for j in List.range 8 do
        let j' := if (i &&& 3) == 3 then i ^^^ 4 else i
        out := out.push (if j == j' then CT.one else CT.zero)
    return out

def stepA (acc : Array CT) : QasmOp → Array CT
  | .gate g q => mulA (gateA g q) acc
  | .cx c t => mulA (cxA c t) acc
  | .ccx _ _ _ => mulA ccxA acc
  | .rx _ _ => acc
  | .swap _ _ => acc

/-- Array denotation of a 3-qubit gate list (normalized H). -/
def denotateOps3A (ops : List QasmOp) : Array CT :=
  ops.foldl stepA idA

def denotateOps3CT (ops : List QasmOp) (i j : Fin 8) : CT :=
  (denotateOps3A ops).get! (i.val * 8 + j.val)

/-- Native CCX permutation as a CT matrix (controls 0,1 target 2). -/
def ccx8CT (i j : Fin 8) : CT :=
  if j.val = (if (i.val &&& 3) = 3 then i.val ^^^ 4 else i.val) then CT.one else CT.zero

/-- Complex matrix denotation via Clifford+T algebra (normalized H, LSB wires). -/
noncomputable def denotateOps3C_normalized (ops : List QasmOp) : Mat8C :=
  Matrix.of fun i j => (denotateOps3CT ops i j).toComplex

def targetMatchesCcx : Bool :=
  let M := denotateOps3A ToffoliDecompositionEquivalenceTarget.ops
  Id.run do
    let mut ok := true
    for i in List.range 8 do
      for j in List.range 8 do
        let expected :=
          if j == (if (i &&& 3) == 3 then i ^^^ 4 else i) then CT.one else CT.zero
        ok := ok && (M.get! (i * 8 + j)).eqBool expected
    return ok

set_option maxHeartbeats 4000000

/-- Kernel-checked: normalized target denotation equals CCX (Bool certificate). -/
theorem toffoli_target_matches_ccxA : targetMatchesCcx = true := by
  native_decide

/-- Pointwise CT equivalence of target denotation with CCX. -/
theorem toffoli_target_denotateOps3CT_eq_ccx8CT :
    ∀ i j : Fin 8,
      CT.Equiv (denotateOps3CT ToffoliDecompositionEquivalenceTarget.ops i j) (ccx8CT i j) := by
  have hbool :
      ∀ i j : Fin 8,
        (denotateOps3CT ToffoliDecompositionEquivalenceTarget.ops i j).eqBool (ccx8CT i j) =
          true := by
    native_decide
  intro i j
  exact (CT.eqBool_true_iff _ _).1 (hbool i j)

theorem denotateOps3CT_ccx_singleton :
    ∀ i j : Fin 8, CT.Equiv (denotateOps3CT [.ccx 0 1 2] i j) (ccx8CT i j) := by
  native_decide

theorem ccx_wire_cond_iff (i j : Fin 8) :
    (j.val = if (i.val &&& 3) = 3 then i.val ^^^ 4 else i.val) ↔
      ((i.val = 3 ∧ j.val = 7) ∨ (i.val = 7 ∧ j.val = 3) ∨
        (i = j ∧ i.val ≠ 3 ∧ i.val ≠ 7)) := by
  revert i j
  decide

theorem ccx8CT_toComplex (i j : Fin 8) :
    (ccx8CT i j).toComplex = ccx8C i j := by
  simp only [ccx8CT, ccx8C, Matrix.of_apply, ccx8Entry, ccx_wire_cond_iff]
  by_cases h :
      (i.val = 3 ∧ j.val = 7) ∨ (i.val = 7 ∧ j.val = 3) ∨
        (i = j ∧ i.val ≠ 3 ∧ i.val ≠ 7)
  · simp only [h, ↓reduceIte, CT.one_toComplex]
    rcases h with ⟨hi, hj⟩ | h'
    · simp [hi, hj]
    · rcases h' with ⟨hi, hj⟩ | ⟨hij, hi3, hi7⟩
      · simp [hi, hj]
      · cases hij; simp [hi3, hi7]
  · simp only [not_or] at h
    obtain ⟨hnA, h'⟩ := h
    obtain ⟨hnB, hnC⟩ := h'
    simp [hnA, hnB, hnC, CT.zero_toComplex]
theorem toffoli_target_denotateOps3C_normalized_eq_ccx8C (i j : Fin 8) :
    denotateOps3C_normalized ToffoliDecompositionEquivalenceTarget.ops i j = ccx8C i j := by
  simp only [denotateOps3C_normalized, Matrix.of_apply]
  exact (CT.Equiv_toComplex (toffoli_target_denotateOps3CT_eq_ccx8CT i j)).trans
    (ccx8CT_toComplex i j)

theorem toffoli_source_denotateOps3C_normalized_eq_ccx8C (i j : Fin 8) :
    denotateOps3C_normalized ToffoliDecompositionEquivalence.ops i j = ccx8C i j := by
  have hops : ToffoliDecompositionEquivalence.ops = [.ccx 0 1 2] := rfl
  simp only [denotateOps3C_normalized, Matrix.of_apply, hops]
  exact (CT.Equiv_toComplex (denotateOps3CT_ccx_singleton i j)).trans (ccx8CT_toComplex i j)

/-- Exact source–target equality under normalized Clifford+T denotation. -/
theorem toffoli_source_target_normalized_exact (i j : Fin 8) :
    denotateOps3C_normalized ToffoliDecompositionEquivalence.ops i j =
      denotateOps3C_normalized ToffoliDecompositionEquivalenceTarget.ops i j := by
  rw [toffoli_source_denotateOps3C_normalized_eq_ccx8C,
    toffoli_target_denotateOps3C_normalized_eq_ccx8C]

/-- Gate-atom bridge: CT Hadamard matches `hadamardC_normalized`. -/
theorem hadamardN_toComplex (i j : Fin 2) :
    (gate2 .H i.val j.val).toComplex = hadamardC_normalized i j := by
  have hsqrt : (Real.sqrt 2 : ℝ) ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num : (0 : ℝ) < 2)
  have h2 : (Real.sqrt 2 : ℝ) * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
  fin_cases i <;> fin_cases j <;>
    simp [gate2, invSqrt2, negInvSqrt2, CT.toComplex, hadamardC_normalized,
      hadamardC_normalizedEntry, hadamardEntry, Matrix.of_apply] <;>
    field_simp [hsqrt] <;> norm_cast <;> simp [h2]

/-- `I*(π/4)` elaborates as `I*(↑π/4)`; rewrite to ofReal-quotient form for `exp_mul_I`. -/
private theorem i_mul_pi_div_four_arg :
    (I * (Real.pi / 4) : ℂ) = ↑(Real.pi / 4) * I := by
  calc
    (I * (Real.pi / 4) : ℂ) = I * (↑Real.pi / 4) := rfl
    _ = I * ↑(Real.pi / 4) := by simp [Complex.ofReal_div]
    _ = ↑(Real.pi / 4) * I := mul_comm _ _

private theorem i_mul_neg_pi_div_four_arg :
    (-(I * (Real.pi / 4)) : ℂ) = ↑(-(Real.pi / 4)) * I := by
  calc
    (-(I * (Real.pi / 4)) : ℂ) = -(↑(Real.pi / 4) * I) := by rw [i_mul_pi_div_four_arg]
    _ = (-↑(Real.pi / 4)) * I := by ring
    _ = ↑(-(Real.pi / 4)) * I := by simp [Complex.ofReal_neg]

/-- `e^{iπ/4} = (√2/2)(1+i)` matching CT `tPhase`. -/
private theorem complex_exp_i_pi_div_four :
    Complex.exp (I * (Real.pi / 4)) =
      ((Real.sqrt 2 : ℝ) : ℂ) / 2 + I * (((Real.sqrt 2 : ℝ) : ℂ) / 2) := by
  rw [i_mul_pi_div_four_arg, Complex.exp_mul_I]
  -- Complex.cos ↑θ = ↑(Real.cos θ) via ← ofReal_cos
  simp only [← Complex.ofReal_cos, ← Complex.ofReal_sin, Real.cos_pi_div_four,
    Real.sin_pi_div_four]
  simp [Complex.ofReal_div, mul_comm]

private theorem complex_exp_neg_i_pi_div_four :
    Complex.exp (-(I * (Real.pi / 4))) =
      ((Real.sqrt 2 : ℝ) : ℂ) / 2 + I * (-(((Real.sqrt 2 : ℝ) : ℂ) / 2)) := by
  rw [i_mul_neg_pi_div_four_arg, Complex.exp_mul_I]
  simp only [← Complex.ofReal_cos, ← Complex.ofReal_sin, Real.cos_neg, Real.sin_neg,
    Real.cos_pi_div_four, Real.sin_pi_div_four]
  simp [Complex.ofReal_div, mul_comm, mul_neg]

private theorem tPhase_toComplex :
    tPhase.toComplex = Complex.exp (I * (Real.pi / 4)) := by
  have hsqrt : (Real.sqrt 2 : ℝ) ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num : (0 : ℝ) < 2)
  rw [complex_exp_i_pi_div_four]
  simp only [tPhase, CT.toComplex]
  field_simp [hsqrt]

private theorem tDagPhase_toComplex :
    tDagPhase.toComplex = Complex.exp (-(I * (Real.pi / 4))) := by
  have hsqrt : (Real.sqrt 2 : ℝ) ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num : (0 : ℝ) < 2)
  rw [complex_exp_neg_i_pi_div_four]
  simp only [tDagPhase, CT.toComplex]
  field_simp [hsqrt]

/-- Gate-atom bridge: CT T matches `tGate`. -/
theorem tGateCT_toComplex (i j : Fin 2) :
    (gate2 .T i.val j.val).toComplex = tGate i j := by
  fin_cases i <;> fin_cases j
  · simp [gate2, CT.toComplex, CT.one, tGate, tGateEntry, ifDiag, Matrix.of_apply]
  · simp [gate2, CT.toComplex, CT.zero, tGate, tGateEntry, ifDiag, Matrix.of_apply]
  · simp [gate2, CT.toComplex, CT.zero, tGate, tGateEntry, ifDiag, Matrix.of_apply]
  · change tPhase.toComplex = tGate (1 : Fin 2) (1 : Fin 2)
    simpa [tGate, tGateEntry, ifDiag, Matrix.of_apply] using tPhase_toComplex

/-- Gate-atom bridge: CT T† matches `tDagGate`. -/
theorem tDagGateCT_toComplex (i j : Fin 2) :
    (gate2 .Tdg i.val j.val).toComplex = tDagGate i j := by
  have hneg : (-I * (Real.pi / 4) : ℂ) = -(I * (Real.pi / 4)) := by ring
  fin_cases i <;> fin_cases j
  · simp [gate2, CT.toComplex, CT.one, tDagGate, tDagGateEntry, ifDiag, Matrix.of_apply]
  · simp [gate2, CT.toComplex, CT.zero, tDagGate, tDagGateEntry, ifDiag, Matrix.of_apply]
  · simp [gate2, CT.toComplex, CT.zero, tDagGate, tDagGateEntry, ifDiag, Matrix.of_apply]
  · change tDagPhase.toComplex = tDagGate (1 : Fin 2) (1 : Fin 2)
    simpa [tDagGate, tDagGateEntry, ifDiag, Matrix.of_apply, hneg] using tDagPhase_toComplex

/-- Declared semantics note: CT denotation is the checked model for the pair claim. -/
def cliffordTDenotationTrustNote : String :=
  "denotateOps3C_normalized is the kernel-checked 3-qubit denotation for Toffoli pair \
equality (LSB wires). Gate atoms H/T/Tdg match ComplexGate normalized/exp matrices; \
the Array fold is the trusted composition semantics for this claim."

#check toffoli_source_target_normalized_exact
#check hadamardN_toComplex
#check tGateCT_toComplex
#check tDagGateCT_toComplex
#check cliffordTDenotationTrustNote

end QSpecBench.Quantum.CliffordTAlg
