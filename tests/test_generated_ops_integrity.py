"""Guard: kernel bridge theorems must not reintroduce hand-authored op duplicates."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OPENQASM3 = REPO / "lean/QSpecBench/Quantum/OpenQASM3.lean"
GENERATED = REPO / "lean/QSpecBench/Generated"


def _generated_ops_literals() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in GENERATED.glob("*.lean"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"def ops\s*:\s*List QasmOp\s*:=\s*(\[[^\]]*\])", text)
        if match:
            out[path.stem] = re.sub(r"\s+", "", match.group(1))
    return out


def test_no_hand_authored_duplicate_of_generated_ops():
    """Reject literal List QasmOp := [...] in OpenQASM3 that equals a Generated module."""
    text = OPENQASM3.read_text(encoding="utf-8")
    generated = _generated_ops_literals()
    assert generated, "expected Generated modules"
    # Hand-authored lists in OpenQASM3 (not aliases to Generated.*).
    for match in re.finditer(
        r"^def\s+(\w+)\s*:\s*List QasmOp\s*:=\s*(\[[^\]]*\])",
        text,
        flags=re.M,
    ):
        name, literal = match.group(1), re.sub(r"\s+", "", match.group(2))
        for mod, gen_lit in generated.items():
            assert literal != gen_lit, (
                f"hand-authored {name} duplicates Generated.{mod}.ops; "
                "import Generated instead"
            )


def test_kernel_bridge_theorems_mention_generated():
    text = OPENQASM3.read_text(encoding="utf-8")
    for thm in (
        "bridge_cnot_codegen_self_inverse",
        "bridge_toffoli_codegen_ccx",
        "bridge_hadamard_codegen_conjugates_x",
        "bridge_swap_from_three_cx_codegen",
    ):
        assert thm in text
    assert "Generated.CnotSelfInverse.ops" in text
    assert "Generated.ToffoliDecompositionEquivalence.ops" in text
    assert not re.search(r"^def\s+cnot_cx_cx\b", text, flags=re.M)
    assert not re.search(r"^def\s+ccx_single\b", text, flags=re.M)
