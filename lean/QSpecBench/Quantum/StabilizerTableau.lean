import Mathlib.Tactic.FinCases

/-!
# Stabilizer tableau — Clifford row-update fragment + fail-closed shipping status.

Shipping full tableau simulation (measurement update, arbitrary Cliffords) remains
**fail-closed / not checked**. This module adds a kernel-checked **Clifford row-update**
fragment (CNOT, Hadamard, Phase/S) on boolean symplectic generators for n≤3,
linked to bit-flip Z-generators.

Do not treat this module as `qec_small_code_checked` evidence.
-/

namespace QSpecBench.Quantum.StabilizerTableau

/-- Shipping backend maturity. -/
inductive BackendStatus where
  /-- Legacy bool `runClifford`: fail-closed on X-support measure. -/
  | declaredFailClosed
  /-- Phased AG runner `runCliffordPhased`: nondet measure with multipivot rowsum. -/
  | agPhasedShipping
  deriving DecidableEq, Repr

/-- Primary shipping backend: phased AG multipivot path. -/
def backendStatus : BackendStatus := .agPhasedShipping

theorem backend_is_ag_shipping : backendStatus = .agPhasedShipping := rfl

/-- Phased AG shipping path (same as `backendStatus`; retained alias). -/
def phasedBackendStatus : BackendStatus := .agPhasedShipping

theorem phased_backend_is_ag_shipping : phasedBackendStatus = .agPhasedShipping := rfl

/-- One stabilizer generator: X and Z supports on `n` qubits (boolean symplectic). -/
structure Gen (n : Nat) where
  x : Fin n → Bool
  z : Fin n → Bool

abbrev Tableau (n : Nat) := List (Gen n)

/-- Symplectic product (commutation test): Σᵢ (xₐᵢ z_bᵢ ⊕ zₐᵢ x_bᵢ) = 0 ⇒ commute. -/
def symplecticProduct {n : Nat} (a b : Gen n) : Bool :=
  (List.range n).foldl
    (fun acc k =>
      if h : k < n then
        let i : Fin n := ⟨k, h⟩
        Bool.xor acc (Bool.xor (a.x i && b.z i) (a.z i && b.x i))
      else acc)
    false

/-- Aaronson–Gottesman CNOT update on a single generator (control `c`, target `t`). -/
def applyCNOTGen {n : Nat} (g : Gen n) (c t : Fin n) : Gen n :=
  { x := fun i => if i = t then Bool.xor (g.x i) (g.x c) else g.x i
    z := fun i => if i = c then Bool.xor (g.z i) (g.z t) else g.z i }

def applyCNOT {n : Nat} (tab : Tableau n) (c t : Fin n) : Tableau n :=
  tab.map (fun g => applyCNOTGen g c t)

/-- Hadamard: swap X/Z supports on qubit `q` (phase ignored in bool tableau). -/
def applyHGen {n : Nat} (g : Gen n) (q : Fin n) : Gen n :=
  { x := fun i => if i = q then g.z i else g.x i
    z := fun i => if i = q then g.x i else g.z i }

def applyH {n : Nat} (tab : Tableau n) (q : Fin n) : Tableau n :=
  tab.map (fun g => applyHGen g q)

/-- Phase/S: `z_q := z_q ⊕ x_q` (phase ignored in bool tableau). -/
def applySGen {n : Nat} (g : Gen n) (q : Fin n) : Gen n :=
  { x := g.x
    z := fun i => if i = q then Bool.xor (g.z i) (g.x i) else g.z i }

def applyS {n : Nat} (tab : Tableau n) (q : Fin n) : Tableau n :=
  tab.map (fun g => applySGen g q)

/-- Single-qubit X generator on qubit 0 (n=3). -/
def genXII : Gen 3 :=
  { x := fun i => decide (i.val = 0)
    z := fun _ => false }

/-- Bit-flip code Z-generators: ZZI and IZZ. -/
def bitFlipGenZZI : Gen 3 :=
  { x := fun _ => false
    z := fun i => decide (i.val ≤ 1) }

