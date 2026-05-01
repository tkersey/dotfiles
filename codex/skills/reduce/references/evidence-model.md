# Evidence model

The reduce skill should make claims from evidence, not aesthetics.

## Evidence packet

Collect enough evidence to fill this packet:

```text
Area inspected:
Entrypoints:
Primary behavior path traced:
Build/runtime commands:
Tests or proof commands:
Public/external surfaces:
Generated artifacts:
Deploy/CI/ops dependencies:
Docs/ADRs/runbooks/contracts:
Unknowns:
```

Use `scripts/reduce-scan.sh` for initial inventory if available. Treat it as a map of likely places to inspect, not as a basis for deletion.

## Evidence ledger item

Use one ledger item per source:

```text
Source: <file, command, test, doc, config>
Observation: <what you saw>
Proves: <what this evidence supports>
Does not prove: <limits of this evidence>
Confidence impact: <high|medium|low>
```

## Request or command path trace

For each high-impact abstraction, trace a concrete path:

```text
Path name:
Entrypoint:
Files crossed:
Config/generation crossed:
Runtime side effects:
Tests/proof commands:
Hard-to-reason step:
Possible simplification seam:
```

## Required checks by abstraction type

### Code generation

- Source schema/spec.
- Generation command.
- Whether generated output is checked in.
- Consumers of generated code.
- Drift detection or schema compatibility tests.
- Whether a narrower handwritten surface would be smaller.

### Dependency injection / service locator

- Composition root.
- Runtime registration rules.
- Whether dynamic swapping is used in production or tests.
- Number of concrete implementations per interface.
- Test setup cost.
- Whether direct constructors or explicit parameters would work.

### Plugin/middleware/decorator layers

- Registry/config source.
- Ordering dependencies.
- Runtime discovery behavior.
- Which plugins are actually enabled.
- Whether extension by third parties is required.
- Whether an explicit map or function pipeline would work.

### ORM / query abstraction

- Query complexity and count.
- Migration tooling.
- Transaction boundaries.
- N+1 or eager/lazy behavior.
- Dialect portability requirements.
- Raw SQL/query builder replacement feasibility.

### GraphQL/API gateway

- Actual clients and operations.
- Schema compatibility commitments.
- Federation or stitching requirements.
- Authorization boundaries.
- Cache behavior.
- Whether REST/RPC endpoints or typed clients preserve behavior.

### Monorepo/task/build tooling

- Number of packages affected.
- Cross-package dependency graph.
- Cache/value proof.
- CI duration and cache hit evidence.
- Whether simple workspace scripts are enough.
- Whether tool removal breaks release/versioning workflows.

### Infra orchestration

- Environments and deploy targets.
- Secrets/config management.
- Rollback behavior.
- Policy/compliance controls.
- SLO/observability requirements.
- Whether simpler deployment preserves operational guarantees.

## Provisional audit rules

Mark the audit provisional when:

- no runtime path was traced
- tests cannot be located or run
- public API obligations are unknown
- generated artifacts exist but source schemas are missing
- deploy/runtime configuration is absent

When provisional:

- do not recommend `delete` except for obviously orphaned files with rollback
- avoid `replace` for public or operational layers
- list the next evidence needed
- prefer `wrap` or `slice`
