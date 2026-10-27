# Reduce output templates

## Full audit

```md
## Scope and assumptions
- Scope:
- Evidence present:
- Evidence missing:
- Provisional: yes/no

## Current altitude map
- Altitude 0 / platform primitives:
- Altitude 1 / explicit local code:
- Altitude 2 / domain invariants:
- Altitude 3 / protocols/interpreters:
- Altitude 4 / framework/tooling:
- Altitude 5 / distributed/platform:

## Evidence ledger
| Evidence | What it proves | What it does not prove | Confidence |
|---|---|---|---|

## Abstraction audit table
| Abstraction | Evidence | Tax drivers | Agent counters | Proven value | T | V | D | Confidence | External risk | Essential abstraction | Verdict | Lower primitive / reason to keep |
|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|

## Prioritized cut list
1.

## Migration plan
| Phase | Change | Proof | Rollback | Stop condition |
|---|---|---|---|---|

## Patch suggestions

## Risks and unknowns
```

## Quick audit

```md
Top 3:
1. <abstraction> — verdict: <keep|wrap|slice|replace|delete>; evidence: <one sentence>; first safe move: <...>; biggest unknown: <...>; essential check: <...>
2.
3.
```

## Implementation handoff

```md
move: descend | split
scope:
layer:
verdict:
lower_primitive:
essential_truth_to_preserve:
compatibility_boundary:
first_safe_phase:
files_expected:
proof_signal:
rollback:
stop_condition:
```

## Provisional cap language

Use this when evidence is incomplete:

```md
This audit is provisional because <missing evidence>. I would not recommend delete/replace yet. The safe move is <wrap|slice|hold> until <proof or owner confirmation> exists.
```