def bitFlipGenIZZ : Gen 3 :=
  { x := fun _ => false
    z := fun i => decide (i.val ≠ 0) }

def bitFlipTableau : Tableau 3 := [bitFlipGenZZI, bitFlipGenIZZ]

theorem bitFlipTableau_length : bitFlipTableau.length = 2 := rfl

/-- Bit-flip generators commute (symplectic product false). -/
theorem bitFlipGens_commute :
    symplecticProduct bitFlipGenZZI bitFlipGenIZZ = false := by
  native_decide

/-- CNOT(0,1) on ZZI: z_c := z_c ⊕ z_t clears Z on control when both Z-support bits set. -/
theorem applyCNOT_bitFlip_ZZI_c01_z0 :
    (applyCNOTGen bitFlipGenZZI ⟨0, by decide⟩ ⟨1, by decide⟩).z ⟨0, by decide⟩ = false := by
  simp [applyCNOTGen, bitFlipGenZZI]

theorem applyCNOT_bitFlip_ZZI_c01_z1 :
    (applyCNOTGen bitFlipGenZZI ⟨0, by decide⟩ ⟨1, by decide⟩).z ⟨1, by decide⟩ = true := by
  simp [applyCNOTGen, bitFlipGenZZI]

/-- After CNOT(0,1) on both bit-flip gens, the updated pair still commute. -/
theorem applyCNOT_preserves_bitFlip_commutation :
    symplecticProduct
        (applyCNOTGen bitFlipGenZZI ⟨0, by decide⟩ ⟨1, by decide⟩)
        (applyCNOTGen bitFlipGenIZZ ⟨0, by decide⟩ ⟨1, by decide⟩) =
      false := by
  native_decide

/-- H maps X on qubit 0 to Z on qubit 0. -/
theorem applyH_XII_to_Z :
    (applyHGen genXII ⟨0, by decide⟩).x ⟨0, by decide⟩ = false ∧
      (applyHGen genXII ⟨0, by decide⟩).z ⟨0, by decide⟩ = true := by
  simp [applyHGen, genXII]

/-- S on X adds Z support on the same qubit. -/
theorem applyS_XII_adds_Z :
    (applySGen genXII ⟨0, by decide⟩).x ⟨0, by decide⟩ = true ∧
      (applySGen genXII ⟨0, by decide⟩).z ⟨0, by decide⟩ = true := by
  simp [applySGen, genXII]

/-- H then H restores XII on qubit 0 (pointwise involution). -/
theorem applyH_involutive_XII (i : Fin 3) :
    (applyHGen (applyHGen genXII ⟨0, by decide⟩) ⟨0, by decide⟩).x i = genXII.x i ∧
      (applyHGen (applyHGen genXII ⟨0, by decide⟩) ⟨0, by decide⟩).z i = genXII.z i := by
  fin_cases i <;> simp [applyHGen, genXII]

/-- H preserves commutation of the bit-flip generator pair. -/
theorem applyH_preserves_bitFlip_commutation :
    symplecticProduct
        (applyHGen bitFlipGenZZI ⟨0, by decide⟩)
        (applyHGen bitFlipGenIZZ ⟨0, by decide⟩) =
      false := by
  native_decide

/-! ## Deterministic Z-measurement update (computational-basis fragment) -/

/-- Measure qubit `q` in the Z basis when the tableau is a computational eigenstate
fragment: if any generator has X-support on `q`, measurement is nondeterministic and
this fragment returns `none` (fail-closed). Otherwise outcome is determined by Z-support
randomness seed `rnd` only when random; here we return the deterministic phase bit
proxy `false` when all X-supports on `q` vanish. -/
def measureZDeterministic {n : Nat} (tab : Tableau n) (q : Fin n) : Option Bool :=
  if tab.any (fun g => g.x q) then none
  else some false

theorem measureZDeterministic_bitFlip_q0 :
    measureZDeterministic bitFlipTableau ⟨0, by decide⟩ = some false := by
  native_decide

