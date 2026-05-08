# IO-CONTRACTS — JSONL artifact schemas

Every JSONL artifact this skill produces has a stable schema. Re-runs across passes produce records that are comparable byte-for-byte (modulo `applied`/`scores` updates and known volatile fields). This file is the source of truth.

A schema validator script is at `tools/validate_scorecard.sh` (covers `agent_surfaces.jsonl`). All schemas can also be checked manually with `jq`.

## Path convention

Two distinct path styles appear throughout this skill, and conflating them is a common bug:

- **Filesystem-action paths** (in subagent prompts, scripts, instructions like *"write to X"* or *"read from X"*): use the absolute placeholder form `<SIBLING>/audit/foo`. A subagent reading the prompt cold gets an unambiguous path regardless of cwd.
- **Stored field values** (path fields *inside* JSONL records like `manifest.json`'s `artifacts.*`, `applied_changes.jsonl`'s `test_path`, etc.): use the relative form `audit/foo`. Records remain portable across machines and re-runs without rewriting absolute paths.

When in doubt: if you're telling an agent to read or write a file, use `<SIBLING>/audit/foo`. If you're storing a path inside a JSON record that someone else will read later, use `audit/foo`.

---

## `audit/manifest.json`

The entry point. The skill reads this to determine pass number, target SHA, and artifact paths.

```json
{
  "schema_version": "1.0.0",
  "tool_name": "<TOOL>",
  "tool_repo": "<absolute path>",
  "audit_workspace": "<absolute path to sibling>",
  "rubric_version": "<git SHA of references/rubric/SCORING-RUBRIC.md when scoring ran>",
  "passes": [
    {
      "pass": 1,
      "started_at": "2026-05-06T10:00:00Z",
      "completed_at": "2026-05-06T15:00:00Z",
      "mode": "full",
      "target_sha": "abc123...",
      "feature_branch": "agent-ergonomics-pass-1",
      "summary": {
        "surfaces_inventoried": 142,
        "surfaces_scored": 142,
        "recommendations_total": 47,
        "recommendations_applied": 12,
        "median_uplift_pts": 89,
        "regressions_count": 0,
        "fresh_eyes_rounds": 3
      },
      "artifacts": {
        "surface_inventory": "audit/surface_inventory.jsonl",
        "agent_surfaces": "audit/agent_surfaces.jsonl",
        "intent_corpus": "audit/intent_inference_corpus.jsonl",
        "recommendations": "audit/recommendations.jsonl",
        "playbook": "audit/playbook.md",
        "applied_changes": "audit/applied_changes.jsonl",
        "scorecard": "audit/scorecard_pass_1.md",
        "heatmap": "audit/heatmap.svg",
        "uplift_diff": "audit/uplift_diff.md",
        "regression_alerts": "audit/regression_alerts.md",
        "handoff": "audit/HANDOFF.md",
        "simulations_pre": "audit/agent_simulations/pre_pass_1/",
        "simulations_post": "audit/agent_simulations/post_pass_1/"
      }
    }
  ],
  "current_pass": 1,
  "pass_N+1_ready": true,
  "next_pass_focus": "self-documentation hardening + intent-inference for verbs in src/cmd/sync.rs"
}
```

---

## `audit/phase0_cli.json` — Phase 0 output (from `scripts/discover-cli.sh`)

Single JSON object describing the target CLI's language(s), build system, binary entry points, and existing agent-ergonomic surfaces. The skill reads this to pick the recommended mode and to seed Phase 1's recursive walk.

```jsonc
{
  "target_path": "/abs/path/to/target",
  "discovered_at": "2026-05-06T20:00:00Z",
  "languages": ["rust"],                                           // multi-element if polyglot
  "binaries": ["mytool"],                                          // entry-point names to invoke
  "env_var_prefix": "MYTOOL",                                      // detected from env-var usage
  "existing_surfaces": {
    "robot_mode": false,                                           // any --robot-* flag found in source
    "capabilities": false,                                         // any "capabilities --json" pattern
    "robot_docs": false                                            // any "robot-docs" / "--robot-help"
  },
  "recommended_mode": "full"                                       // "audit-only" if mature; "full" if gaps
}
```

