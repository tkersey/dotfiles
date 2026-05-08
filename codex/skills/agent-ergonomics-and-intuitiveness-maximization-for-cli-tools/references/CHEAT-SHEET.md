# CHEAT-SHEET — Dense single-page agent-ergonomics reference

If you only have time to read ~330 lines of this skill, read this. Everything else is depth.

---

## The One Rule

Design every surface so the FIRST thing an agent instinctively tries "just works." Never silent-fail. Never punish a reasonable misstep. Always provide a safe alternative for any dangerous request. Output is parseable, deterministic, and self-describing.

---

## What gets audited

A target CLI's **agent surfaces**: every verb, flag, env var, exit code, error message, prompt, config key, signal handler. Each gets a deterministic `surface_id` and is scored on 11 dimensions.

---

## The 11 dimensions (0–1000 each)

1. **agent_intuitiveness** — does the first command guess work?
2. **agent_ergonomics** — round-trip count for canonical task
3. **agent_ease_of_use** — discoverable from `--help` alone?
4. **output_parseability** — `--json`, exit-code contract, stdout/stderr split
5. **error_pedagogy** — does the error TEACH? name the safe alternative?
6. **intent_inference** — handles `--jsno` → `did you mean --json?`
7. **safety_with_recovery** — `--dry-run` + `--yes`; safe alts named
8. **determinism_and_reproducibility** — same input → same output bytes
9. **self_documentation** — `capabilities --json`, `robot-docs guide`
10. **composability** — pipes work; honors NO_COLOR / CI / non-TTY
11. **regression_resistance** — golden tests pin contracts

Score > 700 requires evidence (file:line OR invocation transcript).

---

## The Polish Bar (12 non-negotiables)

1. **First-try success**: `<tool>`, `<tool> --help`, `<tool> -h`, `<tool> help` all produce useful output.
2. **JSON everywhere**: every read-side verb has `--json` or `--robot-*`.
3. **Capabilities endpoint**: `<tool> capabilities --json` returns version + contract_version + features + commands + exit_codes + env_vars.
4. **Robot-docs endpoint**: `<tool> robot-docs guide` (or `--robot-help`) returns paste-ready agent handbook < 80 lines.
5. **Mega-command**: ≥ 1 `<tool> --robot-triage`-style call returning multiple slices + copy-paste-ready follow-up commands.
6. **Exit-code contract**: 0=success, ≥1 documented categories. Exit 1 ≠ "no results."
7. **Error pedagogy**: every error names what failed, where, AND the exact corrected command/flag.
8. **Intent inference**: typos / aliases / mis-orderings either succeed-with-warning or produce "did you mean X?" hint.
9. **Dangerous-op gating**: every irreversible op requires `--yes` AND offers `--dry-run`.
10. **Determinism**: same input → same output bytes; honors `SOURCE_DATE_EPOCH`.
11. **NO_COLOR / CI / non-TTY**: honored everywhere.
12. **Regression test**: every applied recommendation has `audit/regression_tests/R-NNN__*.test.{sh,rs,py,ts}`.

---

## The 5 modes

- `audit-only` — score + recommend; no code changes
- `full` — audit + apply + re-score + tests; feature branch in target
- `re-score-only` — quick pulse vs prior pass
- `simulate-only` — fresh-context agent attempts canonical tasks
- `single-surface-rescore` — one named surface

Default: ask the user.

---

## The 10-phase loop

```
1  SURFACE INVENTORY     (parallel by subcommand)
2  RUBRIC-DRIVEN SCORING (≥2 scorers per surface; warn at 200, tiebreak at ≥300, escalate at ≥500)
3  INTENT-INFERENCE STRESS  (naive + savvy corpora)
4  RECOMMENDATION SYNTHESIS  (rank by frequency × score_gap × blast_radius)
5  APPLY CHANGES          (full mode only; bead per rec; reservations)
6  RE-SCORE & UPLIFT      (median ≥ 25 pts; no surface drops > 50 pts)
7  FRESH-EYES BUG REVIEW  (3 calibrated prompts; clean twice)
8  SELF-DOC HARDENING     (capabilities, robot-docs, --robot-* missing)
9  AGENT-IN-THE-LOOP SIM  (fresh-context agent canonical tasks)
10 HANDOFF & ITERATION    (HANDOFF.md, push, beads for next pass)
```

Phases 4, 5, 6, 7 are **reapply-until-quiet**.

---

## The 8 universal recs (default top-N for almost any audit)

- **U-1**: Add `<tool> capabilities --json`
- **U-2**: Add `<tool> robot-docs guide` (or `--robot-help`)
- **U-3**: Add `--robot-*` mode for read-side verbs (or `--json` if more idiomatic)
- **U-4**: Add levenshtein-1 typo correction
- **U-5**: Schema-pin `capabilities --json` regression test
- **U-6**: Add `recommended_action` field to `doctor`/`health` outputs
- **U-7**: Add `meta._provenance` / `--robot-meta` for fallback-mode detection
- **U-8**: Add AGENT/AUTOMATION footer to every subcommand's `--help`