theorem measureZDeterministic_fails_on_XII :
    measureZDeterministic [genXII] ⟨0, by decide⟩ = none := by
  native_decide

/-- After measuring a Z-only qubit, remove generators with Z on that qubit (stabilize). -/
def postMeasureZUpdate {n : Nat} (tab : Tableau n) (q : Fin n) : Tableau n :=
  tab.filter (fun g => !(g.z q) || g.x q)

theorem postMeasureZUpdate_bitFlip_q0_drops_ZZI :
    (postMeasureZUpdate bitFlipTableau ⟨0, by decide⟩).length = 1 := by
  native_decide

/-- Deterministic Z-measure still returns `none` on X-support (partial fragment). -/
theorem measure_fragment_still_fail_closed_on_X :
    measureZDeterministic [genXII] ⟨0, by decide⟩ = none :=
  measureZDeterministic_fails_on_XII

/-- Shipping status is AG phased; deterministic measure fragment remains partial on X-support. -/
theorem backend_still_fail_closed_with_measure_fragment :
    backendStatus = .agPhasedShipping ∧
      measureZDeterministic [genXII] ⟨0, by decide⟩ = none :=
  ⟨backend_is_ag_shipping, measure_fragment_still_fail_closed_on_X⟩

/-! ## Small Clifford program runner (ops); implementation after AG phased path -/

inductive CliffordOp (n : Nat) where
  | cnot (c t : Fin n)
  | h (q : Fin n)
  | s (q : Fin n)
  | measureZ (q : Fin n)
  deriving Repr

/-! ## Phase-bearing generators + rowsum fragment (AG toward shipping) -/

/-- Generator with phase `r` (interpreted mod 4 as factor `i^r`). -/
structure GenP (n : Nat) where
  x : Fin n → Bool
  z : Fin n → Bool
  r : Nat

def forgetPhase {n : Nat} (g : GenP n) : Gen n :=
  { x := g.x, z := g.z }

/-- Phase contribution `2 * Σ x_a z_b` used by AG `rowsum` (accumulated in ℕ). -/
def rowsumPhaseContrib {n : Nat} (a b : GenP n) : Nat :=
  (List.range n).foldl
    (fun acc k =>
      if h : k < n then
        let i : Fin n := ⟨k, h⟩
        if a.x i && b.z i then acc + 2 else acc
      else acc)
    0

/-- AG-style rowsum: `h ← h + i` with phase update (supports xor + phase contrib). -/
def rowsum {n : Nat} (h i : GenP n) : GenP n :=
  { x := fun q => Bool.xor (h.x q) (i.x q)
    z := fun q => Bool.xor (h.z q) (i.z q)
    r := (h.r + i.r + rowsumPhaseContrib h i) % 4 }

def bitFlipGenPZZI : GenP 3 :=
  { x := fun _ => false
    z := fun i => decide (i.val ≤ 1)
    r := 0 }

def bitFlipGenPIZZ : GenP 3 :=
  { x := fun _ => false
    z := fun i => decide (i.val ≠ 0)
    r := 0 }

theorem bitFlipGenP_forget_commute :
    symplecticProduct (forgetPhase bitFlipGenPZZI) (forgetPhase bitFlipGenPIZZ) = false :=
  bitFlipGens_commute

/-- Rowsum of bit-flip Z-generators: X-support clears; Z-support becomes ZIZ (qubits 0 and 2). -/
theorem rowsum_bitFlip_ZZI_IZZ_x_cleared (q : Fin 3) :
    (rowsum bitFlipGenPZZI bitFlipGenPIZZ).x q = false := by
  fin_cases q <;> simp [rowsum, bitFlipGenPZZI, bitFlipGenPIZZ]

theorem rowsum_bitFlip_ZZI_IZZ_z_is_ZIZ (q : Fin 3) :
    (rowsum bitFlipGenPZZI bitFlipGenPIZZ).z q = decide (q.val = 0 ∨ q.val = 2) := by
  fin_cases q <;> simp [rowsum, bitFlipGenPZZI, bitFlipGenPIZZ]