---

## `audit/phase0_scope_decision.md` — Phase 0 output (from main agent + intake)

Markdown file capturing the user's intake answers and scope guardrails. Read by every subsequent phase to know which areas are off-limits. Required structure (one section per heading; agents may add others):

```markdown
# Pass <N> Scope Decision

**Mode.** `audit-only` | `full` | `re-score-only` | `simulate-only` | `single-surface-rescore`
**Target.** `<absolute path or git URL>`
**Sibling.** `<absolute path>`
**Feature branch.** `agent-ergonomics-pass-<N>` (full mode only; null otherwise)
**Triangulation appetite.** `none` | `peer-claude` | `multi-model`
**CASS appetite.** `skip` | `quick` | `deep`
**Date.** <ISO 8601>

## Must-not-touch

- File or area the user explicitly excluded (with one-line rationale)
- ...

## Deprecation policies

- "Add but never remove" / "Add deprecation warning before changing default" / etc.

## Out-of-scope feature work

- Feature requests that surfaced during intake but won't be addressed in this pass
- (These get filed as beads in Phase 10 for future passes — never silently bundled.)

## Resumed-pass notes

(if applicable)

- Prior pass: <N-1>
- Carryover: deferred recs from prior HANDOFF.md
```

The main agent reads `<SIBLING>/audit/phase0_scope_decision.md` at the start of every later phase to know constraints. Subagents that touch the target repo (applier, family-cross-cut-auditor, parity-auditor) consult the must-not-touch list before editing.

---

## `audit/phase0_skill_inventory.json` — Phase 0 output (from `scripts/check-skills.sh`)

Single JSON object listing referenced helper skills and whether each is installed. Drives the optional `scripts/install-referenced-skills.sh` bulk install. Advisory — never blocks a phase.

```jsonc
{
  "checked_at": "2026-05-06T20:00:00Z",
  "jsm_present": true,
  "skills": {
    "ubs":    {"present": true},
    "cass":   {"present": false},
    "...":    {"present": false}
  }
}
```

---

## `audit/surface_inventory.jsonl` — Phase 1 output

One record per agent surface. `surface_id` is deterministic given (kind, subtree, name). It is also a file-stem-safe handle: after the kind prefix, each `__`-separated segment must match `[A-Za-z0-9][A-Za-z0-9._-]*`. Do not include slash, whitespace, control characters, or shell metacharacters; dry-run and aggregation helpers use `surface_id` in artifact filenames. When a raw segment has to be normalized, append a short content hash so distinct surfaces such as `a b` and `a_b` cannot collapse to the same handle.

```jsonc
{
  "surface_id": "verb__list",                                    // computed by tools/compute_surface_id.sh
  "subtree": "list",                                             // top-level subtree this lives in
  "kind": "verb",                                                // verb|flag|env|exit|error|config|signal|prompt
  "name": "list",                                                // the visible name (e.g. "--json", "MYTOOL_HOME", "list")
  "source": {"file": "src/cmd/list.rs", "line": 42},
  "runtime": {
    "help_excerpt": "list   List all items.",                    // line from --help
    "invocation": "<TOOL> list --help",
    "exit_code": 0
  },
  "description": "Lists all items in the configured store.",
  "required": false,
  "deprecated": false,
  "mutates": false,                                              // for verbs only — does this op mutate state? Type: bool | null. The runtime walker (`scripts/inventory_surfaces.sh`) cannot infer this from `--help` output, so it emits `null` for every verb; the surface-inventorist subagent reads the source and sets the bool. Validators MUST treat `null` as "unknown / not yet inferred" rather than crashing on `if .mutates { ... }`.
  "discovered_at": "2026-05-06T10:05:00Z"
}
```

**Per-kind variants:**

