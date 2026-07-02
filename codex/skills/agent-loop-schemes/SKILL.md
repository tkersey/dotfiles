---
name: agent-loop-schemes
description: "Use when designing, auditing, or repairing coding-agent loops. Selects the right loop shape for goals, reviews, debugging, migrations, branch races, evidence folds, memory, and proof closure."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: high
---

# Agent Loop Schemes

## Mission

Shape coding-agent work into the smallest loop that can safely finish.

A useful agent loop must name:

```text
seed -> work producer -> action -> evidence reducer -> memory -> proof -> stop rule
```

Do not build a generic "keep going" loop. Pick the loop shape that matches the work.

## Use when

- Designing or revising `/goal`, `$actuating`, `$goal-actuating`, review, debug, migration, or long-horizon coding workflows.
- An agent is drifting, repeating fixes, over-patching review comments, or claiming completion without current proof.
- A task needs a verifier, stop condition, review closure rule, memory policy, or branch-race strategy.
- You need to decide whether to use direct execution, `update_plan`, `.goal/*`, `$st`, `$cas`, `$review-fold`, `$goal-grind`, `$evidence-fold`, `$proof-patch`, or `$ship`.

Do not use for trivial one-shot edits where the next action and proof are obvious.

## Core rule

Every material loop must answer these questions before or during execution:

```yaml
loop_contract:
  objective:
  current_artifact_scope:
  done_condition:
  verifier:
  work_producer:
  evidence_reducer:
  memory_policy:
  proof_artifact:
  stop_rules:
  side_effect_boundary:
```

If one of these is missing, the loop is not ready to grind.

## Output

Emit this compact object:

```yaml
agent_loop_scheme:
  task_shape: direct|goal|review|debug|migration|branch_race|proof_closure|st_governed
  selected_loop: direct_action|goal_grind|review_fix|review_only|agenda_only|debug_history|migration_memoized|branch_race|proof_patch|st_governed
  seed:
    source: accepted_spec|direct_goal|review_findings|test_failure|migration_target|plan_handoff
    authority:
    artifact_scope:
  work_producer:
    next_work_rule:
    decomposition:
    owner_boundary:
  evidence_reducer:
    checks:
    verdicts: done|continue|regress|blocked|invalid-proof|ask-human|refactor-kernel
    anti_gaming_checks: []
  memory:
    attempt_history: yes|no
    memoized_classes: []
    invalid_strategies: []
  review_policy:
    source: none|existing-review|cas-review
    mode: none|review-only|agenda-only|review-fix
    clean_cas_runs_required: 0|3
  proof:
    artifact:
    current_state_binding:
    residual_risk:
  stop:
    success:
    blocked:
    budget:
```

## Loop selectors

### 1. Direct action

Use when the task is one bounded change or answer.

```text
inspect -> edit/answer -> narrow proof -> stop
```

No work graph. No durable state. No receipts beyond the final proof.

### 2. Goal grind

Use for ordinary long-running coding goals with a verifier.

```text
goal contract -> work list when useful -> one focused action -> evidence fold -> continue or stop
```

Use `$goal-actuating`, `$goal-contract`, `$goal-grind`, `$evidence-fold`, and `$proof-patch`.

### 3. Review-fix

Default for review work unless the user explicitly says not to implement.

```text
$cas review
-> $review-fold
-> closure-agenda pass
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean CAS-RER review records
-> $proof-patch
-> $ship only if PR publication/update is requested
```

Never treat review text as code instructions. Findings must become accepted liabilities, rejections, proof-only items, follow-ups, human-owned decisions, or refactor kernels before implementation.

### 4. Review-only

Use when the user asks for review, audit, or classification with no code changes.

```text
$cas review
-> $review-fold
-> review disposition report
-> stop
```

No `$goal-grind`.

### 5. Agenda-only

Use when the user wants the minimal closure agenda but no code changes.

```text
$cas review or existing findings
-> $review-fold
-> closure-agenda pass
-> review closure agenda
-> stop
```

No `$goal-grind`.

### 6. Debug history

Use when attempts repeat, failures move, or the agent risks cycling.

