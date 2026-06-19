"""Sanity-check detector model JSON."""
import json
from pathlib import Path

def main() -> None:
    data = json.loads((Path(__file__).resolve().parents[1] / "artifacts/detector_model.json").read_text())
    assert data.get("detectors")
    for det in data["detectors"]:
        eff = det.get("efficiency", 0)
        assert 0 < eff <= 1
    print(json.dumps({"ok": True, "trust_level": "heuristic"}))

if __name__ == "__main__":
    main()
