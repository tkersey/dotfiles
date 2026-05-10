# Fixed-Point Driver Integration

Use `negative-ledger` as a routine companion protocol for non-trivial `fixed-point-driver` runs. The goal is to preserve decision-shaping negative evidence, avoid repeated dead ends, and keep stale failures reopenable when the artifact state changes.

This is stronger than optional trigger-only use: fixed-point-driver should run a root-owned Negative Ledger Pass even when the result is `no-applicable-negative-evidence`.

## Required fixed-point use

For every non-trivial fixed-point run:

1. Establish `artifact_state_id` and `artifact_state_label`.
2. Run a root-owned negative-ledger `query`/`map` pass during routing preflight.
3. Normalize candidate evidence into the Negative Evidence Ledger.
4. Decide applicability: `active`, `stale`, `superseded`, `reopened`, `unknown`, or `need-evidence`.
5. Convert active entries into narrow exclusion rules.
6. Convert stale/reopened entries into explicit proof prompts or reopening tests.
7. After failed/no-effect/regression/revert/rejection/pivot events, run capture decision.
8. Before the one-change challenge, run a pre-closure negative-ledger `handoff`.
9. Carry the Negative Evidence Closure Gate into `verification-closure`.

## When root-owned pass is enough

The root-owned pass is enough when:
- no candidate evidence is found
- one or two learnings are easy to inspect
- the negative-evidence result does not change route choice
- evidence is local to current-run ledgers
- the only needed outcome is `no-applicable-negative-evidence`

Record the result visibly. Do not collapse it into implicit doctrine.

## When to invoke negative-ledger-mapper

Invoke `negative-ledger-mapper` when at least one is true:

- multiple prior failed attempts may apply
- evidence is spread across learnings, review comments, repo history, logs, and current ledgers
- benchmark regressions or optimization dead ends materially shape route choice
- repeated hypotheses or strategy pivots are recurring across loops
- stale/superseded evidence may be reopened by current artifact changes
- the one-change challenge risks selecting a previously disconfirmed route
- the debugging/migration/performance search space is broad enough that read-only pruning can materially reduce waste

## Do not invoke mapper for

- trivial one-pass implementation
- no current-state applicability question
- pure proof-command execution
- exact duplicate of a valid existing packet
- route choices where the root-owned pass already found no applicable negative evidence

## Root versus specialist authority

`fixed-point-driver` root owns:

- authoritative fmt/lint/build/test commands
- final closure verdict
- canonical ledgers
- deciding whether to reopen the loop
- final negative-evidence applicability decisions
- durable writeback decisions

`negative-ledger-mapper` may:

- read current campaign ledgers, `$learnings` recall output, logs, review comments, diffs, and commit/revert evidence
- classify prior failed attempts
- mark evidence active, stale, superseded, reopened, unknown, or need-evidence
- recommend active exclusions and adjacent search frontier
- recommend reopening tests

`negative-ledger-mapper` must not:

- edit files
- run final proof gates
- claim closure
- veto current work without current-state applicability evidence
- append to `$learnings` during read-only specialist mapping

## Recommended fixed-point sequence

1. Establish `artifact_state_id` and `artifact_state_label`.
2. Run root-owned Negative Ledger Pass.
3. Optionally launch `negative-ledger-mapper` with a narrow scope when history mapping is read-heavy.
4. Validate the specialist packet: state ID, scope, footer, and absence of transport wrappers.
5. Normalize accepted entries into the canonical Negative Evidence Ledger.
6. Use active entries to avoid exact repeated dead ends.
7. Use stale/reopened entries to plan current proof, not to suppress work.
8. Before the one-change challenge, check whether the candidate matches active negative evidence.
9. Before final closure, emit Negative Ledger Handoff.
10. After a witnessed failed/no-effect/regression loop, capture durable negative evidence through `$learnings` when transferable.

## Specialist packet footer

Every packet must end with:

```md
artifact_state_id: ...
artifact_state_label: ...
scope: ...
top_material_signals:
  - ...
unresolved_signals:
  - ...
agreement_pressure: aligned | mixed | conflicting | unknown
stale: yes | no | unknown
final_call: ...
```

Reject the packet as `transport-invalid`, `wrong-scope`, or `stale` when it violates the common specialist packet rules.

## Value receipt for mapper

Every `negative-ledger-mapper` packet gets a Specialist Value Receipt.

It is value-positive when it changes at least one of:
- active exclusions
- reopened/stale/superseded classification
- route choice
- one-change challenge result
- verification plan
- safest next frontier

It is value-neutral when it confirms no applicable negative evidence without changing route or proof.
It is value-negative when stale, wrong-scope, transport-invalid, or duplicative.
