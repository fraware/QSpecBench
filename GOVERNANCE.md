# Governance

QSpecBench uses three maintainer roles:

## Schema maintainers

Responsible for schema design, validation rules, and compatibility.

## Track maintainers

Responsible for algorithms, equivalence, QEC, Hamiltonian, and AI-formalization tracks.

## Evidence maintainers

Responsible for adapters, checker integration, trust-level rules, and CI behavior.

## Review policy

Every benchmark PR is reviewed across:

1. **Scientific review** — claim sense, assumptions, terminology
2. **Specification review** — spec matches informal claim, semantics clear
3. **Evidence review** — evidence supports claim, checker declared, trust honest

No maintainer should merge their own reference-level benchmark without review.

## Schema changes

Schema changes must be versioned, documented, and justified by real benchmark needs.
