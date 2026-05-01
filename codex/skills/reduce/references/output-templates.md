# Output templates

Use the smallest template that satisfies the request and evidence level.

## Full audit template

```markdown
## Scope and assumptions

Inspected:
- ...

Not inspected:
- ...

Audit level: Full | Provisional

## Abstraction audit

| Abstraction | Evidence | T | V | D | Confidence | External-obligation risk | Verdict |
|---|---|---:|---:|---:|---|---|---|
| ... | ... | 2 | 1 | +1 | Medium | Low | slice |

## Prioritized cut list

### 1. <cut name>

- Current layer:
- Why it is costly:
- Proven value:
- Lower-level primitive:
- Smallest seam:
- Expected simplification:
- Blast radius:
- Compatibility risk:
- Rollback:

## Migration plan

### Phase 0 — proof and seam

- Change:
- Proof signal:
- Stop condition:
- Rollback:

### Phase 1 — first reduction

- Change:
- Proof signal:
- Stop condition:
- Rollback:

### Phase 2 — deletion or cleanup

- Change:
- Proof signal:
- Stop condition:
- Rollback:

## Patch guidance

- File/path:
- Suggested edit:
- Reason:
- Verification:

## Risks and unknowns

- ...
```

## Diagnostic template

Use this when evidence is incomplete.

```markdown
## Provisional audit

Available evidence:
- ...

Missing evidence:
- ...

## Observed abstraction candidates

| Candidate | Observed evidence | Likely tax | Confidence | Safe next verdict |
|---|---|---:|---|---|
| ... | ... | 2 | Low | wrap/slice only |

## Next evidence to collect

1. Inspect `<file>` to confirm build/test entry points.
2. Trace `<path>` from input to output.
3. Search for call sites of `<symbol>`.

## Safe near-term simplifications

- ...

## Deferred decisions

Do not recommend deleting/replacing these until evidence is collected:
- ...
```

## Quick profile template

Use this for a narrow user request or small excerpt.

```markdown
## Reduce profile

Likely cut: <name>
Verdict: keep | wrap | slice | replace | delete
Confidence: low | medium | high

Why:
- Tax:
- Value:
- Risk:

Smallest safe move:
- ...

Proof:
- ...

Rollback:
- ...
```

## Implementation-ready template

Use this when the user explicitly asks to implement a reduction.

```markdown
## Selected implementation phase

Chosen cut:
Phase:
Reason this phase is safe:

## Planned edits

| File | Edit | Behavior preserved |
|---|---|---|
| ... | ... | ... |

## Verification

Commands/signals:
- ...

## Rollback

- Revert files:
- Restore command/config:
- Re-enable compatibility wrapper:

## Non-goals

- ...
```

## Evidence ledger template

```text
Evidence ledger
- Abstraction:
- Paths/commands inspected:
- What the evidence proves:
- What the evidence does not prove:
- Agent-tax evidence:
- Value evidence:
- External-obligation risk:
- Confidence:
```

## Decision record template

Use this for a durable recommendation.

```markdown
# Reduce decision: <abstraction>

Date:
Scope:

## Decision

keep | wrap | slice | replace | delete

## Rationale

- T:
- V:
- D:
- Confidence:
- External-obligation risk:

## Evidence

- ...

## Migration

- Phase 0:
- Phase 1:
- Phase 2:

## Proof

- ...

## Rollback

- ...

## Open questions

- ...
```
