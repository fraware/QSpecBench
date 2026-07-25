"""Circuit backends: select representation without forcing dense matrices."""

from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from qspecbench.resource_bounds import require_dense_matrix, require_perm_circuit
from qspecbench.schema import REPO_ROOT


class CircuitBackend(ABC):
    """Abstract circuit comparison / extraction backend."""

    name: str

    @abstractmethod
    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class DenseExactBackend(CircuitBackend):
    name = "dense_exact"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        from qspecbench.qasm_matrix import extract_matrix

        data = extract_matrix(qasm_path, extraction=extraction)
        return {"backend": self.name, **data}

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        from qspecbench.qasm_matrix import _mat_mul

        if left["n_qubits"] != right["n_qubits"]:
            raise ValueError("compose requires equal n_qubits")
        n = int(left["n_qubits"])
        require_dense_matrix(n)
        return {
            "backend": self.name,
            "n_qubits": n,
            "matrix": _mat_mul(left["matrix"], right["matrix"]),
        }

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        from qspecbench.qasm_matrix import matrices_equal

        ok = matrices_equal(left["matrix"], right["matrix"])
        return {"ok": ok, "backend": self.name, "relation": "exact"}


class DenseApproxBackend(CircuitBackend):
    name = "dense_approx"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        return DenseExactBackend().parse(qasm_path, extraction=extraction)

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        return DenseExactBackend().compose(left, right)

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        result = DenseExactBackend().compare(left, right)
        result["backend"] = self.name
        result["relation"] = "approx"
        return result


class PermutationBackend(CircuitBackend):
    """Exact permutation / reversible circuits without dense matrices."""

    name = "permutation"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        from qspecbench.perm_circuit import apply_qasm_permutation
        import re

        text = qasm_path.read_text(encoding="utf-8")
        m = re.search(r"qubit\s*\[\s*(\d+)\s*\]", text)
        if not m:
            raise ValueError("expected qubit[n] register declaration")
        n = int(m.group(1))
        require_perm_circuit(n)
        _ = extraction
        perm = apply_qasm_permutation(qasm_path, n)
        return {
            "backend": self.name,
            "n_qubits": n,
            "permutation": perm,
        }

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        if left["n_qubits"] != right["n_qubits"]:
            raise ValueError("compose requires equal n_qubits")
        lp = left["permutation"]
        rp = right["permutation"]
        composed = [lp[rp[i]] for i in range(len(lp))]
        return {"backend": self.name, "n_qubits": left["n_qubits"], "permutation": composed}

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        ok = left.get("permutation") == right.get("permutation")
        return {"ok": ok, "backend": self.name, "relation": "exact_permutation"}


class StabilizerTableauBackend(CircuitBackend):
    name = "stabilizer_tableau"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError(
            "stabilizer_tableau backend is declared but not yet shipping; "
            "use dense_exact for small Clifford instances or an external adapter"
        )

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("stabilizer_tableau compose unavailable")

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("stabilizer_tableau compare unavailable")


class QCECBackend(CircuitBackend):
    name = "qcec"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"backend": self.name, "path": str(qasm_path)}

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("qcec compose is not defined; compare two circuits instead")

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        path = REPO_ROOT / "adapters/qcec/parse_result.py"
        spec = importlib.util.spec_from_file_location("qcec_parse", path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.check(Path(left["path"]), Path(right["path"]))


class CertificateOnlyBackend(CircuitBackend):
    name = "certificate_only"

    def parse(self, qasm_path: Path, *, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"backend": self.name, "path": str(qasm_path), "note": "no denotation computed"}

    def compose(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("certificate_only does not compose circuits")

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(
            "certificate_only requires an independently checkable certificate path; "
            "use adapters/matrix_certificate or sat_certificate"
        )


BACKENDS: dict[str, type[CircuitBackend]] = {
    "dense_exact": DenseExactBackend,
    "dense_approx": DenseApproxBackend,
    "permutation": PermutationBackend,
    "stabilizer_tableau": StabilizerTableauBackend,
    "qcec": QCECBackend,
    "certificate_only": CertificateOnlyBackend,
}


def select_backend(
    *,
    n_qubits: int | None = None,
    permutation_only: bool = False,
    name: str | None = None,
) -> CircuitBackend:
    """Never choose dense when a permutation representation suffices."""
    if name:
        cls = BACKENDS.get(name)
        if cls is None:
            raise ValueError(f"unknown circuit backend {name!r}")
        return cls()
    if permutation_only:
        return PermutationBackend()
    if n_qubits is not None:
        from qspecbench.resource_bounds import dense_matrix_allowed

        if not dense_matrix_allowed(n_qubits):
            raise ValueError(
                f"no default dense backend for {n_qubits} qubits; "
                "pass name='permutation'|'qcec'|'certificate_only' or raise the dense limit"
            )
    return DenseExactBackend()