---

## The 33 operators (composable cognitive moves)

```
①  First-Try-Inevitability       Σ  Mega-Command
⟁  Intent-Infer-Then-Act         🛡  Safe-Alternative-Always
📜 Self-Describing                📖 In-Tool-Docs
🚦 Exit-Code-Contract             🪧 Stdout-Data-Stderr-Diag
🧪 Pin-The-Contract-Test          🔀 Macros-vs-Granular
🆔 Stable-Handle                   🩹 Error-Teaches
🚫 Never-Silent-Fail              ⏱  Sub-Second-Hot-Path
🌐 Honors-Env-Conventions         🔢 Deterministic-Output
🧭 Discoverable-From-Help         🪄 Recommended-Action
🪟 Provenance-Field               📐 Schema-Pin
🩻 Doctor-Mode                    🔇 Telemetry-Disable
🎯 Discovery-Footer               🪜 Two-Phase-Latency
🔗 Cross-Verb-Reference           🛂 Identity-Friction-Collapse
📦 Stable-Envelope                🔬 Single-Step-Atomicity
🧷 Idempotency-Pin                🧶 Composable-Verbs
🧮 Bulk-Friendly                  🧾 Drift-Guard
🎓 Onboarding-Curve
```

For any failing dim, OPERATORS.md § Composition gives the operator pipeline.

---

## The Universal Envelope

Every `--json` output:

```jsonc
{
  "ok":           true,
  "tool_version": "0.4.1",
  "data":         { /* verb-specific */ },
  "meta":         { "request_id": "...", "ts_iso": "...", "data_hash": "...", "contract_version": "1" },
  "warnings":     [],
  "commands":     []   // copy-paste-ready follow-ups
}
```

---

## The 5-key capabilities schema (minimum)

```jsonc
{
  "version":          "0.4.1",
  "contract_version": "1",
  "features":         ["json_output", ...],
  "commands":         { "<verb>": {...} },
  "exit_codes":       { "0": "success", "1": "user-input-error", ... },
  "env_vars":         { "<NAME>": {...} }
}
```

---

## The 4 mega-command shapes (pick one if applicable)

1. **TRIAGE** (`bv --robot-triage`) — recommendations + commands + project_health
2. **DIAGNOSE** (`cass doctor`) — components + recommended_action + fallbacks_active
3. **PLAN** (`bv --robot-plan`) — parallelizable tracks + commands
4. **CAPABILITIES** — always.

---

## The 5-stage deprecation

```
0. introduce: new + old both work
1. warn:      old emits deprecation warning
2. error:     old fails with migration recipe
3. remove:    old gone from source
```

Span ≥ 2 passes. NEVER skip stages on a public CLI.

---

## The 5 intent-corpus outcomes

- 🚫 `silent_fail`        — exit 0 + nothing said       (worst)
- 😤 `useless_error`      — exit ≠ 0 + generic msg     (bad)
- 🤝 `useful_hint`        — exit ≠ 0 + names right form (acceptable)
- 🎯 `inferred_and_acted` — succeeded + warned         (best)
- ⏭ `skipped`            — runner intentionally did not execute unsafe or invalid corpus entry

---

## The 15 CLI archetypes

search-tool / package-manager / build-tool / test-runner / SCM / daemon / converter / scaffolder / hook / issue-tracker / auth / migration / diagnostic / mcp-server / multi-binary

Per-archetype dimension weights + canonical mega-command shape: see `methodology/CLI-ARCHETYPES.md`.

---

## The 5 agent profiles

frontier (Claude Code, Codex, Gemini) / mid-tier (aider, cursor, opencode) / specialized (clawdbot, brennerbot) / smaller (Haiku, Flash) / IDE-integrated (Copilot inline)

Per-profile dimension-weight overrides: `methodology/AGENT-PROFILES.md`.

---

## The 12 hard rules from AGENTS.md

