# QSpecBench QCEC evidence runner image (pinned mqt.qcec for reproducible CI).
FROM python:3.11-slim-bookworm

ARG QCEC_VERSION=3.6.0
RUN pip install --no-cache-dir "mqt.qcec==${QCEC_VERSION}"

WORKDIR /workspace
ENTRYPOINT ["/bin/bash", "-lc"]