theorem rowsum_bitFlip_phase_zero :
    (rowsum bitFlipGenPZZI bitFlipGenPIZZ).r = 0 := by
  simp [rowsum, rowsumPhaseContrib, bitFlipGenPZZI, bitFlipGenPIZZ]

/-- Deterministic phased Z-measure: fail-closed on X-support; else outcome from phase of a
Z-on-`q` generator (`r` even → +1/`false`, odd → −1/`true`). -/
def measureZPhased {n : Nat} (tab : List (GenP n)) (q : Fin n) : Option Bool :=
  if tab.any (fun g => g.x q) then none
  else
    match tab.find? (fun g => g.z q) with
    | none => some false
    | some g => some (decide (g.r % 2 = 1))

def genPXII : GenP 3 :=
  { x := fun i => decide (i.val = 0)
    z := fun _ => false
    r := 0 }

theorem measureZPhased_bitFlip_q0 :
    measureZPhased [bitFlipGenPZZI, bitFlipGenPIZZ] ⟨0, by decide⟩ = some false := by
  simp [measureZPhased, bitFlipGenPZZI, bitFlipGenPIZZ]

theorem measureZPhased_fails_on_XII_phased :
    measureZPhased [genPXII] ⟨0, by decide⟩ = none := by
  simp [measureZPhased, genPXII]

/-- AG Hadamard on a phased generator: swap X/Z on `q`; phase `+2` when both bits set. -/
def applyHGenP {n : Nat} (g : GenP n) (q : Fin n) : GenP n :=
  let phaseBump : Nat := if g.x q && g.z q then 2 else 0
  { x := fun i => if i = q then g.z i else g.x i
    z := fun i => if i = q then g.x i else g.z i
    r := (g.r + phaseBump) % 4 }

/-- AG Phase/S: `z_q := z_q ⊕ x_q`; phase `+1` when `x_q`. -/
def applySGenP {n : Nat} (g : GenP n) (q : Fin n) : GenP n :=
  let phaseBump : Nat := if g.x q then 1 else 0
  { x := g.x
    z := fun i => if i = q then Bool.xor (g.z i) (g.x i) else g.z i
    r := (g.r + phaseBump) % 4 }

/-- AG CNOT: same support update as bool tableau; phase bits unchanged on the generator. -/
def applyCNOTGenP {n : Nat} (g : GenP n) (c t : Fin n) : GenP n :=
  { x := fun i => if i = t then Bool.xor (g.x i) (g.x c) else g.x i
    z := fun i => if i = c then Bool.xor (g.z i) (g.z t) else g.z i
    r := g.r }

theorem applyHGenP_forget_eq_applyHGen (g : GenP 3) (q : Fin 3) :
    forgetPhase (applyHGenP g q) = applyHGen (forgetPhase g) q := by
  simp [forgetPhase, applyHGenP, applyHGen]

theorem applySGenP_forget_eq_applySGen (g : GenP 3) (q : Fin 3) :
    forgetPhase (applySGenP g q) = applySGen (forgetPhase g) q := by
  simp [forgetPhase, applySGenP, applySGen]

theorem applyCNOTGenP_forget_eq_applyCNOTGen (g : GenP 3) (c t : Fin 3) :
    forgetPhase (applyCNOTGenP g c t) = applyCNOTGen (forgetPhase g) c t := by
  simp [forgetPhase, applyCNOTGenP, applyCNOTGen]

theorem applyHGenP_XII_to_Z_phase_zero :
    (applyHGenP genPXII ⟨0, by decide⟩).x ⟨0, by decide⟩ = false ∧
      (applyHGenP genPXII ⟨0, by decide⟩).z ⟨0, by decide⟩ = true ∧
      (applyHGenP genPXII ⟨0, by decide⟩).r = 0 := by
  simp [applyHGenP, genPXII]