```jsonc
// kind: flag
{
  "surface_id": "flag__list__json",
  "subtree": "list",
  "kind": "flag",
  "name": "--json",
  "short": "-j",                                                 // optional
  "type": "bool",                                                // bool|string|int|enum|path
  "enum_values": null,                                           // populated if type=enum
  "source": {"file": "src/cmd/list.rs", "line": 38},
  "runtime": {"help_excerpt": "  -j, --json     Output JSON"},
  "description": "Output JSON instead of human-readable.",
  "required": false,
  "deprecated": false,
  "discovered_at": "..."
}

// kind: env
{
  "surface_id": "env__MYTOOL_HOME",
  "subtree": null,                                               // env vars span all subtrees
  "kind": "env",
  "name": "MYTOOL_HOME",
  "source": {"file": "src/config.rs", "line": 17},
  "runtime": {"help_excerpt": "MYTOOL_HOME — root config dir; defaults to $XDG_CONFIG_HOME/mytool"},
  "description": "Root config directory.",
  "required": false,
  "deprecated": false,
  "default": "$XDG_CONFIG_HOME/mytool",
  "discovered_at": "..."
}

// kind: exit
{
  "surface_id": "exit__1",
  "subtree": null,
  "kind": "exit",
  "name": "1",
  "value": 1,
  "condition": "user-input-error",
  "source": {"file": "src/main.rs", "line": 99},
  "description": "Generic user-input or argument-parsing error.",
  "discovered_at": "..."
}

// kind: error
{
  "surface_id": "error__list_no_store",
  "subtree": "list",
  "kind": "error",
  "name": "no_store_configured",
  "message": "no store configured; run 'mytool init' first",
  "source": {"file": "src/cmd/list.rs", "line": 22},
  "description": "Emitted when no store is configured.",
  "exit_code": 3,
  "discovered_at": "..."
}

// kind: config
{
  "surface_id": "config__store_path",
  "subtree": null,                                               // config keys span all subtrees
  "kind": "config",
  "name": "store.path",                                          // dotted path within the config file
  "config_format": "toml",                                       // toml|yaml|json|ini|env|other
  "config_file": "~/.config/mytool/config.toml",                 // default location; honors XDG/etc.
  "type": "path",                                                // bool|string|int|enum|path
  "enum_values": null,
  "default": "$XDG_DATA_HOME/mytool",
  "source": {"file": "src/config.rs", "line": 27},
  "runtime": {"help_excerpt": "store.path: path to the store; defaults to $XDG_DATA_HOME/mytool"},
  "description": "Where the store lives on disk.",
  "required": false,
  "deprecated": false,
  "sensitive": false,                                            // true → mask in `mytool config show` output
  "discovered_at": "..."
}

// kind: signal
{
  "surface_id": "signal__SIGINT",
  "subtree": null,                                               // signals are process-level
  "kind": "signal",
  "name": "SIGINT",                                              // POSIX signal name
  "behavior": "graceful_shutdown",                               // graceful_shutdown|abort|ignored|reload|undefined
  "source": {"file": "src/main.rs", "line": 14},
  "runtime": {"help_excerpt": null},                             // signals usually undocumented in --help
  "description": "Ctrl-C — flush in-flight writes and exit with code 130 (128 + 2).",
  "exit_code": 130,                                              // expected exit on this signal
  "discovered_at": "..."
}

// kind: prompt
{
  "surface_id": "prompt__delete_confirm",
  "subtree": "delete",
  "kind": "prompt",
  "name": "confirm_delete",
  "message": "Really delete <N> items? [y/N] ",                  // verbatim prompt text
  "source": {"file": "src/cmd/delete.rs", "line": 41},
  "runtime": {"help_excerpt": null},
  "description": "Interactive confirmation before destructive delete.",
  "non_tty_behavior": "abort",                                   // abort|default_no|default_yes|requires_--yes
  "bypass_flag": "--yes",                                        // flag that skips this prompt; null if no bypass
  "discovered_at": "..."
}
```

---

## `audit/agent_surfaces.jsonl` — Phase 2 output

