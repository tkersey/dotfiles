---
name: learnings
description: "Recall consequential lessons; assess reusable fixes, regressions, footguns, and strategy pivots. Establish the supported claim, applicability, and useful destination before retaining evidence. Use for lessons learned, learning correction, or memory admission and supersession. Delivery alone is not a trigger."
metadata:
  version: "8.5.0"
---

# Learnings

## Mission

Turn consequential experience into supported future decisions with the least
repeated reasoning. Establish what happened, what follows, and where the result
belongs before choosing retention. When canonical evidence adds value, maintain
project-scoped learnings through `$ledger` and selectively admit useful snapshots
to the native memory compiler. Worktrees share history, not artifact applicability.

Preserve what happened without overstating what follows. Capture the narrowest
useful claim supported by evidence; wider technical guidance must earn its scope.
Retrieval relevance is neither current applicability nor exclusion authority.

## Decision before retention

Use task evidence to answer three questions; reuse adequate answers already
established by the owning task rather than requiring a new packet:

1. **Claim:** distinguish the observation, inferred cause, and reusable rule.
   Keep the claim within the evidence, including uncertainty and untested scope.
2. **Applicability:** identify the conditions that make the claim relevant here
   and what current evidence establishes them. Similar wording or another
   worktree's success is not enough.
3. **Destination:** choose the existing owner that can preserve the useful
   consequence with the least future checking and maintenance.

| Useful consequence | Appropriate destination |
|---|---|
| An authorized construction can enforce the required behavior | The owning implementation, with preservation and boundary evidence. |
| A reproducible regression needs continued detection | An existing test or check, with its actual detection scope. |
| An enduring requirement or operating rule belongs to an established owner | That owner's policy or documentation. |
| A preference, retrieval hint, or ordinary cross-task context is sufficient | Native memory through its supported owner; no canonical row is required. |
| An experiment or conditional result still informs future choices | Canonical evidence when existing artifacts do not adequately preserve it. |
| A witnessed failure can justify excluding a route | Negative Ledger under its own applicability and lifecycle rules. |
| Existing artifacts already carry the useful result, or no transferable delta exists | No additional retention. |

These are choices, not an ordered pipeline. One experiment may remain useful even
after code absorbs its corrective lesson. Do not copy the same content into every
destination or introduce another store. Selection grants no new mutation authority;
an unimplemented proposal cannot replace a warning still needed today.

A construction can retire a reminder only for the domain whose admission,
permitted operations, and sanctioned paths actually enforce the required law while
preserving required-valid behavior. A regression test detects its exercised cases;
passing it alone does not establish that a failure family is unavailable. Reuse the
owning task's adequate proof; no extra proof ceremony is required by this skill.

## Canonical authority

For selected canonical retention or custom memory-source admission:

```text
definitions/ledger/learnings-protocol.json
  canonical passive protocol; learning records live under event.record

$ledger-resolved personal store + the definition's events logical slot
  canonical project history, independent of checkout lifetime

the selected memory root's extensions/learnings/notes/*.md
  immutable admission snapshots for Phase 2

memory_summary.md / MEMORY.md / skills/*
  compiled memory written only by Phase 2
```

`$ledger` alone owns storage location, registration, and migration policy.
Do not infer custody from the current checkout or duplicate that policy here.
Do not duplicate every learning into memory notes. For an accepted admission,
load `$memory-source-notes` before invoking its validated adapter in the same turn.

## Trigger Cues

- `$learnings`;
- browse, recent, search, rank, or summarize learnings;
- "what do we already know about X";
- a request for lessons learned or takeaways;
- fail-to-pass, pass-to-fail, timeout-to-stable;
- strategy pivot, footgun, gotcha, retry loop, or acceleration pattern;
- explicit request to promote/admit a learning to memory.

## Selected guidance

At a trigger, apply Decision before retention and Capture Gate from task evidence.
If no canonical write adds value and no canonical read or source-note lifecycle
work is needed, retain `no-op` and return without loading store/admission manuals,
resolving storage, or bootstrapping Ledger. Commit, PR creation, or handoff alone
is not a trigger.
Use an independently selected native-memory or implementation destination through
its owner; the canonical `no-op` does not prevent that authorized work.

| Selected operation | Read before the operation |
|---|---|
| Canonical browse, query, or recall | [store.md](store.md) and [recall.md](recall.md) |
| Accepted capture or canonical supersession | [store.md](store.md) and [capture.md](capture.md) |
| Authorized recovery of retired Learnings | [retired-import.md](retired-import.md); storage context remains owned by `$ledger`. |
| Evaluate or perform custom source-note admission, supersession, or withdrawal | [memory-admission.md](memory-admission.md); canonical operations also require store/capture guidance as applicable. |
| Generated digest | `$memory-source-notes`; no new canonical writer |

Canonical writes and derived admission remain separate outcomes; admission
failure cannot undo a successful canonical write. A no-op, duplicate, or
source-memory failure alone does not invalidate object-level delivery. Follow
enclosing read-only/effect authority on every route.

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
6. a correction to the scope or evidence of an existing learning.

Require decision delta, transferability, counterfactual cost, and value from
canonical retention beyond the selected existing destination. Prefer one
essential learning; append at most three per turn. Evaluate from task evidence
before bootstrap or store inspection when no recall/canonical operation is needed.
If the gate fails, retain `no-op` internally and continue the task.
The owning task adjudicates worker findings before capture; inherited reports and
repeated checks do not independently qualify as new learnings.

## Disposition Invariant

At each material Learnings activation, retain exactly one internal outcome:

```text
learning-disposition: appended id=lrn-...
learning-disposition: duplicate-skip reason=<reason>
learning-disposition: no-op reason=<no canonical write selected>
learning-disposition: blocked reason=<store selection, binding, or capture failure>
```

Do not claim Learnings closeout without a disposition. Keep `no-op` and
`duplicate-skip` internal unless asked; surface `blocked` when it affects delivery.
`no-op` includes an adequate existing construction, check, policy, or native-memory
destination, as well as a failed capture gate. It does not claim that no useful
work occurred or that a selected noncanonical effect succeeded.

## Memory Digest

`$memory-source-notes` owns generated Learnings digests and timestamped resources.
Ledger supplies only the deterministic source projection from resolved custody.

## Relationship to Negative Ledger

A learning can seed negative evidence, but it is not an operational route gate.
Promote witnessed failed hypotheses through the Negative Evidence definition's
`capture` transaction, then use its `memory-note` projection for admission.

## Guardrails

- Ground every row in observed evidence.
- Write bounded rules, not changelog bullets or unsupported universal claims.
- Select the intended personal store explicitly when no cataloged workspace applies.
- Do not force-add private canonical source stores.
- Do not bypass Ledger, edit persistent records, or fall back to checkout storage.
- Do not admit every learning to memory or write compiled memory directly.
- Do not use source notes to bypass canonical custody.
- Do not invoke a sibling source merely because Learnings activated.

For changes to learning-validation rules, use [validation-probes.md](validation-probes.md).
These are package evaluation cases, not a runtime checklist or capture prerequisite.