1. NEVER delete a file without explicit user permission
2. NEVER `git reset --hard` / `git clean -fd` / `rm -rf` without explicit auth
3. NEVER run a script that processes/changes code files (manual edits only)
4. NEVER create `_v2` / `_improved` files (revise in place)
5. NO backwards-compat shims unless rec explicitly requires deprecation path
6. NEVER skip pre-commit hooks (`--no-verify`)
7. NEVER `--amend` a commit that was rejected (create new commit)
8. Trust other agents' uncommitted changes (don't stash/revert)
9. Always work on feature branch, not main
10. Push before ending session (work isn't done until pushed)
11. Use `br` for issue tracking (non-invasive, never runs git)
12. Default to writing NO comments unless WHY is non-obvious

---

## The audit workspace layout

```
<target>__agent_ergonomics_audit/
├── audit/
│   ├── manifest.json            ← entry point
│   ├── surface_inventory.jsonl
│   ├── agent_surfaces.jsonl     ← scored
│   ├── intent_inference_corpus.jsonl
│   ├── recommendations.jsonl    ← ranked
│   ├── playbook.md              ← top-10 narrative
│   ├── applied_changes.jsonl
│   ├── scorecard*.md, heatmap.svg, uplift_diff.md
│   ├── regression_tests/        ← R-NNN__*.test.{sh,rs,py,ts}
│   ├── agent_simulations/{pre,post}_pass_<N>/
│   └── HANDOFF.md
├── tools/
└── .gitignore
```

The actual code changes happen on `agent-ergonomics-pass-N` branch in the **target** repo, not the sibling.

---

## The priority formula

```
priority = frequency × score_gap × blast_radius

frequency:    how often agents hit this surface (CASS-mined)
score_gap:    (1000 - weighted_score) / 1000
blast_radius: 0.10 (cosmetic) | 0.50 (workflow) | 1.00 (blocker)
```

Top-10 recs are the playbook for Phase 5.

---

## The 4 termination conditions (Phase 5/6 loop)

- Median absolute uplift in last pass < 25 pts
- No surface regressed > 50 pts (any regression > 50 = HARD STOP)
- Phase 4 produced no new top-10 rec
- Phase 7 fresh-eyes ran clean twice in a row

---

## The skill itself (jump-table)

| Need | Pointer |
|------|---------|
| Phase playbook | methodology/PHASES.md |
| Verbatim subagent prompts | methodology/AGENT-PROMPTS.md |
| 33 operators + composition | methodology/OPERATORS.md |
| Polish-Bar verification queries | methodology/POLISH-BAR.md |
| Per-language framework recipes | methodology/LANGUAGE-RECIPES.md |
| Mega-command design library | methodology/MEGA-COMMAND-DESIGN.md |
| Error-rewriting cookbook | methodology/ERROR-REWRITING-COOKBOOK.md |
| JSON schema patterns | methodology/JSON-SCHEMA-PATTERNS.md |
| Per-archetype defaults | methodology/CLI-ARCHETYPES.md |
| Per-agent-profile calibration | methodology/AGENT-PROFILES.md |
| MCP server audit extension | methodology/MCP-SERVER-AUDIT.md |
| Multi-tool family audit | methodology/MULTI-TOOL-FAMILY-AUDIT.md |
| Self-application meta-doc | methodology/SELF-APPLICATION.md |
| Track A artifact mapping | methodology/OPERATIONALIZING-EXPERTISE-TRACK-A.md |
| 15 worked-example audits | exemplars/WORKED-EXAMPLES.md |
| 25 canonical exemplars (patterns) | exemplars/CANONICAL-EXEMPLARS.md |
| 20 counter-examples (anti-patterns) | exemplars/COUNTER-EXAMPLES.md |
| Quote bank ([Q-NNN]) | exemplars/QUOTE-BANK.md |
| Per-archetype canonical tasks | exemplars/CANONICAL-TASK-LIBRARY.md |

---

## When you're starting

1. `scripts/preflight.sh <target>` → verify local tools and target readability
2. `scripts/scaffold-workspace.sh <sibling> <target>` → create `audit/` before redirects
3. `scripts/discover-cli.sh <target> > <sibling>/audit/phase0_cli.json` → archetype hint
4. `scripts/check-skills.sh <sibling>/audit` → helper-skill inventory
5. Pick and record mode
6. Spawn surface-inventorist subagents (Phase 1)
7. Spawn ≥ 2 scorer subagents per surface (Phase 2)
8. Generate intent corpus + run it (Phase 3)
9. Synthesize recommendations (Phase 4)
10. (full mode) Apply via applier subagents (Phase 5)
11. Re-score; verify uplift; check regressions (Phase 6)
10. Fresh-eyes review until clean twice (Phase 7)
11. Self-doc hardening — add capabilities, robot-docs (Phase 8)
12. Spawn fresh-context simulator (Phase 9)
13. Write HANDOFF.md; push (Phase 10)

---

## The 8 hard signs of an agent-hostile CLI

1. Bare invocation launches TUI in non-TTY context
2. `--help` is > 200 lines with no TOC and no AGENT/AUTOMATION footer
3. No `--json` for read-side verbs
4. No `capabilities --json`
5. Errors are prose-only without `did you mean` hints
6. Destructive ops run on first invocation without `--yes`
7. Output ordering is non-deterministic (hashmap iteration)
8. ANSI codes leak into piped stdout

These are the audit's bread-and-butter findings.

---

## The skill's own contract version

```
schema_version: 1.0.0
rubric_version: <git SHA at audit start>
```

Bumped when dimensions / anchors / weights change semantically.
