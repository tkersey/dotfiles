# Score Reconciliation Policy

When two scorer subagents (A and B) score the same surface, their per-dim
scores will not exactly match. This document defines the action thresholds
that turn that disagreement into a deterministic next-step.

## Why this matters

Without a written policy: every spread > 0 becomes a judgment call. Some
parent agents spawn tiebreakers for everything (expensive, no signal); some
ignore even severe disagreement (silent calibration drift). The policy below
is the contract that lets the parent agent decide WITHOUT thinking.

## Per-(surface, dim) action thresholds

| spread (max − min per dim) | action | rationale |
|---|---|---|
| 0 – 99   | **accept** | Within rounding noise. Take median (= equal to either). |
| 100 – 199 | **accept** | Mild disagreement. Take median; record disagreement in `score_confidence.spread_max`. |
| 200 – 299 | **accept_warn** | Real disagreement. Take median, but flag in scorecard for review. Keep an eye on rubric anchor for this dim if it recurs. |
| 300 – 499 | **tiebreaker** | Genuine disagreement. Spawn `agent-ergo-scorer-tiebreaker` subagent (per `subagents/scorer-tiebreaker.md`); breaks via independent third look. |
| ≥ 500 | **escalate** | Rubric is mis-anchored — two reasonable scorers should not differ by half the scale. Halt the pass; re-read SCORING-RUBRIC.md anchor for this dim; revise before continuing. |

These thresholds are calibrated to a 1000-point scale with 50-point rounding.
On any other scale, scale proportionally.

## What the tiebreaker sees

The tiebreaker subagent reads:
- The full surface record (same as scorers A and B).
- A's evidence + notes (NOT raw scores).
- B's evidence + notes (NOT raw scores).
- The rubric anchors for the disputed dim only.

The tiebreaker explicitly does NOT see A's or B's raw scores. The point is
to break the tie based on evidence, not to compromise.

The tiebreaker emits a single record at `<sibling>/audit/partial/scores_pass<N>_<SID>_scorertiebreaker.jsonl`.
The aggregator's existing logic (median across all present partials) handles
the merge: with three records, median = middle value.

## Escalation flow

When ANY (surface, dim) pair has spread ≥ 500:

1. The reconciler exits 2.
2. The parent agent stops Phase 2 immediately. No more scorer spawns.
3. The user is presented with: "scorer disagreement on `<dim>` for `<surface_id>` was 500+ pts (A: X, B: Y). The rubric anchor for `<dim>` may be mis-tuned. Open `references/rubric/SCORING-RUBRIC.md` § <dim> and review the 250 / 500 / 750 anchors before resuming."
4. After rubric edit, restart Phase 2 (re-spawn scorers, NOT tiebreaker — tiebreaking a misaligned rubric just papers over the issue).

## Inter-rater reliability budget

The reconciler also reports counts:
- accept_warn count
- tiebreaker count
- escalate count

For a healthy pass:
- escalate count = 0 (any > 0 means the rubric is fundamentally mis-anchored)
- tiebreaker count ≤ 5% of (surfaces × evaluated dims) (otherwise scorers are working too independently)
- accept_warn count ≤ 15% of pairs (otherwise rubric is too loose)

Track these across passes; degradation is the early signal.

## How to invoke

```bash
tools/reconcile-scores.sh <sibling>
# Exit 0: clean
# Exit 1: tiebreakers needed (parent should spawn)
# Exit 2: user escalation (halt pass)
```

The output (in --format json mode) is suitable for piping to a
spawn-tiebreaker loop in the parent agent.
