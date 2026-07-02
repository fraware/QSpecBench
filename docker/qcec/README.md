# QSpecBench QCEC Docker image

Build locally:

```bash
docker build -t qspecbench-qcec docker/qcec
```

Run evidence checks:

```bash
docker run --rm -v "$(pwd):/workspace" -w /workspace qspecbench-qcec \
  "pip install -e . && qspecbench check-evidence benchmarks/equivalence/cnot_self_inverse_cancellation/"
```

Default CI installs `mqt.qcec` via the `dev` dependency group in `pyproject.toml` (`uv sync --frozen --dev`);
this Docker image is for local or custom runners only.
