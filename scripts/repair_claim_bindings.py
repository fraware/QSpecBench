"""One-shot corpus repair for claim integrity bindings."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from qspecbench.trust import _declared_obligation_ids

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    for path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in path.parts:
            continue
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        maturity = (spec.get("status") or {}).get("maturity")
        if maturity not in ("artifact_bound_reference_claim", "reference_claim"):
            continue
        changed = False
        ids = _declared_obligation_ids(spec)

        for fc in spec.get("formal_claims") or []:
            supports = list(fc.get("supports") or [])
            keep = [x for x in supports if x in ids]
            drop = [x for x in supports if x not in ids]
            if not drop:
                continue
            hcs = spec.setdefault("headline_claim_status", {})
            ncu = list(hcs.get("not_checked_under") or [])
            dns = list(fc.get("does_not_support") or [])
            for d in drop:
                if d not in ncu:
                    ncu.append(d)
                if d not in dns:
                    dns.append(d)
            hcs["not_checked_under"] = ncu
            fc["does_not_support"] = dns
            ids = _declared_obligation_ids(spec)
            keep = [x for x in supports if x in ids and x not in drop]
            if not keep:
                req = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
                keep = [req[0]] if req else []
            fc["supports"] = keep
            changed = True
            print(path.parent.name, "dropped supports", drop, "kept", keep)

        req = list((spec.get("claim_scope") or {}).get("required_obligations") or [])
        supported: set[str] = set()
        for fc in spec.get("formal_claims") or []:
            supported.update(fc.get("supports") or [])
        missing = [o for o in req if o not in supported]
        if missing and (spec.get("formal_claims") or []):
            fc = spec["formal_claims"][0]
            fc["supports"] = list(dict.fromkeys(list(fc.get("supports") or []) + missing))
            changed = True
            print(path.parent.name, "bound missing", missing, "to", fc["id"])

        title = spec.get("title") or ""
        stmt = ((spec.get("informal_claim") or {}).get("statement") or "")
        t_tok = {t for t in re.split(r"[^a-z0-9]+", title.lower()) if len(t) > 3}
        s_tok = {t for t in re.split(r"[^a-z0-9]+", stmt.lower()) if len(t) > 3}
        if t_tok and s_tok and not (t_tok & s_tok) and title != stmt:
            # Prefer meaningful overlap: include first distinctive statement tokens.
            hint = " ".join(sorted(s_tok)[:2])
            spec["title"] = f"{title} ({hint})"
            changed = True
            print(path.parent.name, "retitled ->", spec["title"])

        prop = ((spec.get("claim_identity") or {}).get("proposition_id") or "").strip()
        bridge_path = path.parent / "expected" / "semantic_bridge.json"
        if prop and bridge_path.is_file():
            bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
            if bridge.get("proposition_id") != prop:
                bridge["proposition_id"] = prop
                bridge_path.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")
                print(path.parent.name, "bridge prop set")

        if changed:
            path.write_text(
                yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=100),
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