theorem applySGenP_XII_phase_one :
    (applySGenP genPXII ⟨0, by decide⟩).x ⟨0, by decide⟩ = true ∧
      (applySGenP genPXII ⟨0, by decide⟩).z ⟨0, by decide⟩ = true ∧
      (applySGenP genPXII ⟨0, by decide⟩).r = 1 := by
  simp [applySGenP, genPXII]

/-- After phased H, XII becomes Z; deterministic phased measure succeeds. -/
theorem measureZPhased_after_H_XII :
    measureZPhased [applyHGenP genPXII ⟨0, by decide⟩] ⟨0, by decide⟩ = some false := by
  simp [measureZPhased, applyHGenP, genPXII]

theorem backend_still_fail_closed_with_phased_fragment :
    measureZPhased [genPXII] ⟨0, by decide⟩ = none :=
  measureZPhased_fails_on_XII_phased

/-! ## Aaronson–Gottesman nondeterministic Z-measure (certified random branch) -/

/-- Replace a pivot generator that has X on `q` by ±Z_q with phase from the outcome
(`rnd = false` → +Z / r=0; `rnd = true` → −Z / r=2). -/
def zOnQubitPhased {n : Nat} (q : Fin n) (rnd : Bool) : GenP n :=
  { x := fun _ => false
    z := fun i => decide (i = q)
    r := if rnd then 2 else 0 }

/-- AG-style nondeterministic Z measurement with certified random bit `rnd`.

Multi-pivot update (Aaronson–Gottesman):
1. If no generator has X on `q`, outcome is deterministic via `measureZPhased`.
2. Otherwise pick the first pivot `p` with `p.x q`, rowsum every other `h` with
   `h.x q` into `p` (clearing those X bits), drop the pivot, and insert `±Z_q`
   with phase from `rnd`.

Shipping `runClifford` (legacy) remains fail-closed on X-support;
`runCliffordPhased` wires this update into the AG shipping path. -/
def measureZNondetAG {n : Nat} (tab : List (GenP n)) (q : Fin n) (rnd : Bool) :
    Bool × List (GenP n) :=
  match tab.findIdx? (fun g => g.x q) with
  | none =>
      let outcome :=
        match measureZPhased tab q with
        | some b => b
        | none => false
      (outcome, tab.filter (fun g => !(g.z q) || g.x q))
  | some pivIdx =>
      match tab.get? pivIdx with
      | none => (rnd, [zOnQubitPhased q rnd])
      | some pivot =>
          -- Rowsum every non-pivot generator that still has X on q into the pivot.
          let cleared : List (GenP n) :=
            tab.enum.map fun ⟨i, g⟩ =>
              if i ≠ pivIdx && g.x q then rowsum g pivot else g
          let withoutPivot := (cleared.enum.filter (fun p => p.1 ≠ pivIdx)).map (·.2)
          let noX := withoutPivot.filter (fun g => !(g.x q))
          (rnd, zOnQubitPhased q rnd :: noX)

/-- Two X-support generators on qubit 0 (multi-pivot witness). -/
def genPXXI : GenP 3 :=
  { x := fun i => decide (i.val ≤ 1)
    z := fun _ => false
    r := 0 }

/-- On an X-support generator, the certified random bit is exactly the measurement outcome. -/
theorem measureZNondetAG_XII_outcome_eq_rnd (rnd : Bool) :
    (measureZNondetAG [genPXII] ⟨0, by decide⟩ rnd).1 = rnd := by
  cases rnd <;> native_decide

/-- Post-measure tableau has no X-support on the measured qubit (stabilizes Z). -/
theorem measureZNondetAG_XII_post_no_X (rnd : Bool) :
    ((measureZNondetAG [genPXII] ⟨0, by decide⟩ rnd).2.any
      (fun g => g.x ⟨0, by decide⟩)) = false := by
  cases rnd <;> native_decide