One record per scored surface. After Phase 6, the post-pass record is appended (so the file grows monotonically; older rows are filtered by `pass` field). For backwards compatibility with prior passes, `tools/diff_scorecards.sh` filters by `pass`.

**Note on `scorer_id`.** Per-scorer partial files (`audit/partial/scores_pass<N>_<SID>_scorer<X>.jsonl`) have a `scorer_id` field identifying which scorer (A, B, or "tiebreaker") produced them. The aggregator (`scripts/aggregate_scores.sh`) intentionally DROPS `scorer_id` from the final aggregated row — the row represents a consensus median across multiple scorers, not any single scorer's view. The fact that a tiebreaker ran is captured in `score_confidence.tiebroken: true`. Validators should not expect `scorer_id` on rows in this file; it appears only in the `partial/` files.

```jsonc
{
  "surface_id": "verb__list",
  "pass": 1,
  "rubric_version": "abc123...",                                 // git SHA of rubric file
  "scores": {
    "agent_intuitiveness": 850,
    "agent_ergonomics": 700,
    "agent_ease_of_use": 600,
    "output_parseability": 900,
    "error_pedagogy": 650,
    "intent_inference": 400,
    "safety_with_recovery": 1000,                                // n/a-as-perfect for read-side verb
    "determinism_and_reproducibility": 850,
    "self_documentation": 650,
    "composability": 800,
    "regression_resistance": 300                                 // no golden test yet
  },
  "weighted_score": 691,                                         // arithmetic mean of the 11 per-dim medians (computed as `(sum of present dims) / (count of present dims) | floor` — i.e. integer floor, not round-half-up; range [0, 1000]; `null`-scored dims are excluded from both numerator and denominator). Producers MUST emit an integer. NOTE: this is INTENTIONALLY archetype-neutral (no per-archetype weights applied) so that cross-archetype comparison works. Per-archetype dimension weights from `CLI-ARCHETYPES.md` flow into Phase 4 RECOMMENDATION PRIORITIZATION only (recommender + synthesizer scale `priority_components.score_gap` by the archetype's weight on the failing dim) — they do NOT modify this weighted_score.
  "score_confidence": {
    "spread_max": 75,                                            // worst-dimension spread between two scorers
    "tiebroken": false                                           // true if ≥1 dim spread 300-499 → tiebreaker ran
  },
  "evidence": {
    "agent_intuitiveness": {
      "invocation": "<TOOL> list",
      "stdout_excerpt": "item1\nitem2\n",
      "stderr_excerpt": ""
    },
    "agent_ergonomics": {
      "file": "src/cmd/list.rs",
      "line": 42,
      "note": "list verb is one-call, returns parseable output"
    }
  },
  "notes": "intent_inference low because '--jsno' typo not corrected; see corpus_id:naive-04.",
  "scored_at": "2026-05-06T11:00:00Z"
}
```

---

## `audit/intent_inference_corpus.jsonl` — Phase 3 output

One record per attempted invocation. Generated by `intent-stresser-naive` + `intent-stresser-savvy`; outcomes filled by `intent-runner` (and/or `scripts/run_intent_corpus.sh`).

