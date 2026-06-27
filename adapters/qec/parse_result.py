"""Stabilizer code JSON validator for QSpecBench QEC artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PAULI_RE = re.compile(r"^[IXYZ_]+$")
PAULI_TO_VEC = {"I": 0, "X": 1, "Y": 2, "Z": 3}


def _pauli_char(p: str, idx: int) -> str:
    if idx >= len(p):
        return "I"
    ch = p[idx]
    return ch if ch in "IXYZ" else "I"


def _pauli_commute(a: str, b: str) -> bool:
    n = max(len(a), len(b))
    anticommute = 0
    for i in range(n):
        pa = _pauli_char(a, i)
        pb = _pauli_char(b, i)
        if pa == "I" or pb == "I" or pa == pb:
            continue
        anticommute += 1
    return anticommute % 2 == 0


def _syndrome_from_error(stabilizers: list[str], error_pauli: str) -> str:
    """Compute syndrome bits s0.. from X/Z anticommutation with stabilizer generators."""
    bits: list[str] = []
    for stab in stabilizers:
        anticommute = 0
        n = max(len(stab), len(error_pauli))
        for i in range(n):
            ps = _pauli_char(stab, i)
            pe = _pauli_char(error_pauli, i)
            if ps == "I" or pe == "I":
                continue
            if ps != pe:
                anticommute += 1
        bits.append("1" if anticommute % 2 else "0")
    return "".join(bits)


def _error_pauli_for_label(label: str, n: int) -> str:
    """Map shorthand like X0, X1 to n-qubit Pauli string."""
    label = label.strip()
    if label in {"I", "III"} or label == "identity":
        return "I" * n
    m = re.match(r"^X(\d+)$", label)
    if m:
        idx = int(m.group(1))
        if not (0 <= idx < n):
            raise ValueError(f"X index {idx} out of range for n={n} in label {label!r}")
        chars = ["I"] * n
        chars[idx] = "X"
        return "".join(chars)
    if PAULI_RE.match(label) and len(label) == n:
        return label
    raise ValueError(f"unknown or malformed error label {label!r} for n={n}")


def validate_syndrome_table(
    code: dict,
    syndrome_table: dict,
    error_model: dict | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = ["syndrome_table_structure"]
    stabilizers = [s.get("pauli", "") for s in code.get("stabilizers", [])]
    n = code.get("parameters", {}).get("n", 0)
    if not isinstance(n, int) or not stabilizers:
        return ["code missing n or stabilizers for syndrome validation"], checks

    entries = syndrome_table.get("entries", [])
    computed: dict[str, str] = {}
    for entry in entries:
        err_label = entry.get("error", "")
        err_pauli = _error_pauli_for_label(err_label, n)
        computed_syndrome = _syndrome_from_error(stabilizers, err_pauli)
        declared = str(entry.get("syndrome", "")).replace(" ", "")
        computed[err_label] = computed_syndrome
        if declared != computed_syndrome:
            errors.append(
                f"syndrome mismatch for error {err_label!r}: "
                f"table={declared!r} computed={computed_syndrome!r}"
            )

    checks.append("syndrome_table_antcommutation")
    if error_model:
        allowed = error_model.get("allowed_errors") or []
        max_weight = error_model.get("max_weight", 1)
        if allowed == ["X"] and max_weight == 1:
            checks.append("single_x_syndrome_injection")
            for i in range(n):
                label = f"X{i}"
                err_pauli = _error_pauli_for_label(label, n)
                syn = _syndrome_from_error(stabilizers, err_pauli)
                if syn not in {e.get("syndrome", "").replace(" ", "") for e in entries}:
                    errors.append(f"single X error X{i} syndrome {syn!r} missing from table")

    return errors, checks


def validate_correction_table(
    syndrome_table: dict,
    correction_table: dict,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = ["correction_table_structure"]
    syn_to_corr: dict[str, str] = {}
    for entry in correction_table.get("entries", []):
        syn = str(entry.get("syndrome", "")).replace(" ", "")
        corr = entry.get("physical_correction") or entry.get("correction") or ""
        syn_to_corr[syn] = corr

    for entry in syndrome_table.get("entries", []):
        syn = str(entry.get("syndrome", "")).replace(" ", "")
        expected = entry.get("correction") or entry.get("physical_correction") or ""
        actual = syn_to_corr.get(syn)
        if actual is None:
            errors.append(f"correction table missing syndrome {syn!r}")
        elif expected and actual != expected:
            errors.append(
                f"correction mismatch for syndrome {syn!r}: "
                f"syndrome_table={expected!r} correction_table={actual!r}"
            )
    checks.append("correction_table_syndrome_alignment")
    return errors, checks


def _pauli_multiply(a: str, b: str) -> str:
    """Multiply two Pauli strings (ignoring global phase)."""
    n = max(len(a), len(b))
    out: list[str] = []
    for i in range(n):
        pa = _pauli_char(a, i)
        pb = _pauli_char(b, i)
        if pa == "I":
            out.append(pb)
        elif pb == "I":
            out.append(pa)
        elif pa == pb:
            out.append("I")
        elif {pa, pb} == {"X", "Z"}:
            out.append("Y")
        elif {pa, pb} == {"X", "Y"}:
            out.append("Z")
        elif {pa, pb} == {"Y", "Z"}:
            out.append("X")
        else:
            out.append("I")
    return "".join(out)


def _stabilizer_group_elements(stabilizers: list[str]) -> set[str]:
    """Brute-force stabilizer group for small generator count."""
    from itertools import product

    gens = stabilizers or []
    elements: set[str] = set()
    for bits in product([0, 1], repeat=len(gens)):
        acc = "I" * max((len(g) for g in gens), default=0)
        for use, gen in zip(bits, gens):
            if use:
                acc = _pauli_multiply(acc, gen)
        n = max(len(g) for g in gens) if gens else len(acc)
        acc = acc.ljust(n, "I")[:n]
        elements.add(acc)
    return elements


def _enumerate_allowed_errors(n: int, error_model: dict | None) -> list[str]:
    from itertools import product

    if not error_model:
        return ["I" * n]
    allowed = error_model.get("allowed_errors") or ["X", "Y", "Z"]
    max_weight = error_model.get("max_weight", 1)
    alphabet = ("I",) + tuple(allowed)

    def weight(p: str) -> int:
        return sum(1 for c in p if c in "XYZ")

    errors: list[str] = []
    for combo in product(alphabet, repeat=n):
        p = "".join(combo)
        if weight(p) <= max_weight:
            errors.append(p)
    return errors


def validate_logical_preservation(
    code: dict,
    syndrome_table: dict,
    correction_table: dict,
    error_model: dict | None = None,
) -> tuple[list[str], list[str]]:
    """Brute-force: error then correction yields a stabilizer (logical state preserved)."""
    errors: list[str] = []
    checks: list[str] = ["logical_preservation_bruteforce"]
    n = code.get("parameters", {}).get("n", 0)
    stabilizers = [s.get("pauli", "") for s in code.get("stabilizers", [])]
    if not isinstance(n, int) or n > 6 or not stabilizers:
        return errors, checks

    stab_group = _stabilizer_group_elements(stabilizers)
    syn_entries = {
        str(e.get("syndrome", "")).replace(" ", ""): e for e in syndrome_table.get("entries", [])
    }
    corr_entries = {
        str(e.get("syndrome", "")).replace(" ", ""): (
            e.get("physical_correction") or e.get("correction") or ""
        )
        for e in correction_table.get("entries", [])
    }

    for err_pauli in _enumerate_allowed_errors(n, error_model):
        syndrome = _syndrome_from_error(stabilizers, err_pauli)
        if syndrome not in corr_entries:
            errors.append(f"correction table missing syndrome {syndrome!r} for error {err_pauli!r}")
            continue
        correction = corr_entries[syndrome]
        residual = _pauli_multiply(err_pauli, correction)
        if residual not in stab_group:
            errors.append(
                f"logical preservation failed: error {err_pauli!r} + correction {correction!r} "
                f"= {residual!r} not in stabilizer group"
            )
        if syndrome in syn_entries:
            expected_corr = (
                syn_entries[syndrome].get("correction")
                or syn_entries[syndrome].get("physical_correction")
                or ""
            )
            if expected_corr and correction != expected_corr:
                errors.append(
                    f"correction table vs syndrome_table mismatch for syndrome {syndrome!r}"
                )

    checks.append("single_pauli_error_correction_validator")
    return errors, checks


def validate_min_weight_distance(
    code: dict, error_model: dict | None
) -> tuple[list[str], list[str], int | None]:
    """Brute-force minimum-weight logical operator under declared error model (small n only)."""
    warnings: list[str] = []
    checks: list[str] = ["distance_min_weight_bruteforce"]
    n = code.get("parameters", {}).get("n")
    stabilizers = [s.get("pauli", "") for s in code.get("stabilizers", [])]
    logicals = [op.get("pauli", "") for op in code.get("logical_operators", [])]
    if not isinstance(n, int) or n > 6 or not stabilizers or not logicals:
        return warnings, checks, None

    from itertools import product

    def weight(p: str) -> int:
        return sum(1 for c in p if c in "XYZ")

    x_only = error_model and error_model.get("allowed_errors") == ["X"]
    alphabet = ("I", "X") if x_only else ("I", "X", "Y", "Z")

    min_d: int | None = None
    for w in range(1, n + 1):
        for combo in product(alphabet, repeat=n):
            p = "".join(combo)
            if weight(p) != w:
                continue
            if not all(_pauli_commute(p, s) for s in stabilizers):
                continue
            if any(not _pauli_commute(p, l) for l in logicals):
                min_d = w
                break
        if min_d is not None:
            break

    params = code.get("parameters", {})
    if x_only and isinstance(params.get("bit_flip_distance"), int) and min_d is not None:
        declared = params["bit_flip_distance"]
        if min_d != declared:
            warnings.append(
                f"computed X-only min logical weight {min_d} != declared bit_flip_distance {declared}"
            )
    elif isinstance(params.get("quantum_distance"), int) and min_d is not None:
        if min_d != params["quantum_distance"]:
            warnings.append(
                f"computed min logical weight {min_d} != declared quantum_distance {params['quantum_distance']}"
            )

    return warnings, checks, min_d


def validate_code(data: dict) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    checks_run: list[str] = ["schema_structure"]

    if data.get("type") != "stabilizer_code":
        errors.append("type must be stabilizer_code")
    params = data.get("parameters", {})
    for key in ("n", "k", "d"):
        if key not in params:
            errors.append(f"parameters.{key} required")
    stabilizers = data.get("stabilizers", [])
    if not stabilizers:
        errors.append("at least one stabilizer required")
    for s in stabilizers:
        pauli = s.get("pauli", "")
        if not PAULI_RE.match(pauli):
            errors.append(f"invalid pauli string: {pauli}")
    logicals = data.get("logical_operators", [])
    for op in logicals:
        pauli = op.get("pauli", "")
        if not PAULI_RE.match(pauli):
            errors.append(f"invalid logical pauli: {pauli}")
    n = params.get("n")
    if isinstance(n, int):
        for s in stabilizers:
            if len(s.get("pauli", "")) != n:
                errors.append(f"stabilizer length must be n={n}")
        for op in logicals:
            if len(op.get("pauli", "")) != n:
                errors.append(f"logical operator length must be n={n}")

    if len(stabilizers) >= 2 and not errors:
        checks_run.append("stabilizer_commutation")
        labels = [s.get("label", s.get("pauli", "?")) for s in stabilizers]
        paulis = [s.get("pauli", "") for s in stabilizers]
        for i in range(len(paulis)):
            for j in range(i + 1, len(paulis)):
                if not _pauli_commute(paulis[i], paulis[j]):
                    errors.append(
                        f"stabilizers {labels[i]} and {labels[j]} anticommute"
                    )

    if logicals and stabilizers and not errors:
        checks_run.append("logical_stabilizer_commutation")
        for op in logicals:
            op_label = op.get("label", op.get("pauli", "?"))
            op_pauli = op.get("pauli", "")
            for s in stabilizers:
                s_label = s.get("label", s.get("pauli", "?"))
                if not _pauli_commute(op_pauli, s.get("pauli", "")):
                    errors.append(
                        f"logical {op_label} anticommutes with stabilizer {s_label}"
                    )

    if isinstance(params.get("d"), int) and isinstance(n, int) and isinstance(params.get("k"), int):
        checks_run.append("distance_consistency")
        d = params["d"]
        k = params["k"]
        if d < 1:
            warnings.append("distance d < 1")
        if n and k and d > n - k + 1:
            warnings.append("distance d exceeds Singleton bound for declared n,k")
        if len(stabilizers) < n - k:
            warnings.append("fewer stabilizers than n-k; code may be under-specified")
        # Declared distance constants are structural metadata, not a proof.
        warnings.append(
            "declared distance is metadata only; it is not a machine-checked distance proof"
        )

    # Optional explicit distance-type fields keep bit-flip distance from being read
    # as a full quantum (Pauli) distance.
    bit_flip_distance = params.get("bit_flip_distance")
    quantum_distance = params.get("quantum_distance")
    if bit_flip_distance is not None or quantum_distance is not None:
        checks_run.append("distance_type_consistency")
        if isinstance(bit_flip_distance, int) and isinstance(params.get("d"), int):
            if bit_flip_distance != params["d"]:
                warnings.append("bit_flip_distance does not equal declared d")
        if isinstance(bit_flip_distance, int) and isinstance(quantum_distance, int):
            if quantum_distance > bit_flip_distance:
                errors.append("quantum_distance cannot exceed bit_flip_distance")

    return errors, warnings, checks_run


def _derive_check_results(
    checks_run: list[str],
    errors: list[str],
    *,
    distance_result: dict | None,
) -> dict[str, bool | None]:
    """Structured booleans for qec_verifier_result evidence artifacts."""
    has = set(checks_run)
    structure_ok = "schema_structure" in has and not any(
        e.startswith("type must") or "parameters." in e or "stabilizer" in e.lower()
        for e in errors
        if "syndrome" not in e and "correction" not in e and "logical preservation" not in e
    )
    syndrome_ok = (
        "syndrome_table_antcommutation" in has
        and not any("syndrome" in e.lower() for e in errors)
    ) if "syndrome_table_structure" in has else None
    correction_ok = (
        "correction_table_syndrome_alignment" in has
        and not any("correction" in e.lower() for e in errors)
    ) if "correction_table_structure" in has else None
    logical_ok = (
        "single_pauli_error_correction_validator" in has
        and not any("logical preservation" in e for e in errors)
    ) if "logical_preservation_bruteforce" in has else None
    distance_ok: bool | None = None
    if "distance_min_weight_bruteforce" in has:
        distance_ok = distance_result is not None and not any(
            "computed" in e and "distance" in e for e in errors
        )
    return {
        "structure": structure_ok,
        "syndrome": syndrome_ok,
        "correction": correction_ok,
        "logical_preservation": logical_ok,
        "distance": distance_ok,
    }


def check(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings, checks_run = validate_code(data)

    artifact_dir = path.parent
    syndrome_path = artifact_dir / "syndrome_table.json"
    correction_path = artifact_dir / "correction_table.json"
    error_model_path = artifact_dir / "error_model.json"

    error_model = None
    if error_model_path.is_file():
        error_model = json.loads(error_model_path.read_text(encoding="utf-8"))

    if syndrome_path.is_file():
        syndrome_data = json.loads(syndrome_path.read_text(encoding="utf-8"))
        syn_errors, syn_checks = validate_syndrome_table(data, syndrome_data, error_model)
        errors.extend(syn_errors)
        checks_run.extend(syn_checks)

    if syndrome_path.is_file() and correction_path.is_file():
        syndrome_data = json.loads(syndrome_path.read_text(encoding="utf-8"))
        correction_data = json.loads(correction_path.read_text(encoding="utf-8"))
        corr_errors, corr_checks = validate_correction_table(syndrome_data, correction_data)
        errors.extend(corr_errors)
        checks_run.extend(corr_checks)
        lp_errors, lp_checks = validate_logical_preservation(
            data, syndrome_data, correction_data, error_model
        )
        errors.extend(lp_errors)
        checks_run.extend(lp_checks)

    if data.get("type") == "stabilizer_code":
        dist_warnings, dist_checks, min_d = validate_min_weight_distance(data, error_model)
        warnings.extend(dist_warnings)
        checks_run.extend(dist_checks)
        distance_result = None
        if min_d is not None:
            distance_result = {
                "method": "bruteforce_min_weight_logical_operator",
                "computed_min_weight": min_d,
                "error_model": error_model or {},
                "n_qubits": data.get("parameters", {}).get("n"),
            }
    else:
        distance_result = None

    check_results = _derive_check_results(
        checks_run, errors, distance_result=distance_result if data.get("type") == "stabilizer_code" else None
    )

    result = {
        "ok": not errors,
        "adapter": "qec_json_validator",
        "path": str(path),
        "trust_level": "tool_checked",
        "checks_run": checks_run,
        "check_results": check_results,
        "warnings": warnings,
        "errors": errors,
    }
    if data.get("type") == "stabilizer_code":
        result["distance_result"] = distance_result
    return result


def main() -> None:
    path = Path(sys.argv[1])
    result = check(path)
    out = path.with_suffix(".validated.json")
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