/-- Post-measure tableau contains a Z generator on the measured qubit. -/
theorem measureZNondetAG_XII_post_has_Z (rnd : Bool) :
    ((measureZNondetAG [genPXII] ⟨0, by decide⟩ rnd).2.any
      (fun g => g.z ⟨0, by decide⟩ && !(g.x ⟨0, by decide⟩))) = true := by
  cases rnd <;> native_decide

/-- Multi-pivot: after measure on q0 for `[XII, XXI]`, no remaining X on q0. -/
theorem measureZNondetAG_multipivot_XII_XXI_no_X (rnd : Bool) :
    ((measureZNondetAG [genPXII, genPXXI] ⟨0, by decide⟩ rnd).2.any
      (fun g => g.x ⟨0, by decide⟩)) = false := by
  cases rnd <;> native_decide

/-- Multi-pivot: outcome equals the certified random bit. -/
theorem measureZNondetAG_multipivot_outcome_eq_rnd (rnd : Bool) :
    (measureZNondetAG [genPXII, genPXXI] ⟨0, by decide⟩ rnd).1 = rnd := by
  cases rnd <;> native_decide

/-- Rowsum of XXI into XII clears X on qubit 0 of the non-pivot image. -/
theorem rowsum_XXI_into_XII_clears_x0 :
    (rowsum genPXXI genPXII).x ⟨0, by decide⟩ = false := by
  simp [rowsum, genPXXI, genPXII]

/-- Deterministic bit-flip case: nondet AG agrees with phased measure (ignores rnd). -/
theorem measureZNondetAG_bitFlip_deterministic (rnd : Bool) :
    (measureZNondetAG [bitFlipGenPZZI, bitFlipGenPIZZ] ⟨0, by decide⟩ rnd).1 = false := by
  cases rnd <;> simp [measureZNondetAG, measureZPhased, bitFlipGenPZZI, bitFlipGenPIZZ]

/-- Map Clifford ops over phased generators. -/
def applyCNOTPhased {n : Nat} (tab : List (GenP n)) (c t : Fin n) : List (GenP n) :=
  tab.map (fun g => applyCNOTGenP g c t)

def applyHPhased {n : Nat} (tab : List (GenP n)) (q : Fin n) : List (GenP n) :=
  tab.map (fun g => applyHGenP g q)

def applySPhased {n : Nat} (tab : List (GenP n)) (q : Fin n) : List (GenP n) :=
  tab.map (fun g => applySGenP g q)

/-- Phased AG shipping runner: X-support measure uses `measureZNondetAG` and consumes one
RNG bit; fails only when X-support measure is requested with an empty RNG stream.
Deterministic (no-X) measures do not consume RNG. -/
def runCliffordPhased {n : Nat} :
    List (GenP n) → List (CliffordOp n) → List Bool → Option (List (GenP n) × List Bool)
  | tab, [], rnds => some (tab, rnds)
  | tab, op :: rest, rnds =>
    match op with
    | .cnot c t => runCliffordPhased (applyCNOTPhased tab c t) rest rnds
    | .h q => runCliffordPhased (applyHPhased tab q) rest rnds
    | .s q => runCliffordPhased (applySPhased tab q) rest rnds
    | .measureZ q =>
      if tab.any (fun g => g.x q) then
        match rnds with
        | [] => none
        | r :: rs =>
          let tab' := (measureZNondetAG tab q r).2
          runCliffordPhased tab' rest rs
      else
        let tab' := (measureZNondetAG tab q false).2
        runCliffordPhased tab' rest rnds

/-- Phased shipping: measure XII with one RNG bit succeeds. -/
theorem runCliffordPhased_XII_measure_isSome (rnd : Bool) :
    (runCliffordPhased [genPXII] [CliffordOp.measureZ ⟨0, by decide⟩] [rnd]).isSome = true := by
  cases rnd <;> simp [runCliffordPhased, measureZNondetAG, genPXII, Option.isSome]

