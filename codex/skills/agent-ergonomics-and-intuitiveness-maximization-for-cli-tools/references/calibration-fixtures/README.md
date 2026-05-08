# Calibration fixtures

Real-world data captured from end-to-end dogfood runs. Each fixture preserves
the scorecard + recommendations from a specific (target, date) pair, with
provenance.

## Fixtures

### `gh-dogfood-2026-05-08.jsonl`

- **Target:** `gh` v2.46.0 (GitHub CLI)
- **Date:** 2026-05-08
- **Pass:** 1 (audit-only, mini-mode)
- **Surfaces scored:** 3 (1 verb + 2 flags)
  - `verb__repo` (the `gh repo` subcommand group)
  - `flag__browse__r` (the `-r` flag of `gh browse` — surfaced a real intuitiveness trap)
  - `flag__ruleset__help` (the `--help` flag of `gh ruleset`)
- **LLM agents spawned:** 6 scorers
- **Cost:** ~$3
- **Mean weighted:** 561 (vs bv's 634)
- **Outstanding:** 2 (surface, dim) pairs in tiebreaker band (300-499 spread); not resolved in this run.
- **Notable real finding:** `gh browse -r` actually means `--releases` (boolean), not `--repo` (which is `-R`). An agent typing `gh browse -r owner/name` gets a cobra `strconv.ParseBool` error rather than redirect to `-R`. Both scorers caught this independently. This is a genuinely novel intuitiveness trap an audit could recommend fixing via a "did-you-mean -R" hint when the value looks like a repo slug.

### `bv-dogfood-2026-05-07.jsonl` + `bv-dogfood-2026-05-07.recommendations.jsonl`

- **Target:** `bv` v0.16.0 (graph-aware triage engine for Beads)
- **Date:** 2026-05-07
- **Pass:** 1 (audit-only)
- **Surfaces scored:** 3
  - `verb__bv` (the bare invocation)
  - `flag__global__related-min-relevance`
  - `flag__global__suggest-bead`
- **LLM agents spawned:** 8 total (6 scorers, 2 tiebreakers, 3 recommenders)
- **Cost:** ~$13 in API spend
- **Tiebreakers triggered:** Yes — both flag surfaces had per-dim spreads ≥ 300
  on multiple dims (agent_ease_of_use, determinism, output_parseability,
  composability, self_documentation). Tiebreakers landed decisive calls (not
  midpoints).
- **Recommendations produced:** 3
  - R-001: Accept int% AND float-fraction for `--related-min-relevance` (priority 0.109)
  - R-002: Levenshtein-1 typo correction for `--suggest-bead` family (priority 0.097)
  - R-003: Levenshtein-1 typo correction for bv unknown flags (priority 0.069)

## Use cases

1. **Calibration corpus for `scripts/rubric-fitness.sh`**: feed
   `bv-dogfood-2026-05-07.jsonl` into the fitness checker to validate that
   future scorer prompts produce comparable scores on the same surfaces.

2. **Regression test for clusterer**: when re-running
   `scripts/cluster-recommendations.sh` against
   `bv-dogfood-2026-05-07.recommendations.jsonl`, the default threshold (3)
   should produce 3 clusters. If a future change collapses them to 2 or
   fewer, the threshold or signature is too lenient.

3. **Replay test**: re-run scorers on the same 3 surfaces with the current
   prompt; compare per-dim scores against the captured values. Per-dim deltas
   > 100 indicate the scorer prompt has drifted.

4. **Methodology validation**: every score > 700 in the captured fixture has
   a matching `evidence.<dim>` entry, including n/a-1000 dims. This is a
   ground-truth example of the post-fix scorer.md discipline.

## Surface evidence quality

Each captured score is accompanied by real evidence from running `bv`:
- `bv --robot-triage` output excerpts demonstrating the structured output
- `bv --robot-schema` output demonstrating per-command JSON Schemas
- typo-correction tests (`bv --hlep`, `--related-min-relevence`, `--sugges-bead`)
- companion-flag error tests
- determinism tests (`data_hash` stable across runs)

This is what production-grade scorer evidence looks like.

## How to add new fixtures

When future audits produce noteworthy data, snapshot:

```bash
DEST=references/calibration-fixtures
DATE=$(date +%Y-%m-%d)
TOOL=<target-tool-name>
cp <sibling>/audit/agent_surfaces.jsonl     "$DEST/${TOOL}-${DATE}.jsonl"
cp <sibling>/audit/recommendations.jsonl    "$DEST/${TOOL}-${DATE}.recommendations.jsonl"
```

Add a section to this README with target, date, surfaces, agents spawned,
spend, and notable findings.

## Why preserve this

The dogfood revealed 7 methodology + algorithm bugs that 8 fresh-eyes review
passes had not found. Without preserved real-world data, future regressions
on the same patterns won't be detectable. Cheap to keep; expensive to recover.
