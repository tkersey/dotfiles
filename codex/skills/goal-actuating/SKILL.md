---
name: goal-actuating
description: "Execute an accepted spec or direct /goal through the recursive goal runtime. Lowers SGR-v2/spec intent into GC-v1, chooses lightweight vs review-first vs st-governed mode, requires $cas for workflow code review, then runs goal-workgraph/goal-grind/evidence-fold/review-fold/proof-patch as needed."
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
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive|adjudicate-first|proof-only|minimal-fix|refactor-kernel|st-governed
  closure: proof-patch|ship-handoff|blocked
```

- `spec-first`: derive GC-v1 from accepted spec/SGR-v2 and execute without semantic drift.
- `direct-goal`: use only when the goal already has outcome, proof surface, non-goals, and constraints.
- `review-first`: use when review comments, CAS findings, or reviewer suggestions are present.
- `dry-plan`: compile GC-v1 and optional WG-v1 only; do not mutate.
- `st-governed`: hand off to `$st` and `$fixed-point-driver` when PSR-v1, claims, fencing, worktrees, serialized integration, or existing `.step/st-plan.jsonl` / `.ledger/st` state must own execution.

## Procedure

1. Locate the accepted spec, SGR-v2, PSR-v1, or direct goal source.
2. If no semantic closure exists, hand off to `$spec-pipeline` and stop until planning/execution is allowed.
3. Derive GC-v1 with `$goal-contract`; preserve spec authority exactly.
4. Select `update_plan`, `goal-artifacts`, or `st` persistence.
5. If the workflow performs code review, use `$cas` review under the mandate below.
6. If existing external review pressure is present, classify it with `$review-fold`.
7. If decomposition changes execution, run `$goal-workgraph`.
8. Execute with `$goal-grind` one frontier node at a time unless in `st-governed` mode.
9. Run `$evidence-fold` after material verification or review results.
10. Run `$failure-memory` when failures or review classes repeat.
11. Close with `$proof-patch`, or hand off to `$ship` only when publication/PR delivery is requested and proven ready.

## Spec-to-contract lowering

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

## CAS review mandate

If `$goal-actuating` does code review, the backend is `$cas`. No generic reviewer, ad-hoc critique, prose pass, or non-CAS subagent review substitutes for workflow-initiated code review.

Use `$cas` review when any of these are true:

```text
the user asks for code review, review closure, adversarial review, or exhaustive review
the accepted spec/SGR-v2 names review as part of the proof bar
review-first mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
proof-patch or ship-handoff would otherwise rely on a review claim
```

A goal may close without code review only when its accepted proof bar does not require review and focused tests/static checks/artifact inspection are sufficient. Once a review gate is present, CAS review is mandatory.

```yaml
review_source:
  mode: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  backend: none|github-comments|cas-review-session
  multi_agent_mode: explicit-request-only|proactive
  blocking: yes|no
```

- `existing-review`: consume already-existing PR comments, prior CAS verdicts, or human reviewer findings; this does not count as a new workflow-initiated code review.
- `cas-probe`: run one bounded `$cas` review as adversarial discovery/proof input.
- `cas-lane`: use persistent `$cas` review lane for repeated review/fix cycles.
- `cas-exhaustive`: use `$cas` review as a blocking exhaustive review gate; continue review/fix/fold cycles until CAS is clean, blocked, or all findings are dispositioned with current-artifact proof.
- `proactive`: discovery breadth for CAS review; findings still require `$review-fold`, but exhaustive review itself is not skipped or replaced.

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

Prefer no-code outcomes when they are correct: `reject`, `proof-only`, `follow-up`, or `ask-human`.

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

Exhaustive review is not optional once requested or named by the proof bar. `$review-fold` controls which findings become code changes; it must not minimize away the CAS review gate itself.

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
code review is required but $cas review is unavailable or not run
```

## Output

At closure, emit:

```text
Goal Actuation:
- source spec / SGR-v2 / PSR-v1:
- mode / persistence:
- review_source / CAS backend, if any:
- CAS review verdict / lane, if review was required:
- GC-v1 summary:
- WorkGraph / frontier:
- review-fold disposition, if any:
- evidence-fold verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
