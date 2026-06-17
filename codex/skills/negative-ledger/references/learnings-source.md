# Learnings as a Negative-Ledger Source

Use `$learnings` as a historical evidence source for negative evidence. The negative ledger owns the failed-hypothesis semantics and durable route-exclusion state in `.ledger/negative-ledger.jsonl`.

## Read path

When a concrete task is available, run read-only recall during context gathering if the CLI is available:

```bash
run_learnings_tool recall \
  --query "<artifact> <objective> failed attempt regression revert no-effect avoid" \
  --limit 10 \
  --drop-superseded
```

Tighten the query after early file reads if the implementation slice materially narrows.

Use:

```bash
run_learnings_tool recent --limit 15
```

when the user wants to browse recent learnings or when no concrete objective exists yet.

Use query specs when the user wants ranking, grouping, or audits:

```bash
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/status-rank.json"
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/top-tags.json"
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/top-paths.json"
```

Do not block negative-ledger operation if `$learnings` is unavailable. Continue with `ledger query/map`, user notes, git history, review comments, and logs.

## Interpreting learnings hits

Treat a `$learnings` row as negative-ledger evidence only when it has:

- a condition/action learning statement relevant to the current task
- anchored evidence: command outcome, commit SHA, run ID, file path, benchmark, exact error, review rationale, or revert
- an application that changes current routing
- non-superseded status, or a clear reason a superseded row still matters historically

Map statuses as follows:

- `avoid_for_now` -> likely negative evidence; check applicability
- `investigate_more` -> unresolved negative signal; route to evidence gathering
- `review_later` -> weak seed; do not suppress a route yet
- `codify_now` -> candidate durable rule; still check current applicability
- `do_less` -> possible negative evidence; inspect witness
- `do_more` -> may indicate positive adjacent frontier rather than exclusion

## Promotion path

After a witnessed failed attempt, append durable route-exclusion evidence through `ledger capture`:

```bash
ledger capture --json capture.json
```

Use one capture per durable negative-evidence record. Prefer one high-signal record over several chronological notes.

## Suggested tags

- `negative-ledger`
- `failed-attempt`
- `benchmark-regression`
- `no-effect`
- `revert`
- `unsound`
- `too-complex`
- `flaky-test`
- domain tags such as `sqlite`, `mvcc`, `auth`, `parser`, `migration`

## Do not duplicate storage logic

Do not manually edit `.ledger/negative-ledger.jsonl` during normal operation. Use `ledger capture` from a verified repo root. `.learnings.jsonl` may cite lessons, but it is not the operational route-exclusion store.

## Capture proof line

When a capture checkpoint occurs, end the capture note with one proof line from `ledger` or an explicit skip:

```text
ledger-capture: neg_id=NEG-... status=active
ledger-capture: neg_id=NEG-... status=need-evidence
ledger-capture: not-attempted: evidence not durable enough
```
