import QSpecBench.CNOT
import QSpecBench.Pauli
import QSpecBench.Matrix
import QSpecBench.QFT2
import QSpecBench.Stabilizer
import QSpecBench.Quantum.QasmOp
import QSpecBench.Generated
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.BridgeMetadata
import QSpecBench.Quantum.OpenQASM3Parser
import QSpecBench.Quantum.Measurement
import QSpecBench.Quantum.ToffoliDecomposition
import QSpecBench.Quantum.StabilizerTableau
import QSpecBench.Teleportation
import QSpecBench.Research.DynamicTeleportation
import QSpecBench.NoCloning
import QSpecBench.Hamiltonian
import QSpecBench.QECDistant
import QSpecBench.QEC.BitFlip
import QSpecBench.QEC.SyndromeExtraction
import QSpecBench.Algorithms

/-!
# QSpecBench library root

Default `lake build QSpecBench` does **not** import `QSpecBench.Evidence.All`.
That aggregate `#check` surface previously caused `std::bad_alloc` when Lean merged
the full environment into this root.

The root does import focused research theorems whose dependencies are already present, such as
`QSpecBench.Research.DynamicTeleportation`, so ordinary library CI compiles those claims directly.

Build the evidence aggregate separately:

```
lake build QSpecBench.Evidence.All
```

See `docs/research_tracks.md` (Adapters / polish).
-/
