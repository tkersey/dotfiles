<!--
rubric_version: 1.0.0
schema: rubric.frontmatter.v1
last_changed_at: 2026-05-07
last_changed_summary: "initial 1.0.0 (formerly unversioned). Added explicit version frontmatter + CHANGELOG.md tracking."
-->

# SCORING-RUBRIC — 11 dimensions × 5 anchor levels

> **rubric_version: 1.0.0** — every score must record this version. See `references/rubric/CHANGELOG.md` for change history. Bumping this version invalidates prior scores; run `scripts/migrate-scores.sh` after edits.

Every agent surface gets scored on each of these 11 dimensions. Anchors at 0, 250, 500, 750, 1000 give scorers a calibrated reference. Concrete examples are taken from the canonical exemplars (`dcg`, `bv`, `am`, `ubs`, `cass`).

The rubric is overridable: projects may extend it (add anchors, add dimensions) without forking the skill, by editing this file. Bump `rubric_version` in the manifest when you do.

---

## 1. agent_intuitiveness

> Would the first command an agent guesses succeed, or be redirected with a useful hint?

| Score | Anchor |
|-------|--------|
| 0 | First-try invocation crashes the binary, hangs forever, or silent-exits. Agent has no way to know what went wrong. (Example: `<tool>` panics on `--help`; `<tool>` launches a TUI in non-TTY mode.) |
| 250 | First-try fails with a generic framework error ("usage: ...; see --help"). Agent must consult external docs to make progress. |
| 500 | First-try fails but the error names what's missing (e.g. "missing required argument PATH"). Agent can recover after one round-trip. |
| 750 | First-try either succeeds OR errors with a hint that names the exact correction. (Example: `<tool> ls` errors with "did you mean 'list'?".) |
| 1000 | First-try succeeds. The bare invocation does something useful AND points at the next steps (e.g. `bv --robot-triage` or `<tool> --help` always returns a useful summary). |

Evidence required for ≥ 750: invocation transcript showing first-try outcome.

---

## 2. agent_ergonomics

> Minimum keystrokes / tool-calls / round-trips to accomplish the canonical task; macros vs. granular composition where relevant.

| Score | Anchor |
|-------|--------|
| 0 | Canonical task requires 5+ round-trips of trial-and-error. No mega-command. No macro for common compositions. |
| 250 | Canonical task takes 3 round-trips with knowledge of the tool. No `--robot-*` or `--json` mode to collapse calls. |
| 500 | Tool has `--json` for read-side verbs; canonical task is 2 round-trips. No mega-command. |
| 750 | Tool has at least one mega-command that bundles 2+ slices of the canonical task into one call. (Example: `bv --robot-triage` collapses `triage`+`status`+`next`.) |
| 1000 | Mega-command returns ALL slices the agent needs (quick_ref + recommendations + commands + project_health) AND embeds copy-paste-ready follow-up commands. Granular composition still available for control. |

Evidence required for ≥ 750: cite the mega-command + show its output structure.

---

## 3. agent_ease_of_use

> Discoverability without external docs (`--help`, `capabilities`, self-describing JSON, `robot-docs`).

| Score | Anchor |
|-------|--------|
| 0 | Tool has no `--help` or `--help` is incoherent. Agent must read README.md or website to make progress. |
| 250 | `--help` exists but is bare (just flag list); no examples, no env-var hints, no agent-mode pointer. |
| 500 | `--help` covers verbs and flags with examples. Mentions `--json` if it exists. |
| 750 | `--help` covers verbs, flags, examples, env vars, and points to `<tool> capabilities` or `<tool> robot-docs`. |
| 1000 | All of 750 PLUS an "AGENT/AUTOMATION" section in `--help` that surfaces `--robot-*`, `--json`, `capabilities`, `robot-docs guide` and exit-code dictionary. (Example: `cass --help` plus `cass robot-docs guide` covers everything.) |

Evidence required for ≥ 750: cite the `--help` excerpt with the agent-pointer.

---

## 4. output_parseability

> Stable schema, `--json` / `--robot-*` mode, stdout-data / stderr-diagnostics separation, exit-code contract.

| Score | Anchor |
|-------|--------|
| 0 | Output is human-only prose. No `--json`. Stdout and stderr both carry data. Exit codes are ad-hoc. |
| 250 | `--json` exists for some verbs but not all. Schema is undocumented and changes between versions. |
| 500 | Every read-side verb has `--json`. Schema is informally documented. Stdout is mostly data. Exit codes follow basic 0/1 convention. |
| 750 | Every read-side verb has `--json`. Schema is pinned (e.g. `--robot-meta` includes contract version). Stdout is data-only; stderr is diagnostics-only. Exit-code dictionary documented in `--help`. |
| 1000 | All of 750 PLUS: (a) `<tool> capabilities --json` returns the full output schema for every verb; (b) `--robot-meta` field gives provenance (search_mode, fallback_tier, etc.) so agents can interpret partial results. (Example: `cass --robot-meta` field set.) |