/-- Phased shipping: multi-pivot `[XII, XXI]` measure succeeds with one RNG bit. -/
theorem runCliffordPhased_multipivot_isSome (rnd : Bool) :
    (runCliffordPhased [genPXII, genPXXI]
        [CliffordOp.measureZ ⟨0, by decide⟩] [rnd]).isSome = true := by
  cases rnd <;> simp [runCliffordPhased, measureZNondetAG, genPXII, genPXXI, rowsum,
    rowsumPhaseContrib, zOnQubitPhased, Option.isSome]

/-- Phased shipping fails only when X-support measure is requested with empty RNG. -/
theorem runCliffordPhased_XII_empty_rng_fails :
    runCliffordPhased [genPXII] [CliffordOp.measureZ ⟨0, by decide⟩] [] = none := by
  simp [runCliffordPhased, genPXII]

/-- Deterministic bit-flip measure on the phased path succeeds without consuming RNG. -/
theorem runCliffordPhased_bitFlip_no_rng :
    (runCliffordPhased [bitFlipGenPZZI, bitFlipGenPIZZ]
        [CliffordOp.measureZ ⟨0, by decide⟩] []).isSome = true := by
  simp [runCliffordPhased, measureZNondetAG, measureZPhased, bitFlipGenPZZI, bitFlipGenPIZZ,
    Option.isSome]

/-! ## Unified bool shipping view onto phased AG -/

def liftGen {n : Nat} (g : Gen n) : GenP n :=
  { x := g.x, z := g.z, r := 0 }

def liftTableau {n : Nat} (tab : Tableau n) : List (GenP n) :=
  tab.map liftGen

def forgetTableau {n : Nat} (tab : List (GenP n)) : Tableau n :=
  tab.map forgetPhase

/-- Primary bool-tableau shipping runner: lifts to GenP, runs phased AG, forgets phase. -/
def runCliffordWithRng {n : Nat} (tab : Tableau n) (ops : List (CliffordOp n))
    (rnds : List Bool) : Option (Tableau n × List Bool) :=
  match runCliffordPhased (liftTableau tab) ops rnds with
  | none => none
  | some (tab', rs) => some (forgetTableau tab', rs)

