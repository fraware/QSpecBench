"""Check declared resource contract fields in hamiltonian.json."""
import json
from pathlib import Path

def main() -> None:
    data = json.loads((Path(__file__).resolve().parents[1] / "artifacts/hamiltonian.json").read_text())
    rc = data.get("resource_contract", {})
    assert rc.get("qubits", 0) >= 1
    assert rc.get("terms", 0) >= 1
    print(json.dumps({"ok": True, "trust_level": "heuristic", "resource_contract": rc}))

if __name__ == "__main__":
    main()
