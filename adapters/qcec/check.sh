#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ "$#" -lt 2 ]; then
  echo "usage: check.sh <source.qasm> <target.qasm>" >&2
  exit 1
fi
python "$DIR/parse_result.py" "$1" "$2"
