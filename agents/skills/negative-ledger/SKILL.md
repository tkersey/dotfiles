---
name: negative-ledger
description: "Check prior failures before consequential retries; assess what durable failures, reverts, and pivots establish and where useful evidence belongs. Use when a failed approach can change future routing, or for exclusion scope, lifecycle, and memory corrections. Skip ordinary successful closeout and transient errors without a durable failed hypothesis."
metadata:
  version: "8.5.0"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.
Establish the supported claim and its applicability, then choose where it can
reduce future repeated reasoning. Invocation need not produce a record.

## Evidence and destination

Before optional capture, answer from available task evidence:

1. **What does this establish?** Separate the observed outcome, inferred cause,
   and proposed exclusion. A failed implementation or an inconclusive experiment
   does not establish that the strategy cannot work.
2. **What makes it applicable here?** Identify the material artifact, mechanism,
   workload, and requirement conditions. Preserve uncertainty outside the tested
   or justified domain. Existing exclusions still require the canonical gate.
3. **Where will it save future reasoning?** Reuse an adequate construction,
   regression check, standing policy, or native memory when it already serves the
   needed decision. Retain an experiment with its existing owner when its setup,
   result, and limits matter without supporting a ban. Select canonical negative
   evidence when its scoped history or exclusion lifecycle adds decision value.

Choose by the required future use, not a fixed storage hierarchy. Ordinary native
memory needs no new `NEG-*` record; it cannot acquire operational exclusion
authority. If another destination suffices, retain `no-op` without bootstrapping
storage. Explicit canonical operations and applicable route checks still run.

Within the task's implementation authority, prefer a construction that prevents
the supported failure while preserving required-valid behavior when adequate.
Bind that claim to the enforced boundary, permitted operations, and covered
variants; a passing regression test alone establishes neither family prevention
nor removal of all bypasses. Keep useful experiment history even when a warning
becomes redundant. Construction work and reminder retirement remain subject to
their existing owners; a repair proposal grants neither mutation nor a retry.

## Canonical authority

The structural boundary is the passive definition:

```text
${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json
```

Its `events` logical slot in the `$ledger`-resolved personal store is canonical.
The Ledger skill owns storage location, the personal catalog, initialization, and
migration policy. Explicit store selection works without Git; checkout lifetime
does not own history. Worktrees share evidence, not automatic applicability.

The derived memory-admission channel remains:

```text
the selected memory root's extensions/negative-ledger/notes/*.md
```

`$negative-ledger` owns the meaning and lifecycle of negative-evidence state.
Ledger replays/projects the declared protocol without semantic authority.
`memory-note` transports an immutable projection to Phase 2, which decides
whether to compile a route constraint, routing trigger, or reusable memory skill.

Never use memory notes as the operational route gate. For accepted admission,
load `$memory-source-notes` before invoking its validated adapter in the same turn.

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

Before selecting a route resembling a prior failure, discover canonical
`route-candidates` using component, invariant, and failure-mechanism terms.
Assess material candidates against the current artifact, then project the exact
`route-gate` using established identities. A route-label miss is not absence of
relevant evidence. A recalled learning may trigger the check, not block directly.
After a material strategy pivot, regression-confirmed revert, or closeout leaving
a failed route likely to recur, evaluate evidence and destination before capture.
A transient red test, syntax error, first incomplete implementation, or discarded
typo is `no-op` unless it
exposes a durable failed hypothesis that changes future routing.

Retain exactly one internal disposition for each material activation:

```text
mapped       current ledger checked; no write required
captured     witnessed negative evidence appended
transitioned existing NEG record changed lifecycle state
no-op        no new canonical record needed; another destination suffices or evidence does not qualify
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
applicability, authoritative lifecycle state, and exact-enough route/cluster
matching are all required. A potentially missing relevant transition leaves the
gate unresolved; a readable partial history is still useful evidence. Fuzzy or
lexical overlap is suggest-only.

## Selected guidance

Evaluate evidence and destination before resolving storage unless a canonical
operation or relevant route check is required. A transient failure or an adequate
existing destination needs only this entrypoint: retain `no-op` and return.
Do not read operation manuals merely because the skill activated.

| Selected work | Required guidance before that decision or effect |
|---|---|
| Canonical recall, projection, or any native operation | [store.md](references/store.md); `$ledger` owns bootstrap and custody. |
| Select a retry resembling prior failure | Store guidance and [route-gate.md](references/route-gate.md); discover candidates, assess applicability, and interpret the exact gate before selection. |
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
- A failed canonical read is unavailable evidence, not an empty result. A failed
  memory admission does not invalidate independent canonical writes or delivery.
- Do not invoke sibling sources merely because Negative Ledger activated.

For exclusion-scope changes, use Negative Ledger cases in
[validation-probes.md](../learnings/validation-probes.md). These are package
validation, not a runtime dependency or activation of Learnings.