```jsonc
{
  "corpus_id": "naive-04",
  "generator": "naive",                                          // "naive" | "savvy"
  "category": "A",                                               // see INTENT-CORPUS-GENERATION.md categories
  "invocation": "mytool --jsno",                                 // human-readable form (display only after argv is set)
  "argv": ["mytool", "--jsno"],                                  // REQUIRED for new corpora: array of strings. argv[0] is replaced with <TOOL> at runtime so the same corpus replays against different binaries. The runner accepts legacy `invocation`-only entries when the string contains only whitespace-separated tokens with no shell metachars (`$`, backtick, `;`, `&`, `|`, `<`, `>`, `()`, `{}`, `[]`, `*`, `?`, `!`, `~`, quotes, backslash) — anything else is `classification: "skipped"` with `skip_reason` set. New generators MUST emit `argv`; `invocation` is display-only.
  "cwd": null,                                                   // optional working directory; null = inherit
  "env": {},                                                     // optional extra env vars merged on top of NO_COLOR/TERM/CI
  "mutates": false,                                              // true if the invocation would mutate state (delete, write, etc.)
  "safe_to_run": true,                                           // must be true for runner to actually invoke a mutating entry; otherwise -> skipped
  "predicted_outcome": "useful_hint",                            // generator's prediction
  "classification": "useless_error",                             // runner's actual outcome: silent_fail|useless_error|useful_hint|inferred_and_acted|skipped
  "skip_reason": null,                                           // populated only when classification == "skipped" (e.g. unsafe shell syntax in legacy `invocation`, mutating without safe_to_run, missing cwd)
  "matched_predicted": false,                                    // classification == predicted_outcome
  "stresses_surface_id": "flag__list__json",
  "stdout": "",
  "stderr": "error: unknown flag '--jsno'\n",
  "exit_code": 2,
  "reason": "agent confuses --json spelling",
  "cites": [],                                                   // populated by savvy generator only
  "generated_at": "2026-05-06T11:00:00Z",                        // when the corpus entry was generated (set by intent-stresser-{naive,savvy} and scripts/generate_intent_corpus.sh; preserved by the runner)
  "ran_at": "2026-05-06T11:30:00Z"                               // when the runner actually executed the entry (added/overwritten by run_intent_corpus.sh)
}
```

**Argv-vs-invocation contract.** Generators may emit either an `argv` array (preferred) or just an `invocation` string. The runner replaces `argv[0]` with the actual `<TOOL>` path before exec, so corpora are tool-agnostic. Legacy `invocation`-only entries are accepted only when the string contains *only* whitespace-separated tokens with no shell metacharacters (`$`, backtick, `;`, `&`, `|`, `<`, `>`, `()`, `{}`, `[]`, `*`, `?`, `!`, `~`, quotes, backslash). Any unsafe legacy entry is recorded with `classification: "skipped"` and `skip_reason: "legacy invocation contains shell syntax; provide argv[] instead"` — the runner never executes it through a shell. New corpora **should always emit `argv`**.

---

## `audit/recommendations.jsonl` — Phase 4 output

One record per recommendation. Updated in Phase 5 (`applied:true`). The `pass`
field is the audit pass that produced the recommendation.

```jsonc
{
  "recommendation_id": "R-007",
  "pass": 1,
  "title": "Add levenshtein-1 typo correction for --json/--colour/--verbose",
  "summary": "When an unknown flag is one edit away from a real flag, suggest the real flag in the error message AND optionally proceed-with-warning.",
  "surface_ids": [
    "flag__list__json",
    "flag__add__json",
    "flag__verbose"
  ],
  "diff_sketch": "in src/cli.rs::handle_unknown_flag, compute levenshtein distance to known flags; if distance == 1, print 'did you mean --<closest>?' and exit 2 with the suggestion in stderr.",
  "expected_uplift_per_dim": {
    "intent_inference": 400,
    "error_pedagogy": 200
  },
  "expected_uplift_total": 600,
  "risk": "no breakage; new behavior only on previously-erroring inputs",
  "test_plan": "audit/regression_tests/R-007__levenshtein_typo_hint.test.sh — invokes mytool --jsno and asserts stderr matches 'did you mean --json?'.",
  "priority": 0.0875,                                            // frequency × score_gap × blast_radius (raw product in [0, 1]; per PRIORITY-FORMULA.md). MUST be a JSON number; producers SHOULD round to 4 decimal places to avoid float-noise like 0.087499999...; consumers MUST tolerate any float in [0, 1] including exact zero.
  "priority_components": {
    "frequency": 0.7,
    "score_gap": 0.5,
    "blast_radius": 0.25,
    "blast_radius_reason": "workflow-class: agent corrects after one round-trip but with friction"  // optional; per PRIORITY-FORMULA.md, default to workflow (0.50) for ambiguous cases and document the rationale here
  },
  "applied": false,                                              // flipped to true in Phase 5
  "applied_at": null,
  "applied_commit_sha": null,
  "deferred_reason": null,                                       // set if applied:false AND deferred
  "triangulation": {                                             // optional; populated if multi-model triangulation ran
    "claude_agreed": true,
    "codex_agreed": true,
    "gemini_agreed": true,
    "consensus_diff": null
  },
  "anchor_quote": "[Q-300]",                                     // quote-bank entry the rec aligns with
  "anchor_pattern": "Pattern 2 from CANONICAL-EXEMPLARS",        // canonical exemplar pattern
  "counter_example": "CE-3 from COUNTER-EXAMPLES",               // counter-example the rec fixes
  "operators_applied": ["⟁", "🩹"],                              // glyphs from OPERATORS.md
  "created_at": "2026-05-06T12:00:00Z"
}
```

