---
name: goal-actuating
description: "Execute an accepted spec or direct /goal through the recursive goal runtime. Lowers SGR-v2/spec intent into GC-v1, chooses lightweight vs review-first vs st-governed mode, optionally uses $cas as a review source, then runs goal-workgraph/goal-grind/evidence-fold/review-fold/proof-patch as needed."
metadata:
  version: "1.0.0"
  activation_cost: medium
  default_depth: high
---

# Goal Actuating

## Mission

Actuate a semantically closed spec through the goal-scheme runtime.

```text
accepted spec / SGR-v2 / direct goal
-> GC-v1 GoalContract
-> mode selection
-> WorkGraph when useful
-> one-node-at-a-time grind
-> evidence fold
-> proof patch
```

`$goal-actuating` is the recursive runtime owner. `$actuating` is the user-facing workflow façade that normally runs `$spec-pipeline -> $goal-actuating`.

## Inputs

Accept any of these:

```text
implementation_spec.md
SGR-v2 / spec governance receipt
PSR-v1 / policy handoff
review findings bound to a current diff
direct /goal text with enough proof surface
```

When SGR-v2 or an accepted spec is present, it is the semantic authority. Do not reinterpret scope, non-goals, compatibility posture, or proof bar.

## Modes

```yaml
goal_actuating_mode:
  source: direct-goal|spec-first|review-first|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: proof-only|minimal-fix|refactor-kernel|branch-race
  review: none|existing-review|cas-probe|cas-lane|adjudicate-first|proof-only|minimal-fix|refactor-kernel|st-governed
  closure: proof-patch|ship-handoff|blocked
```

### `spec-first`

Use after `$spec-pipeline` has produced an implementation spec or SGR-v2. Derive GC-v1 from the spec and execute without semantic drift.

### `direct-goal`

Use when the user goal already contains outcome, proof surface, non-goals, and constraints. If not, call `$goal-contract` or hand off to `$grill-me`.

### `review-first`

Use when review comments, CAS findings, or reviewer suggestions are present. Start with `$review-fold`; no code runs until findings are classified.

### `dry-plan`

Compile GC-v1 and optional WG-v1 only. Do not mutate. Use this when the user wants to inspect execution shape before implementation.

### `st-governed`

Use when PSR-v1, resource claims, fencing, worktrees, serialized integration, or existing `.step/st-plan.jsonl` / `.ledger/st` state must own execution. Hand off to `$st` and `$fixed-point-driver`; do not run direct mutation through goal-grind.

## Procedure

1. Locate the accepted spec, SGR-v2, PSR-v1, or direct goal source.
2. If no semantic closure exists, hand off to `$spec-pipeline` and stop until planning/execution is allowed.
3. Derive GC-v1 with `$goal-contract`; preserve spec authority exactly.
4. Select mode and persistence:
   - `update_plan` for lightweight session-local steps;
   - `goal-artifacts` when attempts/evidence/memo rows matter;
   - `st` when durable coordination, claims, fencing, worktrees, or serialized integration are required.
5. If review pressure exists or the proof bar asks for adversarial review, use the review backend policy below.
6. If decomposition changes execution, run `$goal-workgraph`.
7. Execute with `$goal-grind` one frontier node at a time unless in `st-governed` mode.
8. Run `$evidence-fold` after material verification or review results.
9. Run `$failure-memory` when failures or review classes repeat.
10. Close with `$proof-patch`, or hand off to `$ship` only when publication/PR delivery is requested and proven ready.

## Spec-to-contract lowering

Map spec fields into GC-v1:

```text
scope / objective              -> goal_contract.objective.summary
non-goals                      -> goal_contract.objective.non_goals
success bar / done state       -> goal_contract.done.success_state
proof bar / validation         -> goal_contract.verification.primary_checks
compatibility posture          -> goal_contract.constraints.compatibility
rollout / rollback             -> goal_contract.constraints and stop conditions
risk / blast radius            -> goal_contract.boundaries and proof bar
review expectations            -> goal_contract.review_policy
human-owned decisions          -> goal_contract.ambiguity.human_owned_decisions
planning/execution allowed     -> goal_contract.authority
```

## CAS review backend

`$goal-actuating` may use `$cas` as a **review source**, not as an implementation authority.

Use `$cas` review when one of these is true:

```text
the user asks for review closure or adversarial review
the accepted spec/SGR-v2 names review as part of the proof bar
review-first mode is selected and no current review artifact exists
repeated review cycles need a persistent detached lane
```

Do not run `$cas` review automatically on every goal. A goal can close without CAS review when its proof bar is satisfied by focused tests, static checks, artifact inspection, or existing review evidence.

### Review source modes

```yaml
review_source:
  mode: none|existing-review|cas-probe|cas-lane
  backend: none|github-comments|cas-review-session|native-review-fallback
  multi_agent_mode: explicit-request-only|proactive
  blocking: yes|no
```

- `existing-review`: consume current PR comments, existing CAS verdicts, or reviewer findings.
- `cas-probe`: run one bounded `$cas` review as adversarial discovery/proof input.
- `cas-lane`: use persistent CAS review lane for repeated review/fix cycles.
- `proactive`: discovery only by default; findings are not blocking until `$review-fold` accepts liability.

### CAS consumption rule

CAS output must pass through `$review-fold` before it can change code:

```text
$cas review verdict / findings
-> $review-fold
-> reject | proof-only | minimal-fix | refactor-kernel | ask-human | follow-up
-> $goal-grind only for accepted code-change liabilities
```

Treat CAS findings as claims until they are bound to current diff, intent, validity, liability, novelty, and disposition. CAS transport success, lane receipts, review thread IDs, or raw review text are not proof of readiness or mutation authority.

## Review behavior

Default review posture is `adjudicate-first`:

```text
review text -> classify -> compress -> decide -> only then implement accepted liabilities
```

Prefer no-code outcomes when they are correct:

```text
reject
proof-only
follow-up
ask-human
```

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

## Stop rules

Stop immediately when:

```text
semantic gate denies execution
scope would drift from accepted spec
review finding expands product/API scope
st-governed authority is required but absent
verification regresses
proof is stale or not current-artifact-bound
public tracker side effect would be needed without explicit intent
```

## Output

At closure, emit:

```text
Goal Actuation:
- source spec / SGR-v2 / PSR-v1:
- mode / persistence:
- review_source / CAS backend, if any:
- GC-v1 summary:
- WorkGraph / frontier:
- review-fold disposition, if any:
- evidence-fold verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