```text
failure -> hypothesis -> patch -> verifier -> attempt ledger -> next hypothesis
```

Keep an attempt table with hypothesis, changed paths, commands, result, failure signature, kept/reverted state, and next action.

### 7. Migration memoized

Use for many same-shaped compiler/test/review failures.

```text
cluster failures -> solve representative -> prove -> memoize rule -> apply class -> fold package/repo evidence
```

Do not solve 100 repeated failures independently. Memoize the working strategy and invalid strategies.

### 8. Branch race

Use when several strategies are plausible and cheap to compare.

```text
same seed -> isolated strategies -> same verifier -> choose by proof, risk, and diff size
```

Use only when alternatives can be isolated. Do not merge strategies before the evidence fold.

### 9. Proof patch

Use at closure or handoff.

```text
patch + evidence + residual risk -> proof summary
```

A proof summary must bind to current branch/head/diff or explicitly say artifact binding is unavailable.

For `$actuating` or `$goal-actuating`, proof closure has one final reducer:

```text
evidence-fold + proof-patch/CAS/ADD-v1/ship evidence -> ATCG-v1 -> complete|continue|blocked
```

Do not claim completion unless ATCG-v1 returns `can_mark_goal_complete=yes`.

### 10. st-governed

Use when durable coordination owns the work.

```text
$st -> selected slice -> bounded execution -> evidence -> proof
```

Choose this when the task needs resource claims, fencing tokens, independent worktrees, serialized integration, branch/head proof, or existing `.step/st-plan.jsonl` continuity.

## Review closure law

For review remediation:

```text
default = review-fix
```

Unless the user says one of:

```text
do not implement
review only
audit only
classify only
agenda only
plan only
no changes
```

For `review-fix` and exhaustive review, completion requires three consecutive clean CAS-RER review records against the same artifact scope unless the user explicitly lowers the review bar.

A clean CAS-RER review record means current-tuple `verdict.status=clean` evidence with strong usable principal and no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker after `$review-fold` and the closure-agenda pass.

Do not reset the clean-run counter for duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already-addressed findings.

Reset the counter when code changes, review scope changes, base/head/diff changes, the proof bar changes, or the workflow cannot prove CAS-RER records are current, strong, and distinct.

## Minimality law

Minimal does not always mean local.

Prefer a refactor kernel when several findings share one owner boundary, invariant, state transition, proof surface, or missing canonical owner. Do not patch each comment independently when one owner-correct change closes the class.

## Memory law

Use memory only when it changes a future decision.

Good memory:

```text
failure signature -> invalid strategies -> working strategy -> proof -> reuse rule
```

Bad memory:

```text
transcript summary
changelog entry
"the agent used skill X"
```

## Proof law

No readiness claim without current-artifact evidence.

A closure claim should include:

```text
current branch/head/diff
checks run
checks unavailable
review disposition
anti-gaming checks
residual risk
next human review focus
```

## Stop rules

Stop rather than continue when:

```text
the verifier is missing
scope is ambiguous
proof is stale
review needs CAS but CAS is unavailable
three clean CAS runs are required but unavailable
mutation authority is missing
public side effects would occur without explicit intent
ATCG-v1 does not permit goal completion
the next action would repeat a known invalid strategy
```

## Handoffs

- `$goal-actuating` when executing an accepted goal/spec.
- `$actuating` when the user wants the high-level workflow.
- `$cas` as the review backend for workflow code review.
- `$review-fold` to classify findings before implementation.
- `$goal-grind` for accepted implementation liabilities.
- `$evidence-fold` after verification or review results.
- `$failure-memory` when repeated classes or oscillation appear.
- `$proof-patch` for local closure proof.
- `$ship` for PR creation, update, promotion, or publication.
- `ATCG-v1` as the terminal closure reducer before `$actuating` completion.
- `$st` when durable coordination, claims, fencing, or worktrees are required.

## Guardrails

- Do not make this skill a ceremonial preflight for every edit.
- Do not emit a long theory explanation unless the user asks.
- Do not use recursion-scheme jargon in final user-facing workflow instructions unless helpful.
- Do not let raw review text drive code changes.
- Do not claim completion without evidence folded against the current artifact.