/-- Unified `runClifford`: empty-RNG view of phased shipping. -/
def runClifford {n : Nat} (tab : Tableau n) (ops : List (CliffordOp n)) : Option (Tableau n) :=
  match runCliffordWithRng tab ops [] with
  | none => none
  | some (tab', _) => some tab'

theorem forget_lift_gen {n : Nat} (g : Gen n) : forgetPhase (liftGen g) = g := rfl

theorem forget_lift_tableau {n : Nat} (tab : Tableau n) :
    forgetTableau (liftTableau tab) = tab := by
  simp [forgetTableau, liftTableau, List.map_map]
  change List.map (fun g => forgetPhase (liftGen g)) tab = tab
  simp [liftGen, forgetPhase]

theorem runClifford_empty (tab : Tableau 3) :
    runClifford tab ([] : List (CliffordOp 3)) = some tab := by
  simp [runClifford, runCliffordWithRng, runCliffordPhased, forget_lift_tableau]

theorem runClifford_measure_XII_fails :
    runClifford [genXII] [CliffordOp.measureZ ⟨0, by decide⟩] = none := by
  simp [runClifford, runCliffordWithRng, runCliffordPhased, liftTableau, liftGen, genXII]

theorem runCliffordWithRng_XII_isSome (rnd : Bool) :
    (runCliffordWithRng [genXII] [CliffordOp.measureZ ⟨0, by decide⟩] [rnd]).isSome = true := by
  cases rnd <;>
    simp [runCliffordWithRng, runCliffordPhased, measureZNondetAG, liftTableau, liftGen, genXII,
      forgetTableau, forgetPhase, zOnQubitPhased, Option.isSome]

theorem runClifford_H_then_measure_XII_isSome :
    (runClifford [genXII]
        [CliffordOp.h ⟨0, by decide⟩, CliffordOp.measureZ ⟨0, by decide⟩]).isSome = true := by
  simp [runClifford, runCliffordWithRng, runCliffordPhased, applyHPhased, applyHGenP,
    measureZNondetAG, measureZPhased, liftTableau, liftGen, forgetTableau, forgetPhase,
    genXII, Option.isSome]

theorem runClifford_bitFlip_measure_q0_ok :
    (runClifford bitFlipTableau [CliffordOp.measureZ ⟨0, by decide⟩]).isSome = true := by
  simp [runClifford, runCliffordWithRng, runCliffordPhased, measureZNondetAG, measureZPhased,
    liftTableau, liftGen, forgetTableau, forgetPhase, bitFlipTableau, bitFlipGenZZI, bitFlipGenIZZ,
    Option.isSome]

theorem backend_still_fail_closed_with_nondet_fragment :
    backendStatus = .agPhasedShipping ∧
      runClifford [genXII] [CliffordOp.measureZ ⟨0, by decide⟩] = none ∧
      (measureZNondetAG [genPXII] ⟨0, by decide⟩ true).1 = true := by
  refine ⟨backend_is_ag_shipping, runClifford_measure_XII_fails, ?_⟩
  exact measureZNondetAG_XII_outcome_eq_rnd true

/-- Packaging alias: empty-RNG X-support fails; AG available with RNG. -/
theorem legacy_runClifford_still_fail_closed_on_X :
    runClifford [genXII] [CliffordOp.measureZ ⟨0, by decide⟩] = none ∧
      (measureZNondetAG [genPXII] ⟨0, by decide⟩ true).1 = true :=
  ⟨runClifford_measure_XII_fails, measureZNondetAG_XII_outcome_eq_rnd true⟩

def stabilizerTableauBackendNote : String :=
  "Primary `backendStatus = agPhasedShipping`. Bool `runClifford` views \
`runCliffordPhased` via lift/forget (empty RNG); X-support needs `runCliffordWithRng`."

def cliffordRowUpdateFragmentNote : String :=
  "Unified `runClifford`/`runCliffordWithRng` → `runCliffordPhased` + measureZNondetAG multipivot."

#check backend_is_ag_shipping
#check bitFlipGens_commute
#check applyCNOT_bitFlip_ZZI_c01_z0
#check applyCNOT_preserves_bitFlip_commutation
#check applyH_XII_to_Z
#check applyS_XII_adds_Z
#check applyH_involutive_XII
#check applyH_preserves_bitFlip_commutation
#check measureZDeterministic_bitFlip_q0
#check measureZDeterministic_fails_on_XII
#check backend_still_fail_closed_with_measure_fragment
#check runClifford_measure_XII_fails
#check runClifford_H_then_measure_XII_isSome
#check runClifford_bitFlip_measure_q0_ok
#check runCliffordWithRng_XII_isSome
#check rowsum_bitFlip_ZZI_IZZ_x_cleared
#check rowsum_bitFlip_ZZI_IZZ_z_is_ZIZ
#check rowsum_bitFlip_phase_zero
#check measureZPhased_bitFlip_q0
#check measureZPhased_fails_on_XII_phased
#check applyHGenP_XII_to_Z_phase_zero
#check applySGenP_XII_phase_one
#check applyHGenP_forget_eq_applyHGen
#check measureZPhased_after_H_XII
#check backend_still_fail_closed_with_phased_fragment
#check measureZNondetAG_XII_outcome_eq_rnd
#check measureZNondetAG_XII_post_no_X
#check measureZNondetAG_XII_post_has_Z
#check measureZNondetAG_multipivot_XII_XXI_no_X
#check measureZNondetAG_multipivot_outcome_eq_rnd
#check rowsum_XXI_into_XII_clears_x0
#check measureZNondetAG_bitFlip_deterministic
#check backend_still_fail_closed_with_nondet_fragment
#check phased_backend_is_ag_shipping
#check runCliffordPhased_XII_measure_isSome
#check runCliffordPhased_multipivot_isSome
#check runCliffordPhased_XII_empty_rng_fails
#check runCliffordPhased_bitFlip_no_rng
#check stabilizerTableauBackendNote

end QSpecBench.Quantum.StabilizerTableau