---

## `audit/applied_changes.jsonl` — Phase 5 output

One record per applied change. The `pass` field is the audit pass where the
change was applied.

```jsonc
{
  "recommendation_id": "R-007",
  "pass": 1,
  "bead_id": "br-1234",
  "commit_sha": "def456...",
  "files_changed": [
    {
      "path": "src/cli.rs",
      "before_excerpt": "fn handle_unknown_flag(flag: &str) -> Error {\n    Error::UnknownFlag(flag.into())\n}",
      "after_excerpt": "fn handle_unknown_flag(flag: &str) -> Error {\n    if let Some(suggestion) = closest_known(flag, KNOWN_FLAGS, 1) {\n        return Error::UnknownFlagDidYouMean(flag.into(), suggestion);\n    }\n    Error::UnknownFlag(flag.into())\n}",
      "lines_added": 4,
      "lines_removed": 1
    }
  ],
  "surface_ids_touched": [
    "flag__list__json",
    "flag__add__json",
    "flag__verbose",
    "error__unknown_flag"
  ],
  "test_path": "audit/regression_tests/R-007__levenshtein_typo_hint.test.sh",
  "applied_at": "2026-05-06T13:30:00Z"
}
```

---

## `audit/phase0_archetype.json` — Phase 0 output (from `subagents/cli-archetype-classifier.md`)

Single JSON object identifying which CLI archetype(s) the target falls into. Drives dimension-weight overrides (per `references/methodology/CLI-ARCHETYPES.md`) and selects the canonical-task corpus for Phase 9.

```jsonc
{
  "primary_archetype": "search-tool",                            // one of the 15 archetypes
  "secondary_archetype": null,                                    // optional, for multi-archetype tools
  "confidence": 0.85,                                             // 0..1 score from classifier evidence
  "evidence": [
    {"signal": "tool description matches", "match": "search/grep/find idioms in --help"},
    {"signal": "verbs present", "match": ["search", "grep", "find"]}
  ],
  "weight_overrides": {                                           // per CLI-ARCHETYPES.md weight table
    "output_parseability": 1.5,
    "determinism_and_reproducibility": 1.3
  },
  "canonical_tasks_source": "archetype-default + README mining + CASS findings",
  "classified_at": "2026-05-06T10:30:00Z"
}
```

---

## `audit/canonical_tasks.md` — Phase 0 output (from `subagents/canonical-task-author.md`)

Markdown file with one task per `## Task NN: <slug>` heading. Read by `subagents/canonical-task-simulator.md` in Phase 3 (pre-pass) and Phase 9 (post-pass). Each task block has the structure described in `assets/canonical-task-template.md`.

Required structure:
```markdown
# Canonical Tasks for <TOOL>

(generated by canonical-task-author from archetype + README + CASS findings)

## Task 01: <slug>

**Statement.** (User-perspective description)

**Tags.** read-only / mutating / pipe-friendly / multi-step / requires-config / network-required

**Expected outcome.**
- exit code: 0
- stdout: ...
- side effects: ...

**Documented in.** README.md "Examples" § OR `<tool> --help` OR CASS finding F-NNN

**Pre-pass round-trips estimate.** <K>
**Post-pass target.** <K - 1 or K>

## Task 02: <slug>
...
```

