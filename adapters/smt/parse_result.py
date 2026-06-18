"""Adapter result parser stub."""
from __future__ import annotations
import json, sys
from pathlib import Path

def main() -> None:
    path = Path(sys.argv[1])
    ok = path.is_file()
    print(json.dumps({"ok": ok, "path": str(path)}))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
