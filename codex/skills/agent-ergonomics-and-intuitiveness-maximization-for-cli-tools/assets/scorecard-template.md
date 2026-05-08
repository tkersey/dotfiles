# Agent Ergonomics Scorecard

Generated: <ISO8601>
Source: `audit/agent_surfaces.jsonl`
Pass: <N>
Tool: `<TOOL>` @ `<TARGET_SHA>`
Rubric: `<RUBRIC_VERSION>`

---

## Per-surface scores

| surface_id | weighted | intu | ergo | ease | parse | error | intent | safe | det | self | comp | regr |
|------------|----------|------|------|------|-------|-------|--------|------|-----|------|------|------|
| verb__list | 691 | 850 | 700 | 600 | 900 | 650 | 400 | 1000 | 850 | 650 | 800 | 300 |
| flag__list__json | 720 | 750 | 700 | 700 | 900 | 700 | 400 | 1000 | 800 | 700 | 800 | 350 |

(table truncated; see source JSONL for all rows)

---

## Distribution histogram

### Weighted score distribution (per surface)

```
   0- 99 │  (0)
 100-199 │  (0)
 200-299 │  (0)
 300-399 │ ██ (2)
 400-499 │ ████ (4)
 500-599 │ ████████ (8)
 600-699 │ ██████████ (10)
 700-799 │ █████████████ (13)
 800-899 │ ████████ (8)
 900-999 │ ████ (4)
1000     │ ██ (2)
```

### Per-dimension medians

| dim | median | min | max | count_below_700 |
|-----|--------|-----|-----|------------------|
| agent_intuitiveness | 750 | 200 | 1000 | 12 |
| agent_ergonomics | 700 | 100 | 1000 | 18 |
| ... |

---

## Top 10 lowest-scoring surfaces

(sorted by weighted_score ascending; these become Phase 4 recommendation candidates)

1. `<surface_id>`: weighted=<N>; failing dims: <list>
2. ...

---

## Below-Polish-Bar surfaces (weighted < 750)

- `<surface_id>` (weighted: <N>) — failing on <dim list>
- ...

---

## Above-Polish-Bar surfaces (weighted ≥ 750)

count: <N>/<total>

These surfaces meet the bar today. Phase 5 work focuses on the below-bar list.