The simulator reads tasks in order (Task 01 first, etc.) and emits one `task-NN-<slug>.transcript.jsonl` per task into `audit/agent_simulations/<stage>_pass_<N>/`.

---

## `audit/agent_simulations/<stage>_pass_<N>/task-NN-<slug>.transcript.jsonl` — Phase 3 / Phase 9 output (from `subagents/canonical-task-simulator.md`)

One JSONL record per "step" the fresh-context simulator agent took. Re-runnable via `scripts/replay_simulation.sh`.

```jsonc
{
  "task_slug": "list-with-filter",                               // kebab-case slug, used in the filename; task_number filename is zero-padded (`task-01-list-with-filter.transcript.jsonl`) but task_number here is the unpadded integer (1, not "01"). Consumers correlating filename ↔ record use `(task_number, task_slug)`, not the padded prefix.
  "task_number": 1,                                              // integer, ≥ 1, matches the numeric portion of `task-NN-` in the filename without zero-padding
  "stage": "pre|post",
  "pass": 1,
  "step": 1,                                                      // 1-indexed
  "intent": "I want to list items filtered by status=active",    // simulator's interpretation
  "invocation": "mytool list --status active",                   // display text for the exact command attempted
  "argv": ["mytool", "list", "--status", "active"],              // replay replaces argv[0] with the supplied binary path
  "cwd": null,                                                    // working directory used for the step; null = transcript runner cwd
  "env": {},                                                      // per-step env overlay, if any
  "stdin_data": null,                                             // null unless data was piped in
  "exit_code": 0,
  "stdout": "...",                                                // truncated to ~4 KB
  "stderr": "...",
  "elapsed_ms": 142,
  "outcome": "success|partial|stuck|error",                       // simulator's read of the step
  "ran_at": "2026-05-06T18:00:00Z"
}
```

Per-task summary lives at `task-NN-<slug>.summary.md` alongside; per-stage rollup at `summary.md` in the same dir (counts, median round-trips, stuck-task list).

---

## `audit/phase7_fresh_eyes_log.md` — Phase 7 output (from `subagents/fresh-eyes.md`)

Markdown log of the three fresh-eyes review rounds. Drives the Phase 7 termination gate ("two consecutive CLEAN rounds").

Required structure (one section per round, appended in order):
```markdown
# Phase 7 Fresh-Eyes Log — Pass <N>

## Round 1

**Prompt.** Round 1 (read recent diff)

**Findings.** 7 total; 4 trivial; 3 substantive.

**Substantive fixes.**
- <commit_sha>: fixed off-by-one in render_heatmap.sh range
- <commit_sha>: corrected exit code in verify-determinism.sh
- <commit_sha>: removed dead branch in synthesize_recommendations.mjs

**Verdict.** NOT_CLEAN

## Round 2

**Prompt.** Round 2 (random walk + trace flows)
**Findings.** 2 total; 2 trivial; 0 substantive.
**Verdict.** CLEAN

## Round 3

**Prompt.** Round 3 (review fellow agents' work)
**Findings.** 1 total; 1 trivial; 0 substantive.
**Verdict.** CLEAN

**Termination.** Two consecutive CLEAN rounds → exit Phase 7.
```

A round is **CLEAN** if all findings are trivial (typo / whitespace / comment polish only). Phase 7 exits when two consecutive rounds are CLEAN.

---

## `audit/metrics_timeseries.jsonl` — Phase 10 output (from `subagents/benchmark-collector.md`)

Append-only time series of per-pass metrics. Used for cross-pass uplift analysis and continuous-improvement cadence (per `CONTINUOUS-IMPROVEMENT.md`).

