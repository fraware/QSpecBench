# -*- coding: utf-8 -*-
"""PyMatching Blossom fixture-graph agreement with Lean decodeSpacetimeMwpm.

Optional dependency (pymatching==2.4.0). Fail-closed when missing or when
agreement fails. Never treats a bare success string as a certificate.
Honest label: Blossom on a declared fixture graph — not Stim DEM / not full spacetime MWPM.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PYMATCHING_PIN = "2.4.0"


class PyMatchingFixtureError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_payload(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_pymatching():
    try:
        import pymatching  # noqa: F401
    except ImportError as exc:
        raise PyMatchingFixtureError(
            f"pymatching not installed; pin pymatching=={PYMATCHING_PIN} "
            "(optional extra qec-matching)"
        ) from exc
    import pymatching

    ver = getattr(pymatching, "__version__", "unknown")
    if ver != PYMATCHING_PIN:
        raise PyMatchingFixtureError(
            f"pymatching version {ver!r} != pinned {PYMATCHING_PIN!r}"
        )
    return pymatching


def load_graph(graph_path: Path) -> dict[str, Any]:
    if not graph_path.is_file():
        raise PyMatchingFixtureError(f"matching graph missing: {graph_path}")
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    if data.get("schema") != "qspecbench.matching_graph_fixture.v1":
        raise PyMatchingFixtureError(f"unexpected graph schema {data.get('schema')!r}")
    if not data.get("edges"):
        raise PyMatchingFixtureError("matching graph requires edges")
    return data


def load_table(table_path: Path) -> dict[str, Any]:
    if not table_path.is_file():
        raise PyMatchingFixtureError(f"declared decode table missing: {table_path}")
    data = json.loads(table_path.read_text(encoding="utf-8"))
    if data.get("schema") != "qspecbench.declared_decode_table.v1":
        raise PyMatchingFixtureError(f"unexpected table schema {data.get('schema')!r}")
    if not data.get("cases"):
        raise PyMatchingFixtureError("declared decode table requires cases")
    return data


def build_matching(graph: dict[str, Any]):
    pymatching = _require_pymatching()
    m = pymatching.Matching()
    for edge in graph["edges"]:
        nodes = edge["nodes"]
        if len(nodes) != 2:
            raise PyMatchingFixtureError(f"edge must have 2 nodes: {edge}")
        m.add_edge(
            int(nodes[0]),
            int(nodes[1]),
            fault_ids=set(edge.get("fault_ids") or []),
            weight=float(edge.get("weight", 1.0)),
        )
    return m


def decode_syndrome(matching, syndrome_bits: list[int]) -> list[int]:
    import numpy as np

    syn = np.array(syndrome_bits, dtype=np.uint8)
    pred = matching.decode(syn)
    return [int(x) for x in pred]


def verify_fixture_agreement(
    graph_path: Path,
    table_path: Path,
) -> dict[str, Any]:
    """Compare PyMatching Blossom decode to declared Lean-mirror table on finite cases."""
    graph = load_graph(graph_path)
    table = load_table(table_path)
    matching = build_matching(graph)
    import pymatching

    agreed: list[str] = []
    disagreed: list[str] = []
    outside_ok: list[str] = []
    outside_fail: list[str] = []
    case_details: list[dict[str, Any]] = []

    for case in table["cases"]:
        name = str(case["name"])
        syndrome = list(case["syndrome_bits"])
        expected = list(case["expected_prediction"])
        kind = case.get("kind", "in_model")
        pred = decode_syndrome(matching, syndrome)
        detail = {
            "name": name,
            "kind": kind,
            "syndrome_bits": syndrome,
            "expected_prediction": expected,
            "pymatching_prediction": pred,
            "agree": pred == expected,
        }
        case_details.append(detail)
        if kind == "outside":
            # Outside negatives: must NOT agree with the in-model expected correction
            # (Lean outside theorems show correction fails). Table stores the Lean
            # decode output; agreement with that output is required for honesty of
            # the mirror, while `outside_breaks` records that correction is wrong.
            if pred == expected:
                outside_ok.append(name)
            else:
                outside_fail.append(name)
                disagreed.append(name)
        else:
            if pred == expected:
                agreed.append(name)
            else:
                disagreed.append(name)

    ok = not disagreed and not outside_fail and len(agreed) > 0
    result: dict[str, Any] = {
        "schema": "qspecbench.external_matching_agree.v1",
        "ok": ok,
        "stim_invoked": False,
        "pymatching_invoked": True,
        "full_spacetime_mwpm": False,
        "pymatching_version": pymatching.__version__,
        "command": (
            "python -m qspecbench.pymatching_fixture_adapter "
            f"--graph {graph_path.name} --table {table_path.name}"
        ),
        "graph_sha256": sha256_file(graph_path),
        "table_sha256": sha256_file(table_path),
        "agreed_faults": agreed,
        "disagreed_faults": disagreed,
        "outside_checked": outside_ok,
        "outside_failed": outside_fail,
        "case_details": case_details,
        "notes": (
            "Blossom-backed PyMatching on declared fixture graph agrees with "
            "Lean decodeSpacetimeMwpm mirror table on the finite in-model set. "
            "Not Stim DEM; not full spacetime MWPM."
        ),
    }
    result["output_sha256"] = sha256_payload(
        {k: v for k, v in result.items() if k != "output_sha256"}
    )
    if not ok:
        raise PyMatchingFixtureError(
            "fixture agreement failed: "
            + ", ".join(disagreed or outside_fail or ["unknown"])
        )
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify_fixture_agreement(args.graph, args.table)
    except PyMatchingFixtureError as exc:
        payload = {
            "schema": "qspecbench.external_matching_agree.v1",
            "ok": False,
            "stim_invoked": False,
            "pymatching_invoked": False,
            "full_spacetime_mwpm": False,
            "error": str(exc),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(exc, file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": result["ok"], "output_sha256": result["output_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
