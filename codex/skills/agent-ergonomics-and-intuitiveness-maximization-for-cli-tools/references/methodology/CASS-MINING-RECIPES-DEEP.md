# CASS-MINING-RECIPES-DEEP — 38+ Targeted Queries

The full "deep" appetite query bank, organized by failure class. Use during Phase 0 when CASS appetite is `deep` (see `ORCHESTRATION.md § CASS mining schedule`).

The 10 canned queries from the `quick` appetite are a subset; this file extends them with class-specific probes.

Each query produces hits that the `subagents/cass-miner.md` agent digests into `audit/cass_findings.md`. The patterns observed feed Phase 4 priority weighting (the `frequency` factor of `priority = frequency × score_gap × blast_radius`).

---

## Class A — agent_intuitiveness probes (first-try success)

**Goal.** Find sessions where the agent guessed wrong on first try.

```bash
cass search "<TOOL> command not found" --robot --limit 30
cass search "<TOOL> doesn't have" --robot --limit 30
cass search "<TOOL> --help shows" --robot --limit 30
cass search "<TOOL> tried but" --robot --limit 30
cass search "<TOOL> didn't expect" --robot --limit 30
```

What you're looking for: the user's prior agents reaching for a verb / flag that didn't exist. Each hit is signal that the canonical name diverges from agent expectation.

---

## Class B — agent_ergonomics probes (round-trip count)

**Goal.** Find sessions where the canonical task took many round-trips.

```bash
cass search "<TOOL> let me try" --robot --limit 30
cass search "<TOOL> chain of commands" --robot --limit 30
cass search "<TOOL> too many calls" --robot --limit 30
cass search "<TOOL> would be nice if" --robot --limit 30
cass search "<TOOL> wish there was" --robot --limit 30
```

These hits surface candidates for new mega-commands.

---

## Class C — output_parseability probes

**Goal.** Find sessions where the user / agent struggled to parse output.

```bash
cass search "<TOOL> jq" --robot --limit 30
cass search "<TOOL> grep" --robot --limit 30
cass search "<TOOL> awk" --robot --limit 30
cass search "<TOOL> can't parse" --robot --limit 30
cass search "<TOOL> output is messy" --robot --limit 30
```

Hits where the user resorted to `jq | grep | awk` chains indicate the JSON schema is awkward OR the agent didn't know about `--robot-meta`.

---

## Class D — error_pedagogy probes

**Goal.** Find sessions where errors didn't teach.

```bash
cass search "<TOOL> error message" --robot --limit 30
cass search "<TOOL> unhelpful error" --robot --limit 30
cass search "<TOOL> what does this mean" --robot --limit 30
cass search "<TOOL> tried with" --robot --limit 30
```

Hits often capture quotes like "the error didn't say what to do" — direct evidence for Phase 4 error-rewriting recs.

---

## Class E — intent_inference probes

**Goal.** Find sessions where typo / alias / mis-ordering was the issue.

```bash
cass search "<TOOL> typo" --robot --limit 30
cass search "<TOOL> meant to type" --robot --limit 30
cass search "<TOOL> oops" --robot --limit 30
cass search "<TOOL> --jsno OR --colur OR --vebose" --robot --limit 20
```

Direct signal for Phase 4 typo-correction recs.

---

## Class F — safety_with_recovery probes

**Goal.** Find sessions where a destructive op went wrong.

```bash
cass search "<TOOL> deleted accidentally" --robot --limit 30
cass search "<TOOL> reset --hard <TOOL>" --robot --limit 30
cass search "<TOOL> lost work" --robot --limit 30
cass search "<TOOL> --force" --robot --limit 30
cass search "<TOOL> --yes" --robot --limit 30
```

Hits where users discovered the safety gap. High-priority recs for Phase 4.

---

## Class G — composability probes

**Goal.** Find sessions where pipelines broke.

```bash
cass search "<TOOL> NO_COLOR" --robot --limit 30
cass search "<TOOL> piped output" --robot --limit 30
cass search "<TOOL> in CI" --robot --limit 30
cass search "<TOOL> non-interactive" --robot --limit 30
cass search "<TOOL> stdin" --robot --limit 30
```

Hits indicate composability gaps (ANSI in pipes, prompts in CI, etc.).

---

## Class H — determinism probes

**Goal.** Find sessions where output differed across runs.

```bash
cass search "<TOOL> ordering changed" --robot --limit 30
cass search "<TOOL> different output" --robot --limit 30
cass search "<TOOL> flaky" --robot --limit 30
cass search "<TOOL> reproducible" --robot --limit 30
```

---

## Class I — self_documentation probes

**Goal.** Find sessions where docs failed.

```bash
cass search "<TOOL> --help unclear" --robot --limit 30
cass search "<TOOL> README" --robot --limit 30
cass search "<TOOL> capabilities" --robot --limit 30
cass search "<TOOL> robot-docs" --robot --limit 30
```

If users had to leave the tool to find docs, that's a finding.

---

## Class J — cross-tool comparison probes

**Goal.** Find sessions where the user compared this tool to a sibling tool.

```bash
cass search "<TOOL> vs <SIBLING>" --robot --limit 30
cass search "<TOOL> like <SIBLING>" --robot --limit 30
cass search "<TOOL> better than" --robot --limit 30
cass search "<TOOL> worse than" --robot --limit 30
```

Cross-tool hits inform CLI-archetype assignment AND surface verb-naming alignment opportunities.

---

## Tool-family-specific probe templates

If the tool is in a known family, add these targeted probes:

### Search tool family

```bash
cass search "<TOOL> rg OR ripgrep OR ag OR fd" --robot --limit 30
cass search "<TOOL> regex" --robot --limit 30
cass search "<TOOL> case insensitive" --robot --limit 30
```

