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

Do not admit every `do_more` row, raw chronology, weak `review_later` candidates, failed-hypothesis exclusions better owned by `negative-ledger`, operating-correction events better handled as standing policy, or synesthetic mappings.

## Definition projection and admission

After the source owner accepts admission, load `$memory-source-notes` and pass
the deterministic definition projection to the general writer:

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection memory-note \
  --repo "<repo-root>" \
  --param id=lrn-... \
  --payload-only \
  --format json |
  run_memory_note_tool append \
    --extension learnings \
    --kind learning-admission \
    --json -
```

Do not reconstruct the payload from prose, `recent`, or query output. The
projection validates the canonical store and fails closed for a missing or
incomplete row; it does not decide admission eligibility.

## Admission Proof

When admission is user-visible or actionable, report canonical and admission
outcomes separately:

```text
appended: id=lrn-...
memory-note: id=MSN-... extension=learnings kind=learning-admission status=created
```

If the CLI is unavailable:

```text
appended: id=lrn-...
memory-note: not-attempted: cli unavailable
```

A failed memory admission must never roll back or invalidate the canonical learning append.

## Supersession and Withdrawal

When a canonical learning is superseded or withdrawn from memory relevance, append the new canonical row, create a `learning-supersession` or `learning-withdrawal` note, reference the previous memory-source note ID when known, and let Phase 2 update compiled memory surgically.

Never edit or delete prior admission notes.
