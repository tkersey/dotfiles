# Memory Admission Gate

## Memory Admission Gate

A learning becomes a custom memory-source note only when all four checks pass:

1. the canonical row exists and its ID is known;
2. evidence is inspectable and embedded in a bounded snapshot;
3. scope and future behavior are clear;
4. Phase 2 consideration would plausibly reduce future steering, retries, or search.

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

After the source owner accepts admission, load `$memory-source-notes` and pass
the deterministic projection from the same resolved custody as capture/recall:

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection memory-note \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param id=lrn-... \
  --payload-only \
  --format json |
  run_memory_note_tool append \
    --extension learnings \
    --kind learning-admission \
    --json -
```

Do not reconstruct the payload from prose, `recent`, or query output. Projection
validates canonical custody and fails closed for a missing/incomplete row; it
does not decide eligibility. Definition-relative source locators are interpreted
through `$ledger`, not as files in a retired checkout. Do not rewrite old
provenance, fingerprints, or immutable notes during storage adoption.

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

## Supersession and Withdrawal

When a canonical learning is superseded or withdrawn from memory relevance,
append the new canonical row, create a `learning-supersession` or
`learning-withdrawal` note, reference the previous source-note ID when known,
and let Phase 2 update compiled memory surgically. Never edit/delete old notes.
