# Refactor Ledger — <run-id>

> Every accepted collapse gets one row. Never delete a row — if a collapse is
> reverted, append a REVERTED row with the reason so the lesson stays visible.

## Scoreboard

| Metric             | Before | After | Δ |
|--------------------|-------:|------:|--:|
| LOC (`src/`)       |        |       |   |
| Test pass rate     |        |       |   |
| Warnings / errors  |        |       |   |
| Public-API surface |        |       |   |
| Duplicate clusters |        |       |   |

## Collapse rows

| ID  | Type | Sites | Lever | LOC saved | Risk | Tests | Commit  | Verdict |
|-----|------|------:|-------|----------:|:----:|:-----:|---------|---------|
| ISO-001 | II | 3 | extract helper | 42 | L | green | `abc1234` | shipped |
| ISO-002 | IV | 2 | dispatch table | 28 | M | green | `def5678` | shipped |
| ISO-003 | V  | 2 | (rejected, accidental rhyme) | — | — | — | — | rejected |

## REVERTED rows

| ID  | Original commit | Revert commit | Reason |
|-----|-----------------|---------------|--------|
|     |                 |               |        |

## Rejection log

Candidates considered and explicitly rejected — capture the reason so future
scans don't re-propose them.

- **ISO-003** — two functions looked like a type-IV clone but one was for the sync path and one for async with different cancellation semantics. Collapsing would have changed the observable error mode. Accidental rhyme.
- **ISO-007** — score 1.8, below threshold 2.0. Revisit if third site emerges.
