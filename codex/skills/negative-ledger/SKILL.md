---
name: negative-ledger
description: "Recall prior attempts or handle witnessed failed/no-effect routes, regressions, reverts, abandoned strategies, repeated retries, and negative-evidence lifecycle or memory admission. Not ordinary successful closeout."
metadata:
  version: "8.3.1"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.

The structural boundary is the passive definition:

```text
${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json
```

Its `events` logical slot in `$ledger`-resolved custody is canonical. The Ledger
skill alone owns physical storage location, worktree-family registration,
initialization, and migration policy. Do not derive a separate history from each
checkout. Worktrees share evidence, not automatic applicability or exclusions.

The derived memory-admission channel remains:

```text
~/.codex/memories/extensions/negative-ledger/notes/*.md
```

`$negative-ledger` owns the meaning and lifecycle of negative-evidence state.
Ledger replays/projects the declared protocol without semantic authority.
`memory-note` transports an immutable projection to Phase 2, which decides
whether to compile a route constraint, routing trigger, or reusable memory skill.

Never use memory notes as the operational route gate. For accepted admission,
load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$negative-ledger`;
- failed/no-effect attempts, reverts, benchmark/test regressions;
- repeated semantic routes or same-cluster retries;
- strategy pivots abandoning a concrete route future work might repeat;
- "what have we already tried?" or "do not retry this route";
- route reopening after artifact-state changes;
- fixed-point or review-governor negative evidence;
- memory admission of active/stale/reopened/superseded `NEG-*` projections.

## Activation Policy

Activation is broad; capture is narrow.

Invoke implicitly when work may change route selection because a concrete route
failed, had no effect, regressed a signal, was reverted, was rejected by current
proof/review evidence, or is about to be retried under the same cluster. Do not
wait for the user to name the skill.

Before selecting a route resembling a prior failure, project canonical
`route-gate`. A recalled learning may trigger the check, not block directly.
After a material strategy pivot, regression-confirmed revert, or closeout leaving
a failed route likely to recur, evaluate capture. A transient red test, syntax
error, first incomplete implementation, or discarded typo is `no-op` unless it
exposes a durable failed hypothesis that changes future routing.

Retain exactly one internal disposition for each material activation:

```text
mapped       current ledger checked; no write required
captured     witnessed negative evidence appended
transitioned existing NEG record changed lifecycle state
no-op        activation evaluated; evidence was not durable or route-shaping
blocked      context/store unavailable or invalid, or an active applicable exclusion matched
```

A material closeout without failed-route semantics does not activate this source.
Do not resolve storage, query, doctor, or capture to manufacture a no-op receipt.

## Valid Statuses

```text
capture_candidate
need-evidence
unknown
active
accepted_risk
stale
reopened
superseded
```

Only `active` may block: witness evidence, valid exclusion scope, current artifact
applicability, and exact-enough route/cluster matching are all required. Fuzzy or
lexical overlap is suggest-only.

## Selected guidance

Evaluate from task evidence before resolving storage. A transient failure without
a durable route-shaping hypothesis needs only this entrypoint: retain `no-op` and
return. Do not read operation manuals merely because the skill activated.

| Selected work | Required guidance before that decision or effect |
|---|---|
| Canonical recall, projection, or any native operation | [store.md](references/store.md); `$ledger` owns bootstrap and custody. |
| Select a retry resembling prior failure | Store guidance and [route-gate.md](references/route-gate.md); read and interpret the canonical gate before selection. |
| Capture or promote negative evidence, or challenge an exclusion's scope | [capture.md](references/capture.md); scope challenge precedes capture/promotion. Canonical operations also require store guidance. |
| Transition, reopen, narrow, or supersede a record | [lifecycle.md](references/lifecycle.md), with its selected capture/scope guidance; canonical operations also require store guidance. |
| Admit or update a derived memory snapshot | [memory-admission.md](references/memory-admission.md) and store guidance; load `$memory-source-notes` before transport. |

A selected reference is mandatory, not optional background. Several operations
may apply to one task; load each before its first governed decision and reuse
unchanged guidance. Selection does not grant mutation, retry, admission, or
publication authority. Explicit read-only/no-file limits remain binding.

An active exact applicable exclusion stays binding until its legal source-owned
lifecycle changes it. Do not bypass it by calling a retry a test, sandbox, or
experiment. A failed context or gate lookup is unavailable evidence, not an
empty history; continue only independent authorized work.

## Canonical Store and CLI

Read [store.md](references/store.md) before any canonical operation.

## Route-Gate Workflow

Read [route-gate.md](references/route-gate.md) before selecting a resembling retry.

## Capture Workflow

Read [capture.md](references/capture.md) before capture or promotion.

## Exclusion Scope Challenge

Read the [scope challenge](references/capture.md#exclusion-scope-challenge) before
capture/promotion or deciding a challenged exclusion's breadth. A failed
implementation alone does not justify excluding a strategy.

## Lifecycle Transitions

Read [lifecycle.md](references/lifecycle.md) before transitions or reopening.

## Memory Admission Gate

Read [memory-admission.md](references/memory-admission.md#memory-admission-gate)
before deciding admission; canonical capture does not automatically qualify.

## Admission Workflow

After accepted admission, follow the
[admission workflow](references/memory-admission.md#admission-workflow).

## Proof Lines

[Store guidance](references/store.md#proof-lines) owns the existing reporting
forms. Report canonical writes and derived admissions separately; a later
admission failure never rolls back a successful canonical write.

## Learnings Relationship

Learnings are historical candidate evidence, not route exclusions. Retired source
stores are addressed only during owner-authorized recovery. Verify current
applicability and promote qualifying evidence through canonical `capture`.

## Guardrails

- Do not record vibes or turn one failed implementation into a broad strategy ban.
- Do not block from fuzzy matches or use stale benchmarks without applicability.
- Do not treat absence of an entry as novelty proof.
- Do not bypass Ledger, hand-edit records, or use a checkout-local fallback.
- Do not let memory notes outrank canonical custody or write compiled memory.
- Do not publish incomplete projections or capture every transient red test.
- Failed context, route-gate, memory-note, or doctor boundaries fail closed.
- Do not invoke sibling sources merely because Negative Ledger activated.

For exclusion-scope changes, use Negative Ledger cases in
[validation-probes.md](../learnings/validation-probes.md). These are package
validation, not a runtime dependency or activation of Learnings.
