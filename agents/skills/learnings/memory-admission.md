# Memory Admission Gate

## Memory Admission Gate

This gate governs the custom Learnings source-note channel. Ordinary preferences,
retrieval hints, and context can use the host's supported native-memory workflow
directly when that is sufficient; do not bootstrap Ledger or manufacture a
canonical row to make them eligible. That route does not permit hand-editing
compiled memory or representing an unadmitted canonical claim as authoritative.

A learning becomes a custom memory-source note only when all four checks pass:

1. the canonical row exists and its ID is known;
2. evidence is inspectable and embedded in a bounded snapshot;
3. scope and future behavior are clear;
4. Phase 2 consideration would plausibly reduce future steering, retries, or search
   beyond the useful consequence already carried by existing artifacts.

At least one must also hold:

- status is `codify_now`;
- the same theme appears at least three times;
- the user explicitly asks to remember/promote it;
- it captures a stable cross-task preference or operating default;
- it is an unusually high-impact failure shield, repo map, verification path, or stop rule;
- it proves a repeatable procedure suitable for a memory-root skill.

Do not admit every `do_more` row, raw chronology, weak `review_later` candidates,
failed-hypothesis exclusions better owned by `negative-ledger`, operating
corrections better handled as standing policy, or synesthetic mappings.

When a construction now enforces a previously remembered rule, assess whether a
small retrieval hint still helps. Retire the redundant reminder through its owner
only for the supported domain; retain useful experiment evidence and guidance for
unrepaired versions. A test's passing cases alone do not justify a claim that all
old failures have become impossible. A source-note withdrawal removes admission
support, not the truth of the historical observation.

## Technical generalization

Before admitting a generalized technical procedure, operating default, or
failure shield, verify that evidence supports the scope of future behavior.
`codify_now`, recurrence, and a request to remember are eligibility signals, not
proof. Repeating one narrow fixture does not establish broader applicability.

Identify the most plausible false application within the proposed scope. Use
existing inspectable evidence or, when needed and authorized, a discriminating
boundary check proportionate to breadth and consequence. Confirm the case
exercises the rule, its oracle follows an independent requirement, and any
failure concerns the rule rather than an invalid fixture, unrelated defect, or
environment failure. A suspected counterexample is not an executed result;
passing tests do not prove unrestricted generality.

When refining a rule from a counterexample, preserve and recheck the original
supporting case, replay the challenge, and check a distinct relevant boundary
before claiming generalization. Reuse adequate tests or proofs; do not require
fixed rounds, a challenger agent, or new experiments for every admission.
If execution is unavailable/unauthorized, narrow to supported guidance or defer
elevation rather than inventing validation. Capture/admission remain separate;
insufficient validation does not invalidate a sound canonical capture or
independent object-level delivery.

For variable model/workflow outcomes, a failed run followed by a successful run
does not establish causality. Use matched/repeated comparisons for consequential
causal claims; otherwise retain uncertainty. For deterministic properties,
prefer direct checks or proofs of the condition.

User preferences and requirements derive authority from their source; do not
subject them to technical falsification. A narrow observation can be useful
without becoming universal. If validation narrows/replaces a canonical claim,
update it through capture/supersession before admission. Never edit the projection
to smuggle in a revised rule. Stop when scope is supported, narrowed, or elevation
deferred; do not manufacture rows or validation loops.

## Definition projection and admission

After the source owner accepts admission, load `$memory-source-notes` and use its
validated adapter with the same resolved custody as capture/recall:

```bash
uv run \
  "$memory_source_notes_root/scripts/source_memory_note.py" append \
  --source learnings --operation admit \
  --catalog-root "$ledger_home" --store-id "<context.store_id>" \
  --id lrn-... \
  --codex-home "<layout.codex_home>" --memory-version "<layout.memory_version>"
```

Do not reconstruct the payload from prose, `recent`, or query output. The adapter
obtains the canonical projection and retains canonical relationships as source
provenance, not memory-note identities. It fails closed for invalid custody or a
missing/incomplete row; it does not decide eligibility. Source locators are interpreted
through `$ledger`, not as files in a retired checkout. Do not rewrite old
provenance, fingerprints, or immutable notes during storage adoption.

The writer and reader use the same configured memory root, selected by the
memory owner. Do not hardcode the unversioned directory, dual-write versions, or
admit a backlog wholesale. Canonical retention does not imply memory eligibility.

## Admission Proof

When user-visible or actionable, report canonical and admission outcomes separately:

```text
appended: id=lrn-...
memory-note: id=MSN-... extension=learnings kind=learning-admission status=created
```

If the CLI is unavailable:

```text
appended: id=lrn-...
memory-note: not-attempted: cli unavailable
```

Failed admission never rolls back or invalidates the canonical append.
Persistence, reader visibility, and explicit compiled attribution are different
observations. A compact summary may omit source IDs; omission alone does not
establish failed delivery or compilation lag.

## Supersession and Withdrawal

When the canonical claim changes, append its supported correction through
capture/supersession. When only the reminder loses value, preserve the true
canonical history; no new row or fabricated correction is required.

Use the [managed reminder update](../memory-source-notes/SKILL.md#managed-reminder-updates)
with `--source learnings`, the canonical `--id`, exact `--prior-note-id MSN-...`,
and source-approved reason/evidence. `--operation supersede` emits
`learning-supersession`; `--operation retract` emits `learning-withdrawal`.
The prior note must be resolved, not merely referenced when convenient. If it
cannot be identified, leave the update blocked rather than claim withdrawal.

Preserve guidance for unrepaired versions when narrowing a reminder. Reconcile
source and note identity through the supported reader; a correction note alone
is not proof of downstream invalidation. Phase 2 owns compiled memory. Never
edit/delete old notes or compiled memory.
