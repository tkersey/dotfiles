# Benchmarks — what a good refactor pass looks like

> Numbers for calibration. "Is this pass going well?" becomes answerable
> by comparing to these ranges. Numbers drawn from typical medium-sized
> projects (~50k-200k LOC); scale intuitively.

## Contents

1. [Per-pass metrics](#per-pass-metrics)
2. [Per-candidate metrics](#per-candidate-metrics)
3. [Cumulative (multi-pass) trends](#cumulative-multi-pass-trends)
4. [Red-flag values](#red-flag-values)
5. [How to use these numbers](#how-to-use-these-numbers)

---

## Per-pass metrics

| Metric                       | Low     | Typical  | High    | Notes |
|------------------------------|--------:|---------:|--------:|-------|
| Candidates mapped            |   15    |   40-80  |  200+   | Larger = older or more AI-drift |
| Candidates accepted          |    3    |   8-15   |   25    | Cap at ~20 per pass |
| Ship/reject ratio            | 30/70   |  60/40   | 80/20   | Near 100% accept = too lax |
| Revert rate                  |   0%    |  5-10%   |  > 15%  | One revert per pass is normal |
| LOC delta (`src/`)           |  -0.5%  | -3 to -15%| -25%   | -0% means the pass did nothing |
| Public API surface delta     |    0    |    0     |   ±1-2  | Growth flags API leak |
| Warning ceiling delta        |    0    | -5 to -30| -100+   | Only goes down |
| `any`/`unwrap` delta         |    0    |  -3 to  -20| -50+   | Only goes down |
| Duplicate clusters remaining |  -10%   |  -30%    |   -60%  | After this pass vs before |
| Total wall time              |  1h     |  2-4h    |   8h    | > 8h = split |
| Per-candidate median time    | 5 min   | 15-30 min| 60 min  | > 60min = too big |

## Per-candidate metrics

| Metric                       | Typical  | Notes |
|------------------------------|---------:|-------|
| Sites collapsed              |   2-5    | > 8 sites = split into sub-candidates |
| LOC saved                    |  15-80   | < 10 probably not worth the card |
| Confidence factor            | 0.7-0.9  | < 0.6 flags risk; consider rejecting |
| Risk factor                  |  1-5     | > 7 escalate |
| Score                        |  2.5-8   | < 2.0 reject; > 10 suspicious (too good) |
| Card fill time               | 10-15 min| > 20 reconsider candidate size |
| Edit time                    |  5-15 min| |
| Verify time                  |  2-5 min | faster with `rch` offload |
| Sites read (pre-edit)        | 100% of listed | less = card can't be audited |

## Cumulative (multi-pass) trends

After N consecutive passes on the same project, you should see:

```
Pass →      1       2       3       5       10
LOC(%)   -5%    -8%    -10%   -14%   -20%
         (baseline decaying; diminishing returns expected)

Warnings  -10    -30    -60    -100   -250
         (these decay faster because the scanner catches new patterns)

any/unwrap  -5    -15    -30    -50    -80
           (these have hard floors — code needs SOME)

Duplicate clusters
           80%    60%   45%   25%   10%
          of original total (asymptotic)

Ship/reject
           50/50  55/45  60/40  70/30  75/25
          (rejections become more accurate)

Time per candidate (median min)
            25     20     18    15     12
          (muscle memory improves)
```

If your project diverges materially from these trends, investigate.

## Red-flag values

Stop and reconsider if any of these hit:

| Metric                     | Red-flag value | Likely cause |
|----------------------------|---------------:|--------------|
| Accept rate               |  100%          | Scorer is rubber-stamping; threshold too loose |
| Accept rate               |    0%          | Risk-averse; scanner picking bad candidates; OR project is truly clean |
| Revert rate per pass       |  > 20%         | Card discipline is slipping |
| LOC delta                  |  ≥ 0           | Pass added lines; probably a bug-fix mislabeled as refactor |
| Warning ceiling            |   grew         | Means someone bypassed the gate — investigate which commit |
| Wall time                  |  > 2× typical  | Scope creep; candidates are too big |
| `any` count                |   grew         | Type-safety regression introduced |
| Ship/reject ratio after 5 passes | > 90/10 | You're not finding rhymes; scanner needs upgrade OR team is lax |
| Rejection log entries      |  0             | Nothing examined; pass was rubber-stamp |
| `CLOSEOUT.md` "surprises" field | blank     | No learning captured |

## How to use these numbers

**For a pass driver:** read the per-pass row before closing the pass.
Does your pass fall in the "typical" band? If in the "low" or "high"
band, note why in the closeout (e.g., "high LOC delta — a dead-code
gauntlet cleared 500 lines of orphans"). If outside the red-flag limit,
pause before closeout.

**For a team lead:** track the cumulative trend across passes. If LOC
isn't decreasing cumulatively, either the scanner is underreporting or
new duplication is being created as fast as it's removed — shift to L2
or L3 in [TEAM-ADOPTION.md](TEAM-ADOPTION.md).

**For a new adopter:** don't expect typical numbers on pass 1. The first
pass is a learning pass; aim for "low" numbers and build confidence. By
pass 3 you should be in "typical."

**For a reviewer:** if a candidate claims > 200 LOC saved, it's probably
too big — ask for split. If a candidate claims score > 10 on a small site
count, check the Confidence — often it's optimistically 1.0 when it
should be 0.7.

## Where the numbers come from

These ranges are synthesized from:
- Case studies in [CASE-STUDIES.md](CASE-STUDIES.md).
- Real session evidence in [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md).
- Expected behavior of the scanners with conservative defaults.

They are heuristics, not hard limits. If your project has a principled
reason to diverge (e.g., tiny LOC deltas because the project is already
well-maintained; large LOC deltas because you're rescuing a vibe-coded
project), document it and move on.

See [METRICS-DASHBOARD.md](METRICS-DASHBOARD.md) for the dashboard view
and [EXIT-CRITERIA.md](EXIT-CRITERIA.md) for time-box guidance.
