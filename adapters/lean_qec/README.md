# Lean-QEC version-isolated adapter

Status: **integration contract/scaffold only; not passing evidence.**

This adapter is the planned boundary between QSpecBench and external Lean-QEC theorem/certificate exports. It deliberately avoids forcing the external project into QSpecBench's Lean toolchain before compatibility is established.

## Required imported identity

A usable import must bind:
- upstream repository URL;
- exact upstream commit SHA;
- upstream Lean toolchain / dependency lock identity;
- theorem or certificate identifier;
- exported theorem/certificate bytes and SHA-256;
- QSpecBench benchmark/proposition ID;
- proposition relation (`equivalent`, `strict_weakening`, `instance`, etc.);
- semantic assumptions;
- exact obligation IDs supported;
- trust class and checker path.

## QEC scope discipline

An imported distance/certificate result may support only the obligations it actually proves. It must not automatically discharge:
- syndrome-extraction circuit semantics;
- physical noise-model adequacy;
- decoder implementation correctness;
- correction/logical-state preservation;
- repeated-round/fault-tolerance behavior.

Those remain separate assurance-graph edges.

## Typed protocol

The final executable adapter must consume `qspecbench.adapter_request.v1` and produce `qspecbench.adapter_result.v1`. A passing result must bind exact input hashes and enumerate the supported obligations.

## Activation criterion

Do not register this directory as a passing primary-corpus adapter until there is a concrete imported Lean-QEC export, a deterministic checker, pinned upstream identity, tests, and a benchmark assurance graph that uses it without overstating scope. See issue #18.
