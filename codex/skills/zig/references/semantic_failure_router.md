# Zig Semantic Failure Router

The router is orthogonal to ordinary Zig task classification.

```text
Axis A: migration, build, comptime, formatting, hazard, FFI, concurrency, performance...
Axis B: claim-binding, lifetime-escape, atomic-transition,
        verifier-completeness, repo-closure, proof-context
```

A task may activate several families.

## Route schema

```yaml
zig_semantic_route:
  route_version: ZSR-v1
  artifact_state:
    repository_root:
    head:
    dirty_fingerprint:
    zig_version:
  task_surfaces: []
  material: yes | no
  active_families: []
  no_family_reason:
  owner:
  concrete_counterexample:
  selected_repair_boundary:
  forbidden_shortcuts: []
  required_proof: []
  family_contracts: {}
```

## Family cues

### claim-binding

```text
fingerprint receipt certificate proof evidence ref cursor manifest
checkpoint replay attestation verify passed hash identity signature
```

### lifetime-escape

```text
parse decode arena buffer slice ref snapshot report certificate
returned field deinit reset refresh reallocate staging
```

### atomic-transition

```text
append put commit stage export import recover thaw restore replay
ledger journal outbox event pair ownership transfer later allocation
```

### verifier-completeness

```text
parser decoder binary protocol WASM archive inspector verifier
passed unknown section duplicate section varint LEB stack metadata export
```

### repo-closure

```text
new/moved/removed .zig file compile-fail fixture golden expected
generated output path list manifest registry aggregate lint
```

### proof-context

```text
proof test check CAS receipt stale head dirty tree commit push rebase
fork dependency cache permission worktree target optimize option
```

Broad words such as `proof`, `commit`, `manifest`, and `report` are family cues only when the repository/task is already known to be Zig.

## Materiality

Material:

- behavior changes;
- state or ownership changes;
- public/internal protocol changes;
- proof/certificate changes;
- generated artifacts;
- build/package/dependency changes;
- low-level/hazardous changes;
- test changes that authorize closure.

Usually non-material:

- typo-only docs;
- formatter-only work with no semantic token change;
- isolated comment correction;
- version-neutral question with no edit.

A non-material route may use `active_families: []`, but must name `no_family_reason`.

## Gate behavior

Mutation is blocked when:

- material work was not classified before the first edit;
- an active family lacks a family contract;
- owner or repair boundary is absent;
- no concrete counterexample exists for a claimed defect;
- required proof is empty;
- proof context is material but no epoch is required.

The route should be regenerated when a new counterexample changes the active family or owner.
