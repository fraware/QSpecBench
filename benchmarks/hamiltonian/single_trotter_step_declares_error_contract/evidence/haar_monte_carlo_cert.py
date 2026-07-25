"""Hashed Haar Monte-Carlo AGF certificate (never bare success).

Samples Haar qubit states and estimates average gate fidelity of Pauli-X vs identity.
Compares the sample mean to the Nielsen closed form (|Tr(X†I)|²+2)/6 = 1/3 within
declared absolute tolerance. Emits sha256 over the deterministic certificate payload.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

SCHEMA = "qspecbench.haar_monte_carlo_integral.v1"
SAMPLES = 256
ABS_TOL = 0.02  # matches declaredHaarMonteCarloAbsTol = 1/50
SEED = 20260725
NIELSEN_AGF_X_VS_I = 1.0 / 3.0


def _sha256_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _unit(i: int, salt: int) -> float:
    """Deterministic uniform (0,1) from SHA-256 of (seed, i, salt)."""
    digest = hashlib.sha256(f"{SEED}:{i}:{salt}".encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "little") % 10**15 + 1) / (10**15 + 2)


def _haar_qubit_state(i: int) -> tuple[complex, complex]:
    """Haar qubit via Hopf: z ~ U[0,1], φ ~ U[0,2π]."""
    z = _unit(i, 1)
    phi = 2.0 * math.pi * _unit(i, 2)
    alpha = complex(math.sqrt(z), 0.0)
    beta = complex(math.cos(phi) * math.sqrt(1.0 - z), math.sin(phi) * math.sqrt(1.0 - z))
    return alpha, beta


def _state_fidelity_x_vs_i(alpha: complex, beta: complex) -> float:
    """F(|ψ⟩, X|ψ⟩) = |⟨ψ|X|ψ⟩|² with ⟨ψ|X|ψ⟩ = 2 Re(ᾱ β)."""
    amp = (alpha.conjugate() * beta + beta.conjugate() * alpha).real
    return float(amp * amp)


def main() -> None:
    samples: list[float] = []
    for i in range(SAMPLES):
        alpha, beta = _haar_qubit_state(i)
        samples.append(_state_fidelity_x_vs_i(alpha, beta))
    mean = sum(samples) / len(samples)
    abs_err = abs(mean - NIELSEN_AGF_X_VS_I)
    ok = abs_err <= ABS_TOL
    payload = {
        "schema": SCHEMA,
        "ok": ok,
        "pair": "pauli_X_vs_identity",
        "nielsen_closed_form": NIELSEN_AGF_X_VS_I,
        "samples": SAMPLES,
        "seed": SEED,
        "abs_tol": ABS_TOL,
        "monte_carlo_mean": mean,
        "abs_error": abs_err,
        "notes": (
            "Hashed Haar MC estimate of AGF(X,I) vs Nielsen (|Tr(X)|²+2)/6=1/3. "
            "Not a Lean proof of the Haar integral; numerical certificate only."
        ),
    }
    payload["output_sha256"] = _sha256_payload(
        {k: v for k, v in payload.items() if k != "output_sha256"}
    )
    out = Path(__file__).resolve().parent / "haar_monte_carlo_cert.result.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not ok:
        raise SystemExit(
            f"Haar MC failed: mean={mean} nielsen={NIELSEN_AGF_X_VS_I} "
            f"abs_err={abs_err} tol={ABS_TOL}"
        )
    print(json.dumps({"ok": True, "output_sha256": payload["output_sha256"]}))


if __name__ == "__main__":
    main()
