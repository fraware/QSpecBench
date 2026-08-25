import Mathlib.Tactic.FinCases
import QSpecBench.Generated.SourceOptimizedCompilerPair
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser

/-!
# Compiler-generated OpenQASM source/target equivalence

The authoritative source and target strings and operation lists in
`Generated.SourceOptimizedCompilerPair` are generated from the committed benchmark artifacts by
`qspecbench.reference_qasm_peephole.v1`. The generator fails unless recompiling the source produces
bytes identical to the committed target.

This Lean module supplies the formal half of the chain:

1. both generated artifact strings pass the fail-closed OpenQASM fragment parser with the expected
   AST and register width;
2. the gate-only projection agrees with the generated compiler IR on these already fail-closed
   artifacts;
3. source and target compiler IR have exactly equal normalized complex denotations.

The result is deliberately a theorem about this concrete deterministic compiler instance, not a
general correctness theorem for arbitrary optimization passes.
-/

namespace QSpecBench.Research.CompilerFlagship

open QSpecBench.Quantum.QasmOp
open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.OpenQASM3Parser
open QSpecBench.Quantum.ComplexGate
open QSpecBench.Generated.SourceOptimizedCompilerPair

/-- The generated source artifact is accepted by the fail-closed parser with exactly H-X-X. -/
theorem source_artifact_fail_closed_parse :
    (match parseQasmSourceE sourceArtifact with
      | .ok ast =>
          decide (
            ast.version = canonicalAstVersion ∧
            ast.nQubits = 1 ∧
            ast.gates =
              [{ op := "h", qubits := [0] },
               { op := "x", qubits := [0] },
               { op := "x", qubits := [0] }] ∧
            ast.controls = [] ∧ ast.measurements = [] ∧ ast.resets = [])
      | .error _ => false) = true := by
  native_decide

/-- The compiler-emitted target artifact is accepted by the fail-closed parser with exactly H. -/
theorem target_artifact_fail_closed_parse :
    (match parseQasmSourceE targetArtifact with
      | .ok ast =>
          decide (
            ast.version = canonicalAstVersion ∧
            ast.nQubits = 1 ∧
            ast.gates = [{ op := "h", qubits := [0] }] ∧
            ast.controls = [] ∧ ast.measurements = [] ∧ ast.resets = [])
      | .error _ => false) = true := by
  native_decide

/-- Gate lines extracted from the generated source artifact. String-list equality is decidable
without requiring equality on the full `QasmOp` type (whose RX case carries real parameters). -/
def compilerSourceGateLines : List String :=
  ["h q[0];", "x q[0];", "x q[0];"]

theorem gateLinesFromCompilerSource :
    filterGateLines (sourceArtifact.splitOn "\n" |>.map (·.trimRight)) =
      compilerSourceGateLines := by
  native_decide

/-- The parsed source gate lines agree definitionally with the compiler-generated IR. -/
theorem parseLines_compiler_source_eq_generated_ops :
    parseLines compilerSourceGateLines = sourceOps := by
  unfold compilerSourceGateLines sourceOps
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_x]

/-- Gate lines extracted from the compiler-emitted target artifact. -/
def compilerTargetGateLines : List String :=
  ["h q[0];"]

theorem gateLinesFromCompilerTarget :
    filterGateLines (targetArtifact.splitOn "\n" |>.map (·.trimRight)) =
      compilerTargetGateLines := by
  native_decide

/-- The parsed target gate lines agree definitionally with the compiler-generated IR. -/
theorem parseLines_compiler_target_eq_generated_ops :
    parseLines compilerTargetGateLines = targetOps := by
  unfold compilerTargetGateLines targetOps
  simp [parseLines, parseLineQasmOp_bell_h]

/-- On this artifact, the gate projection agrees with the compiler-generated source IR. -/
theorem source_artifact_ops_bound :
    parseQasmSourceToOps sourceArtifact = some sourceOps := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromCompilerSource, parseLines_compiler_source_eq_generated_ops]
  rfl

/-- On this artifact, the gate projection agrees with the compiler-generated target IR. -/
theorem target_artifact_ops_bound :
    parseQasmSourceToOps targetArtifact = some targetOps := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromCompilerTarget, parseLines_compiler_target_eq_generated_ops]
  rfl

/-- The actual compiler source and target traces have identical normalized complex denotations.

`X·X = I` is discharged directly in the concrete 2×2 complex matrix semantics. No external
equivalence result is used in this theorem.
-/
theorem source_target_normalized_complex_denotation_eq :
    denotateOps1C_normalized sourceOps = denotateOps1C_normalized targetOps := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [sourceOps, targetOps, denotateOps1C_normalized, denotateGateC_normalized,
      mul2C, pauliXC, pauliXEntry, hadamardC_normalized, hadamardC_normalizedEntry,
      hadamardEntry, identityGate, identityEntry, Matrix.of_apply, Matrix.one_apply]

/-- End-to-end formal package for the concrete compiler transformation.

The byte-level source→target regeneration is enforced by the deterministic generator/test layer;
this theorem binds the generated exact artifact strings to the fail-closed parser and proves the
resulting source/target normalized complex denotations equal.
-/
theorem compiler_generated_artifact_pair_semantically_equivalent :
    (match parseQasmSourceE sourceArtifact with
      | .ok ast =>
          decide (
            ast.version = canonicalAstVersion ∧
            ast.nQubits = 1 ∧
            ast.gates =
              [{ op := "h", qubits := [0] },
               { op := "x", qubits := [0] },
               { op := "x", qubits := [0] }] ∧
            ast.controls = [] ∧ ast.measurements = [] ∧ ast.resets = [])
      | .error _ => false) = true ∧
    (match parseQasmSourceE targetArtifact with
      | .ok ast =>
          decide (
            ast.version = canonicalAstVersion ∧
            ast.nQubits = 1 ∧
            ast.gates = [{ op := "h", qubits := [0] }] ∧
            ast.controls = [] ∧ ast.measurements = [] ∧ ast.resets = [])
      | .error _ => false) = true ∧
    parseQasmSourceToOps sourceArtifact = some sourceOps ∧
    parseQasmSourceToOps targetArtifact = some targetOps ∧
    denotateOps1C_normalized sourceOps = denotateOps1C_normalized targetOps :=
  ⟨source_artifact_fail_closed_parse, target_artifact_fail_closed_parse,
    source_artifact_ops_bound, target_artifact_ops_bound,
    source_target_normalized_complex_denotation_eq⟩

def scopeNote : String :=
  "exact compiler instance: committed OpenQASM source -> deterministic X-pair cancellation -> " ++
  "committed target; fail-closed parse; normalized complex source/target denotation equality; " ++
  "not a universal optimizer-correctness theorem"

end QSpecBench.Research.CompilerFlagship