```jsonc
{
  "pass": 2,
  "tool_name": "mytool",
  "rubric_version": "abc123",
  "target_sha": "def456",
  "mode": "full",
  "completed_at": "2026-05-06T18:00:00Z",
  "median_weighted_score": 821,                                   // median across all surfaces
  "p25_weighted_score": 650,                                      // first quartile
  "p75_weighted_score": 900,                                      // third quartile
  "median_uplift_pts": 130,                                       // vs prior pass; null on first pass
  "regressions_count": 0,                                         // surfaces with weighted drop > 50
  "below_polish_bar_count": 4,                                    // surfaces with weighted < 750
  "per_dim_medians": {
    "agent_intuitiveness": 850,
    "agent_ergonomics": 750,
    "agent_ease_of_use": 700,
    "output_parseability": 900,
    "error_pedagogy": 800,
    "intent_inference": 820,
    "safety_with_recovery": 950,
    "determinism_and_reproducibility": 880,
    "self_documentation": 750,
    "composability": 820,
    "regression_resistance": 600
  },
  "applied_recommendations_count": 12,
  "deferred_recommendations_count": 5,
  "fresh_eyes_rounds": 3,
  "simulation_median_round_trips": 2.4,                          // Phase 9 metric
  "wall_time_minutes": 187
}
```

Records are append-only (one per pass); never edit prior records. Rendered to `audit/metrics_timeseries.md` for human reading via the user-side workspace renderer (per `CONTINUOUS-IMPROVEMENT.md`).

---

## `audit/uplift_diff.md` — Phase 6 output (markdown table)

```markdown
# Pass 1 → Pass 2 Uplift Diff

| surface_id | prior weighted | new weighted | Δ | dims improved | dims regressed |
|------------|----------------|--------------|---|---------------|----------------|
| verb__list | 691 | 821 | +130 | intent_inference (+400), error_pedagogy (+200), regression_resistance (+50) | none |
| flag__list__json | 720 | 720 | 0 | none | none |
| flag__add__json | 580 | 770 | +190 | intent_inference (+400), error_pedagogy (+200), self_documentation (+50) | none |
| ...

**Median uplift across applied surfaces:** +89 pts.
**Regressions detected:** 0 surfaces dropped > 50 pts overall.
**Pass 2 stop condition:** met (median ≥ 25 pts AND no regressions).
```

---

## `audit/regression_alerts.md` — Phase 6 output

```markdown
# Pass <N> Regression Alerts

## Hard stops (drop > 50 pts overall)

(none — clean)

## Warnings (drop > 25 pts on any single dimension)

| surface_id | dim | prior | new | Δ | likely cause |
|------------|-----|-------|-----|---|--------------|
| flag__verbose | composability | 800 | 770 | -30 | new --robot-meta output adds extra stderr lines; verify pipe-friendliness |
```

---

## `audit/agent_simulations/{pre,post}_pass_<N>/summary.md`

```markdown
# Pass <N> Simulation Summary

| Task | First-try success | Round-trips | Stuck? | Notes |
|------|--------------------|--------------|--------|-------|
| task-01-list-then-filter | ❌ → ✅ (after typo hint) | 2 | no | tool corrected --filter→--grep |
| task-02-init-then-add | ✅ | 2 | no | clean path |
| task-03-broken-config-recovery | ❌ | 5 | yes | tool didn't suggest 'mytool doctor'; rec R-NN filed |
| ...

**Overall:** N/M tasks completed; median round-trips: K; pre-pass median: K' (Δ = K-K').
```

---

## Validation rules (enforced by `tools/validate_scorecard.sh`)

1. **Every `surface_id` in `agent_surfaces.jsonl` matches a `surface_id` in `surface_inventory.jsonl`.**
2. **No `score > 700` lacks evidence in `evidence.<dim>`.**
3. **Every record has `pass` and `rubric_version`.**
4. **`weighted_score` matches the documented weighting (default: arithmetic mean of present-dim medians, integer-floored — see `aggregate_scores.sh` and the `weighted_score` schema comment).**
5. **`recommendation_id` format: `R-\d{3,4}`.**
6. **Every `applied:true` rec has a non-null `commit_sha` AND a corresponding entry in `applied_changes.jsonl`.**
7. **No two records in `agent_surfaces.jsonl` for the same `(surface_id, pass)` pair (would indicate a double-score; tiebreaker should produce a single median).**

If any rule fails, `validate_scorecard.sh` exits non-zero with a stderr message naming the violating record.