Evidence required for ≥ 750: cite the schema definition + a transcript showing stdout-only-data discipline.

---

## 5. error_pedagogy

> Does the error message teach? Suggest the safe alternative? Cite the exact flag the agent should have used?

| Score | Anchor |
|-------|--------|
| 0 | Error is a stack trace OR generic "syntax error" / "invalid argument". No hint at what to do. |
| 250 | Error names what failed but offers no path forward ("unknown flag '--jsno'"). |
| 500 | Error names what failed AND points to `--help` or the relevant subcommand. Generic. |
| 750 | Error names the exact flag/command the agent should have used. (Example: `dcg` blocks "git reset --hard" with "use git stash; use git revert; back up first.") |
| 1000 | All of 750 PLUS: (a) cites the source location if applicable (`<tool> error: foo at config.toml:12`); (b) for typos, levenshtein-1 "did you mean X?" suggestion AND optionally proceed-with-warning. |

Evidence required for ≥ 750: cite the error message text from a runtime invocation.

---

## 6. intent_inference

> How gracefully does the tool recover from a legible-but-wrong invocation (typos, deprecated flags, common mis-orderings)?

| Score | Anchor |
|-------|--------|
| 0 | Every typo / wrong-order / family-confused invocation errors uselessly. No alias support. |
| 250 | Some flag aliases (`-h`/`--help`) but no typo correction. Wrong subcommand order errors with "see --help." |
| 500 | Common aliases (`ls`/`list`, `rm`/`delete`) work or error with "did you mean". No typo correction. |
| 750 | Typo correction at edit-distance 1 ("did you mean --json?"). Common aliases proceed-with-warning. |
| 1000 | All of 750 PLUS: (a) deprecated flag spellings proceed-with-warning + deprecation timeline; (b) wrong-order invocations re-order silently (or error with the canonical form printed). |

Evidence required for ≥ 750: corpus entry showing the misspelling + tool's response.

---

## 7. safety_with_recovery

> Irreversible operations gated; safe alternatives always offered; reservations / leases / dry-runs available.

| Score | Anchor |
|-------|--------|
| 0 | Destructive op runs immediately on first invocation. No `--dry-run`. No `--yes` gate. (Read-side verbs: 1000 by default — n/a-as-perfect.) |
| 250 | Destructive op requires `--force` or `--yes` but doesn't suggest `--dry-run` first. No safe alt named in error. |
| 500 | Destructive op has both `--yes` and `--dry-run`. Error message names the safe alternative. |
| 750 | All of 500 PLUS: (a) reservation / lease pattern for distributed mutations; (b) error message cites the canonical rollback command. |
| 1000 | All of 750 PLUS: (a) `<tool> doctor` self-diagnoses reversibility; (b) advisory-lock pattern for concurrent mutations; (c) `--plan` option that previews state changes. (Example: `am file_reservation_paths` + `dcg` block messages.) |

Evidence required for ≥ 750: cite the dangerous op's `--help` showing the gate AND the error message naming the alt.

For read-side verbs: score 1000 with `n/a:true` — no irreversible ops to gate.

---

## 8. determinism_and_reproducibility

> Stable output ordering, no wall-clock leakage, deterministic IDs, content-addressed where possible.

| Score | Anchor |
|-------|--------|
| 0 | Output ordering is non-deterministic (hashmap iteration). Wall-clock timestamps in stdout free text. Random IDs. Same invocation → different bytes. |
| 250 | Output is sorted but contains wall-clock timestamps in prose. Re-run produces ~same output but bytes differ. |
| 500 | Output is sorted; timestamps relegated to JSON `meta.ts` field. Honor `SOURCE_DATE_EPOCH` partially. |
| 750 | Same input → same output bytes (modulo documented volatile fields like `request_id`). Honor `SOURCE_DATE_EPOCH`. Stable handle pattern (`project_key`, `surface_id`). |
| 1000 | All of 750 PLUS: (a) content-addressed IDs (hash of inputs); (b) `data_hash` / `etag` field in output so downstream can detect changes; (c) `--seed N` for any RNG-flavored ops. (Example: `bv --robot-insights` includes `data_hash`.) |

Evidence required for ≥ 750: two consecutive `--json` invocations with byte-identical output (or only-volatile-fields differing).

---

## 9. self_documentation