### Package manager family

```bash
cass search "<TOOL> install failed" --robot --limit 30
cass search "<TOOL> lockfile" --robot --limit 30
cass search "<TOOL> dependency resolution" --robot --limit 30
```

### Build tool family

```bash
cass search "<TOOL> rebuild" --robot --limit 30
cass search "<TOOL> incremental" --robot --limit 30
cass search "<TOOL> cache" --robot --limit 30
```

### SCM tool family

```bash
cass search "<TOOL> push --force" --robot --limit 30
cass search "<TOOL> rebase" --robot --limit 30
cass search "<TOOL> cherry-pick" --robot --limit 30
```

---

## Per-failure-class digest in `cass_findings.md`

Group hits by class:

```markdown
## Class A: agent_intuitiveness

### F-001: User's agents repeatedly typed `<TOOL> ls` expecting `list`
**Sessions touched.** 7 sessions across 3 repos.
**Evidence.** ...
**Recommendation.** Add `ls` alias OR a "did you mean 'list'?" hint.

### F-002: ...

## Class B: agent_ergonomics

### F-008: Canonical task takes 5+ round-trips
**Sessions touched.** 12.
**Evidence.** ...
**Recommendation.** Add `--robot-triage` mega-command (Shape 1).
```

This becomes input to Phase 4's recommender pool.

---

## Frequency signal extraction

For each finding, count the number of sessions across distinct workspaces:

```bash
cass search "<query>" --robot --limit 200 \
  | jq -r '.hits[].workspace' | sort -u | wc -l
```

Higher distinct workspace count → higher `frequency` factor in priority computation:

| Distinct workspaces | frequency factor |
|---------------------|------------------|
| 0 | 0.05 |
| 1 | 0.20 |
| 2-3 | 0.50 |
| 4-7 | 0.75 |
| 8+ | 1.00 |

The frequency factor multiplies into `priority` per `PRIORITY-FORMULA.md`.

---

## When CASS yields little signal

For tools the user hasn't used much (fresh CASS index, < 30 sessions touching the tool):

- Drop appetite to `quick`
- Default `frequency = 0.5` for canonical-task surfaces and `0.3` for everything else
- Document in HANDOFF.md: "CASS findings sparse; frequency estimates default-weighted"

For tools the user uses heavily, `deep` mining yields rich Phase 4 prioritization.

---

## Privacy / sensitivity discipline

Per `subagents/cass-miner.md`:

- Never expose raw session content beyond the snippet field.
- Sessions may contain sensitive context (API keys, customer names, internal infrastructure).
- The CASS-mining digest in `audit/cass_findings.md` should reference findings by `F-NNN` ID and one-line context, not full transcripts.
- If a finding requires full transcript context, link to the session path; don't paste content.

---

## Per-tool deep-mining recipe template

For a tool named `<TOOL>` in archetype `<ARCH>`, generate the deep query set:

```bash
#!/usr/bin/env bash
# generate-deep-cass-queries.sh <TOOL> <ARCH>
TOOL="$1"
ARCH="$2"

# Class A-J generic queries
queries=(
  "$TOOL command not found" "$TOOL doesn't have" "$TOOL --help shows"
  "$TOOL let me try" "$TOOL chain of commands"
  "$TOOL jq" "$TOOL grep" "$TOOL can't parse"
  "$TOOL error message" "$TOOL what does this mean"
  "$TOOL typo" "$TOOL meant to type"
  "$TOOL deleted accidentally" "$TOOL --force" "$TOOL --yes"
  "$TOOL NO_COLOR" "$TOOL piped output" "$TOOL non-interactive"
  "$TOOL ordering changed" "$TOOL flaky"
  "$TOOL --help unclear" "$TOOL capabilities"
)

# Archetype-specific
case "$ARCH" in
  search-tool)       queries+=("$TOOL rg" "$TOOL regex" "$TOOL case insensitive") ;;
  package-manager)   queries+=("$TOOL install failed" "$TOOL lockfile") ;;
  build-tool)        queries+=("$TOOL rebuild" "$TOOL incremental" "$TOOL cache") ;;
  scm-tool)          queries+=("$TOOL push --force" "$TOOL rebase") ;;
  test-runner)       queries+=("$TOOL flaky" "$TOOL re-run failed") ;;
  hook-tool)         queries+=("$TOOL blocked" "$TOOL allowlist") ;;
  daemon)            queries+=("$TOOL connection refused" "$TOOL daemon down") ;;
  scaffolder)        queries+=("$TOOL template" "$TOOL overwrite") ;;
  issue-tracker)     queries+=("$TOOL ready" "$TOOL blocked" "$TOOL graph") ;;
esac

for q in "${queries[@]}"; do
  echo "cass search \"$q\" --robot --limit 30 --robot-format compact --fields minimal"
done
```

Run the generator, redirect to `audit/cass_queries_<TOOL>.sh`, then `bash` it (with `cass` available) to populate the findings.

---

## Surfacing high-yield findings into recommendations

Each finding with `distinct_workspaces >= 4` (frequency factor ≥ 0.75) AND a clear remediation path should produce a recommendation:

```jsonc
{
  "recommendation_id": "R-NNN",
  "title": "Add alias 'ls' for 'list' (CASS finding F-001)",
  "summary": "Across 7 sessions in 3 workspaces, user's agents typed 'ls' expecting POSIX-style list.",
  "diff_sketch": "...",
  "cites_cass_finding": "F-001",
  "frequency": 0.75,
  "priority": ...
}
```

Cross-referencing CASS findings into recommendations gives Phase 4 prioritization a real-world ground truth.
