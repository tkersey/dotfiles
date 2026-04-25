# Refactor Dashboard — <project>

> One page. Dense. Read-only for the team, write-only by the refactor session.
> See [METRICS-DASHBOARD.md](../references/METRICS-DASHBOARD.md) for the rationale.

## Current pass

- **Run ID:** <yyyy-mm-dd-pass-N>
- **Branch:** refactor/<name>
- **Driver:** <agent-id or human>
- **Phase:** baseline / map / score / prove / collapse / verify / ledger

## Quality gates (must stay green)

| Gate                      | Before | Now | Delta | Target |
|---------------------------|-------:|----:|------:|-------:|
| Test pass rate            |        |     |       |  100%  |
| Warning count (ceiling)   |        |     |       |  ≤ ceiling |
| `any` / `unwrap` count    |        |     |       |  ≤ ceiling |
| Golden-output diff (bytes)|        |     |       |    0   |
| LOC (`src/`)              |        |     |       |  ≤ before |
| Public API surface        |        |     |       |  ≤ before |

## Top clones (from duplication_map.md)

| Cluster | Sites | Est. LOC saved | Score | Disposition |
|---------|------:|---------------:|------:|-------------|
|         |       |                |       |             |

## This-pass ledger (latest 10)

| ID | Type | Sites | LOC | Commit | Verdict |
|----|------|------:|----:|--------|---------|
|    |      |       |     |        |         |

## Rejections (latest 5)

| ID | Reason |
|----|--------|
|    |        |

## Next

1. <what the driver is about to do>
2. <what blocks next>
3. <what to raise with the user>
