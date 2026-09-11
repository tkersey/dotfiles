---
name: learnings
description: "Capture or recall evidence-backed execution learnings; evaluate capture at validation transitions, strategy pivots, footguns, retry loops, and material delivery or handoff. Also handle explicit learning-memory admission and supersession."
metadata:
  version: "8.1.0"
---

# Learnings

## Mission

Maintain a repo-local, evidence-backed execution-learning store and selectively admit only high-value learning snapshots to the global Codex memory compiler.

Authority split:

```text
definitions/ledger/learnings-protocol.json
  canonical passive protocol; learning records live under event.record

<repo>/.ledger/learnings/events.jsonl
  canonical repo-local store

~/.codex/memories/extensions/learnings/notes/*.md
  immutable admission snapshots for Phase 2

memory_summary.md / MEMORY.md / skills/*
  compiled memory written only by Phase 2
```

Do not duplicate every learning into memory notes. For an accepted admission, load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$learnings`;
- browse, recent, search, rank, or summarize learnings;
- "what do we already know about X";
- lessons learned, takeaways, wrap up, or handoff;
- fail-to-pass, pass-to-fail, timeout-to-stable;
- strategy pivot, footgun, gotcha, retry loop, or acceleration pattern;
- before a Codex-made commit/PR/handoff after material implementation;
- explicit request to promote/admit a learning to memory.

## Selected guidance

At a delivery/capture trigger, evaluate Capture Gate below from task evidence
first. If it fails and no recall or canonical operation was requested, retain
`no-op` and return without loading store/admission manuals or bootstrapping Ledger.
The delivery-time evaluation remains mandatory; an append remains conditional.

| Selected operation | Read before the operation |
|---|---|
| Canonical browse, query, or recall | [store.md](store.md) and [recall.md](recall.md) |
| Accepted capture or canonical supersession | [store.md](store.md) and [capture.md](capture.md) |
| Evaluate or perform memory admission, supersession, or withdrawal | [memory-admission.md](memory-admission.md); canonical operations also require the store/capture guidance as applicable. |
| Generated digest | `$memory-source-notes`; no new canonical writer |

Do not admit every capture to memory. Canonical writes and derived admission
remain separate outcomes; admission failure cannot undo a successful canonical
write. A no-op, duplicate, or source-memory failure alone does not invalidate
object-level delivery. Follow enclosing read-only/effect authority on every route.

<a id="canonical-store"></a>
Canonical Store: [store.md](store.md#canonical-store).
<a id="write-workflow"></a>
Write Workflow: [capture.md](capture.md#write-workflow).
<a id="recall-workflow"></a>
Recall Workflow: [recall.md](recall.md#recall-workflow).
<a id="memory-admission-gate"></a>
Memory Admission Gate: [memory-admission.md](memory-admission.md#memory-admission-gate).
<a id="definition-projection-and-admission"></a>
Definition projection and admission: [memory-admission.md](memory-admission.md#definition-projection-and-admission).
<a id="admission-proof"></a>
Admission Proof: [memory-admission.md](memory-admission.md#admission-proof).
<a id="supersession-and-withdrawal"></a>
Supersession and Withdrawal: [memory-admission.md](memory-admission.md#supersession-and-withdrawal).

## Capture Gate

Capture only when at least one decision-shaping event occurred:

1. validation transition;
2. strategy pivot;
3. hidden footgun or brittle assumption;
4. repeated acceleration pattern;
5. useful or failed recalled learning;
6. delivery boundary after real implementation work.

Require decision delta, transferability, and counterfactual cost. Prefer one essential learning; append at most three per turn.

Evaluate this gate from available task evidence before bootstrap or store inspection
when no recall or canonical operation is needed. If it does not pass, retain `no-op`
internally and continue the task.

## Disposition Invariant

At each material Learnings activation, retain exactly one internal outcome:

```text
learning-disposition: appended id=lrn-...
learning-disposition: duplicate-skip reason=<reason>
learning-disposition: no-op reason=<capture gate not met>
learning-disposition: blocked reason=<doctor, binding, or capture failure>
```

Evaluation is mandatory once the source is materially activated; append is
conditional. Do not claim Learnings closeout without a disposition. Keep
`no-op` and `duplicate-skip` internal unless the user asks, while `blocked` is
user-visible when it affects delivery.

## Memory Digest

`$memory-source-notes` owns generated Learnings digests and their timestamped
resources. Ledger supplies only the deterministic source projection.

## Relationship to Negative Ledger

A learning can seed negative evidence, but the learning source is not the
operational route-exclusion store. Promote witnessed failed hypotheses through
the Negative Evidence definition's `capture` transaction, then use its
`memory-note` projection for admission.

## Guardrails

- Ground every row in observed evidence.
- Write rules, not changelog bullets.
- Do not append from an unverified non-repo cwd.
- Do not force-add local-only source stores.
- Do not bypass the Ledger API or edit persistent-adapter records directly.
- Do not admit every learning to memory.
- Do not write compiled memory directly.
- Do not use source notes to bypass the canonical store.
- Do not invoke a sibling source merely because Learnings activated.