> `--help` quality, embedded examples, `capabilities` endpoint, machine-readable schema export.

| Score | Anchor |
|-------|--------|
| 0 | No `--help` worth the name. No `capabilities`. No examples. Agent can't introspect. |
| 250 | `--help` exists with flag list; no examples; no `capabilities`. |
| 500 | `--help` has examples and env-var docs. No `capabilities`. |
| 750 | `<tool> capabilities --json` exists and returns version/features/exit_codes/env_vars. `--help` mentions it. |
| 1000 | All of 750 PLUS: (a) `<tool> robot-docs guide` paste-ready agent handbook in-tool; (b) `<tool> schema --json` for output-schema introspection; (c) every verb's `--help` cross-references the related verbs. (Example: `cass capabilities --json` + `cass robot-docs guide`.) |

Evidence required for ≥ 750: cite `<tool> capabilities --json` output (or equivalent).

---

## 10. composability

> Exit codes / stdout work cleanly in pipelines; no surprise interactive prompts in non-TTY mode; honors `NO_COLOR`, `CI`, `--yes`.

| Score | Anchor |
|-------|--------|
| 0 | Pipes are broken: ANSI codes leak into piped stdout; tool prompts in non-TTY; ignores `NO_COLOR`. Cannot be used in scripts. |
| 250 | Detects piped stdout for color, but ignores `NO_COLOR=1`. May still prompt in non-TTY. |
| 500 | Detects piped stdout AND honors `NO_COLOR`. Prompts in non-TTY but exits non-zero with a hint. |
| 750 | All of 500 PLUS: honors `CI=true` (suppresses prompts). Honors `TERM=dumb`. Cache directory under `$XDG_CACHE_HOME`. |
| 1000 | All of 750 PLUS: (a) honors `SOURCE_DATE_EPOCH`; (b) explicit `--yes` flag for prompts (instead of relying on env detection); (c) verbose log lines on stderr never contaminate stdout. (Example: `ubs` clean pipeline composability.) |

Evidence required for ≥ 750: pipe + non-TTY + NO_COLOR transcripts.

---

## 11. regression_resistance

> Golden tests, snapshot tests, schema-pinned outputs that protect ergonomics from drift.

| Score | Anchor |
|-------|--------|
| 0 | No tests pinning the agent-facing surface. Help text drift would not be caught. JSON schema drift would not be caught. |
| 250 | A handful of snapshot tests for top-level help. Subcommand drift not tested. |
| 500 | `--help` for top-level + every subcommand has a snapshot test. JSON schema for each verb has at least one assertion. |
| 750 | All of 500 PLUS: (a) every `--robot-*` mode has a contract-pinning test (`--robot-meta` schema asserted); (b) golden tests for canonical agent-task transcripts. |
| 1000 | All of 750 PLUS: (a) golden tests run in CI on every PR; (b) test failure messages cite the agent-ergonomic dimension that would regress; (c) drift-guard tests for `capabilities --json` schema (any change requires explicit version bump). |

Evidence required for ≥ 750: cite the test file path + a representative test assertion.

For Pass 1 (no tests yet), score 0 across the board. After Phase 5, surfaces that received `audit/regression_tests/R-NNN__*.test.{sh,rs,py,ts}` get scored against the new bar.

---

## Default weighting

Default weighted_score = arithmetic mean of the 11 dim scores.

To override (project-specific): edit this file's "Default weighting" section to specify per-dim weights, e.g.:

```yaml
weights:
  agent_intuitiveness: 1.5
  agent_ergonomics: 1.5
  intent_inference: 1.5
  output_parseability: 1.5
  safety_with_recovery: 1.5
  others: 1.0
```

Then bump `rubric_version` and re-score.

---

## Per-surface-class adjustments

Not every dimension applies equally to every surface class. See `SURFACE-CLASSES.md` for per-class scoring guidance. Highlights:

- **Read-side verb**: `safety_with_recovery` scores 1000 with `n/a:true`.
- **Mutating verb**: `safety_with_recovery` is critical; weight × 1.5 if user opted into project weighting.
- **Env var**: `error_pedagogy` is "what happens when the env var is malformed?"; `composability` is "does the env var name follow `XDG_*`/`<TOOL_PREFIX>_*` conventions?"; many other dims n/a.
- **Exit code**: `output_parseability` is "is the exit value documented?"; `composability` is "is it stable across versions?"; `error_pedagogy` is "does the source comment explain what the value means?".
- **Error message**: only `error_pedagogy`, `intent_inference`, `composability` score meaningfully; rest n/a.

`tools/validate_scorecard.sh` allows `n/a:true` records but verifies they are accompanied by a "applies to" justification in `notes`.
