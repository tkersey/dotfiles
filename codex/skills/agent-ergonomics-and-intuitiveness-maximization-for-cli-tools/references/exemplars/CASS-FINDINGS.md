# CASS-FINDINGS — Patterns mined from prior agent sessions

Surprising patterns observed in the user's prior agent-coding sessions, captured via `cass` mining. These supplement the canonical exemplars + counter-examples by anchoring the rubric to *real* agent failures rather than synthetic ones.

This file is updated each pass via `subagents/cass-miner.md`. Entries here are stable across passes (don't rewrite — append).

---

## Methodology

The 10 canned queries (see `ORCHESTRATION.md § CASS mining schedule`):

1. `"<tool>" --robot` (does the user already use this tool's robot mode?)
2. `"<tool>" error` (what errors did the user hit?)
3. `"<tool>" --help` (did the user reach for --help; how did it go?)
4. `"<tool>" exit code` (any stuck-on-exit-code experiences?)
5. `"<tool>" intent inference` (did the user manually correct the agent's command?)
6. `"<tool>" did not work` (failure-pattern phrases)
7. `"<tool>" silent` (silent_fail patterns)
8. `"<tool>" json output` (parseability complaints)
9. `"<tool>" couldn't figure out` (discoverability gaps)
10. `"<tool>" took too long` (perf complaints in the hot path)

Run with: `cass search "<query>" --robot --limit 20 --robot-format compact`. Output appended to `audit/cass_findings.jsonl` and digested into this file.

---

## Findings — General agent-ergonomic patterns

### F-001: Robot mode is THE pattern (not a feature)

> "Now let me look at how robot-mode output works and examine the output package..."
> "Use bv with the robot flags to find the most impactful bead to work on next"
> "Run bv in robot-triage mode"

Across multiple unrelated repositories (ntm, beads_viewer, repo_updater, wezterm_automata), the user's agents reach for `--robot-*` flags as the FIRST move when integrating a tool into an automated workflow. The pattern is so consistent it's effectively a north star:

> **If your tool doesn't have a robot mode, an agent's first instinct will be to ask for one OR to abandon the tool.**

This validates the rubric's emphasis on `output_parseability` and `self_documentation` (capabilities/robot-docs).

### F-002: "I want one mega-call, not three round-trips"

Repeated theme across sessions:

> "Use bv --robot-triage as your single entry point — it returns recommendations + quick_wins + blockers + project_health + commands in one call"

When the user has had to paint a tool's agent mode themselves, they always converge on a mega-command pattern. This validates `agent_ergonomics` Card Σ (Mega-Command) as the highest-leverage move.

### F-003: Agents probe for `capabilities` and `robot-docs` early

When meeting a new tool, agents in the user's sessions typically run:

```
<tool> --version
<tool> --help
<tool> capabilities --json    # if the agent has seen this in another tool
<tool> robot-docs guide       # likewise
```

If `capabilities --json` and `robot-docs guide` exist, the agent quickly internalizes the tool. If they don't, the agent thrashes through `--help` and source code. The presence of these endpoints is the single biggest predictor of "agent figured it out fast."

### F-004: Silent-fail is the worst experience

> "[the tool] just exited 0 with no output — I assumed it worked..."
> "ran the command, nothing happened, no error — wasted an hour"

The user's agents consistently lose the most time on silent_fail outcomes. Anything that looks like "the tool ran but did nothing visible" is a P0 finding. This justifies the rubric's hard line: every "did nothing" outcome must produce a stderr line.

### F-005: Error messages that don't name the alternative are a major friction point

The user's prior sessions show repeated patterns of:

```
<tool> X
error: invalid argument
[agent runs --help]
[agent reads --help]
[agent guesses again]
[agent re-runs]
```

When the error message names the right command directly ("did you mean `--json`?"), the loop short-circuits to one round-trip. dcg's "use `git stash`; use `git revert`" pattern is the gold standard.

### F-006: Stable handles matter across migration / re-runs

The user has repeatedly hit issues where:
- A tool's session ID is regenerated on every invocation, breaking re-runs.
- A project name differs from the project path, causing the agent to "lose" projects on `cd`.
- An ID is local to a process, not persisted.

`am`'s `project_key` (absolute path) and `bv`'s `data_hash` solve these. The rubric's `determinism` dimension is high-stakes for any tool where state persists across invocations.

### F-007: TUI gates are essential

The user has explicitly stated: bare `bv` and bare `cass` should NOT launch a TUI for an agent. These tools enforce `--robot-*` / `--robot` for non-TTY use.

When a tool *does* trap an agent in a TUI, it's a P0 finding. Agents in the user's session lose entire turns to this. The recommendation: detect non-TTY and emit a one-line guide to the agent surface.

### F-008: Verb naming follows POSIX-y pattern, not Unix shorthand

The user's tools consistently use:
- `list` (not `ls`)
- `delete` (not `rm`)
- `move` (not `mv`)
- `create` / `new` (not `mk`)

But every tool ALSO accepts the shorthand as an alias with no warning. This is the right balance: canonical name in `--help`, shorthand works for muscle-memory.

### F-009: Exit codes are sometimes weaponized

Some of the user's tools use exit codes to communicate richer signals than just "did it work":

- `dcg`: 0=allowed, 1=blocked-with-explanation, 2=blocked-without-explanation (Codex-compatible)
- `ubs`: 0=safe, ≥1=fix
- `cass`: 0=success, lock-busy, repair-failure (per `exit_code_kind`)

Agents check exit codes first; the rich content is on stdout/stderr. This is the canonical exit-code-contract pattern.

### F-010: Provenance fields prevent silent fallback bugs

`cass`'s `--robot-meta` includes `requested_search_mode`, `search_mode`, `semantic_refinement`, `fallback_tier`, `fallback_reason`. When semantic search isn't available, the tool uses lexical and reports it.

Agents in the user's sessions have had silent-fallback bugs in tools without this pattern: the tool fell back to a degraded mode without telling the agent, and the agent trusted partial results. The provenance pattern fixes this.

---

## Findings — Specific tools

### F-101: `bv` and the `--robot-triage` mega-command became the user's reference

The user has cited `bv --robot-triage` as the canonical example multiple times when designing agent surfaces for other tools:

> "give it the bv treatment — one mega-call returning everything an agent needs"

This validates Pattern 7 (mega-command) as the rubric's anchor for agent_ergonomics.

### F-102: `am`'s macro vs. granular split is the ergonomic-axis exemplar

Across sessions, the user has converged on the macro-then-granular pattern for any agent-facing API:

> "macro_start_session collapses identity friction"
> "granular tools are still there for control"

This validates Pattern 11 (macros vs granular) as the rubric's anchor for both agent_ergonomics and self_documentation.

### F-103: `dcg`'s "name the safe alternative" is the error-pedagogy gold standard

The user explicitly designs error messages to mimic `dcg`:

> "the error must say what to use instead, not just 'this is blocked'"

This validates Pattern 2 (error-pedagogy anchor) at score 1000.

### F-104: `cass capabilities --json` is the introspection pattern users propagate

The user has explicitly added `capabilities --json` to multiple internal tools after using `cass`'s. The pattern travels.

This validates Pattern 21 as the canonical introspection anchor.

---

## Findings — Anti-patterns the user has named

### F-201: "Don't make me read the source to know what flags exist"

Tools without `capabilities --json` or `<tool> commands --json` force agents to read source. The user marks this as P0 always.

### F-202: "If you have a TUI, --help should explicitly tell me how to NOT launch it"

`bv` and `cass`'s `--help` both warn: "do not run bare; use --robot-*." The user has cited this as table-stakes for any TUI-having tool.

### F-203: "An agent should never have to grep through stderr to find a flag suggestion"

Stderr is for diagnostics. If the tool wants to suggest a flag, it goes in the *primary* error message, prominently. Not buried.

### F-204: "Provenance fields are not optional for opportunistic enrichment"

If your tool has any "best-effort" mode (semantic search, optional caching, async metric computation), agents need to know which mode actually ran. `--robot-meta` is the pattern; missing it is a finding.

### F-205: "Don't invent your own JSON shape per verb"

Pick a single canonical envelope (`{"ok": true, "data": ..., "meta": {...}}` or similar) and use it everywhere. Per-verb shapes are a documentation tax.

---

## Findings — Methodology refinements suggested

### MR-001: The rubric should weight `intent_inference` heavily for swarm-tier tools

In the user's swarm runs, agents misspell flags constantly. Tools that don't typo-correct cost cumulative time × N agents. The user has explicitly weighted intent_inference 1.5x for swarm-tier work.

### MR-002: Phase 9 simulation should use a *different* model than Phase 5 applied

The user has noted that simulating with the same model that applied the changes can hide blind spots. Best practice: Phase 5 = Claude Opus; Phase 9 = Claude Sonnet (or vice versa) — multi-perspective.

### MR-003: Long-tail recommendations should not be deferred forever

Recs that score below median priority but are easy fixes (one-line --help additions, missing `-h` aliases) should be batched and applied as "Phase 5 cleanup" — not deferred to next pass. The user has noted that pass-by-pass deferrals accumulate into a permanent technical-debt pile.

---

## How to extend this file

When `subagents/cass-miner.md` runs, it appends new findings to this file with `F-NNN` IDs. Don't rewrite existing entries — they're calibration data. If a pattern is contradicted by new sessions, add a counter-finding with `F-NNN-counter` and explain why.

Findings that consistently recur across multiple sessions (≥ 3 distinct repos) get promoted to canonical-exemplar status (move to `CANONICAL-EXEMPLARS.md`). Findings that are one-off curiosities stay here as anecdotes.

The rubric refinement section (`MR-NNN`) feeds back into `SCORING-RUBRIC.md` revisions between passes.
