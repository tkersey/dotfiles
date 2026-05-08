---
name: agent-ergonomics-and-intuitiveness-maximization-for-cli-tools
description: >-
  Score and rigorously improve a CLI tool's ergonomics for AI agents as the
  primary user. Use when "agent ergonomics", "make CLI agent-friendly", "robot
  mode audit", "intuitiveness scoring", "score my CLI for agents", or rebuilding
  a CLI's --help / --json / robot surface. Produces a sibling
  `__agent_ergonomics_audit/` workspace with surfaces, scorecard, heatmap,
  recommendations, playbook, regression tests, applied on an `agent-ergonomics-pass-N` branch.
---

<!-- TOC: One Rule | Inputs | Mode Router | Skill Bootstrap | Phase Loop | Parallelism | Dimensions & Rubric | Polish Bar | Scoring Workspace Layout | IO Contracts | Anti-Patterns | Failure Modes | Pre-Flight & End | Reference Index | Scripts | Subagents | Assets | Self-Test -->

# Agent Ergonomics and Agent Intuitiveness Maximization for CLI Tools

> **First action — cold-context agents start here.** When activated for "audit `<TARGET>`", the agent MUST execute these steps in order before any other work:
>
> 1. **Run intake.** Open `assets/intake-prompt.md` and ask the user the 8 questions verbatim. Default mode: see [Mode-default heuristic](#mode-default-heuristic) below — pick a default deterministically and let the user override.
> 2. **Pre-flight checklist.** Run `scripts/preflight.sh <TARGET>` to verify: target is a directory, target's `<TOOL>` binary builds + `--help` exits 0, `jq` + `git` + `flock` available, optional helpers (Beads `br`, Agent Mail) detected with fallback path noted. Fail fast on missing requirements with an actionable message; don't proceed to scaffold until pre-flight is green or the user has explicitly accepted the missing-helper fallback.
> 3. **Skill bootstrap (Phase 0.5).** Run the three scripts in `## Skill Bootstrap` below in EXACT order: `scaffold-workspace.sh` → `discover-cli.sh` → `check-skills.sh`. The order is load-bearing: scaffold creates `<sibling>/audit/` which the discover-cli redirect requires.
> 4. **Then enter the Phase Loop.** Phases 1→10 in `## Phase Loop` below. Each phase has a script-or-subagent invocation, an artifact, and an exit criterion. Don't skip the validation steps — `validate_pass.sh` and `validate_scorecard.sh` are mandatory between phases that produce durable artifacts.
>
> If the user is impatient ("just run it"): pick the deterministic default mode + skip CASS-mining, but always run the pre-flight + intake confirmations. Failing fast on a misconfigured target is far cheaper than salvaging a corrupted audit halfway through Phase 5.

> **In a hurry?** Read **[references/CHEAT-SHEET.md](references/CHEAT-SHEET.md)** — the dense single-page reference (~330 lines) covering everything below.

> **The One Rule.** Design every surface of the CLI so the FIRST thing an agent instinctively tries "just works" — a feel of natural inevitability. When the agent's intent is legible but its command is technically wrong, the tool infers intent, does the right thing (or refuses with a precise, actionable explanation of what to do instead), and leaves a breadcrumb that helps the agent learn permanently. Never silent-fail. Never punish a reasonable misstep. Always provide a safe alternative for any dangerous request. Output is parseable, deterministic, and self-describing.

> **What this skill produces.** Either (a) a thorough **audit-only** scorecard + recommendations for a CLI tool's agent ergonomics, or (b) an **audit + apply + re-score + test** loop that lands the highest-leverage ergonomics fixes in the target repo on a feature branch, with every score, surface, recommendation, applied change, and post-pass simulation persisted as durable, machine-readable artifacts that future agents can re-score against.

---

## What This Skill Is For

You point this skill at a CLI tool repo (Rust, Go, Python, TypeScript, Bash, anything with a binary or entry point a shell can invoke) and ask one of these:

1. *"Audit this CLI for how well it works when an AI agent is the primary user."*
2. *"Score every command, flag, and error message in `<tool>` from 0–1000 across the agent-ergonomics dimensions and tell me what to fix first."*
3. *"Make this CLI feel like the first thing an agent tries actually works — apply the changes."*
4. *"Add `--robot-*` mode, `capabilities --json`, `robot-docs guide` to this tool."*
5. *"Re-run the agent-ergonomics audit on `<tool>` against the changes since the last pass and report uplift."*
6. *"Compare two passes of the audit and tell me which surfaces regressed."*
7. *"Mine my prior agent sessions for examples where this CLI's ergonomics failed me, and prioritize those."*

The skill answers each by routing through the same kernel (the One Rule + the canonical exemplars distilled in [references/exemplars/CANONICAL-EXEMPLARS.md](references/exemplars/CANONICAL-EXEMPLARS.md)), the same operator library ([references/methodology/OPERATORS.md](references/methodology/OPERATORS.md)), the same **eleven-dimension rubric** ([references/rubric/SCORING-RUBRIC.md](references/rubric/SCORING-RUBRIC.md)), and the same **ten-phase loop** that you can re-enter idempotently to drive cumulative uplift across passes.

**Not in scope.** This skill does not redesign the CLI's *features*. It re-shapes the *surface* an agent touches: command/subcommand naming, flag spelling, output format, exit codes, error messages, intent inference, self-documentation, dangerous-op safety, determinism. Feature work (new commands, real new functionality) is filed as beads for follow-up, never silently bundled into an ergonomics pass.

---

## Inputs

- **Target CLI repo path** (default: cwd) — absolute path to a CLI tool's source repo, OR a git URL we should clone into `/tmp/`.
- **Audit workspace path** (default: `<target>__agent_ergonomics_audit/` as a sibling) — auto-detected if it already exists; resumes prior pass.
- **Pass number** (auto-detected from `audit/manifest.json`; first run = `pass 1`).
- **Mode** — `mini` (Phase 1+2 only — scorecard + heatmap, ~5 min) | `audit-only` (no code changes, recs only) | `full` (audit + apply + re-score + tests). See **Mode-default heuristic** below. Use `mini` as a "is this worth committing to?" preview.
- **Tool language(s)** — auto-detected by `scripts/discover-cli.sh` (Rust / Go / Python / TypeScript / Bash / Ruby / Java / etc.); the skill won't install a missing toolchain without explicit user approval.
- **Binary entry points** — auto-detected (Cargo bin, `package.json` bin, Go `cmd/*`, Python `entry_points`, Bash exec scripts). User can override.
- **Triangulation appetite** — `none` | `peer-claude` (two Claude subagents) | `multi-model` (Claude + Codex + Gemini via `/multi-model-triangulation`). Default: `peer-claude` for `audit-only`, `multi-model` for `full` if available.
- **CASS mining appetite** — `skip` | `quick` (10 canned queries) | `deep` (38+ queries against the user's prior agent sessions). Default: `quick` for first pass, `skip` on resumed passes unless surface count changed materially.

## Mode-default heuristic

Compute the default mode deterministically rather than blocking on the user. Compute, then present as: "I'll default to `<MODE>`. Override with `audit-only` / `full` if you'd rather."

First classify explicit user intent; intent wins over the size heuristic:
- If the user asks to "audit", "review", "score", or "report" and does not ask to change code, default to `audit-only`.
- If the user asks to "fix", "improve", "apply", "harden", or make the CLI more agent-friendly, default to `full` subject to the scope guardrails.
- If the user asks "what changed" or "did the changes work?", use `re-score-only` or `simulate-only` when a prior pass exists.

Use the surface-count / prior-pass heuristic below only when the prompt does not already imply a mode.

```
total_surfaces = lines in audit/surface_inventory.jsonl    # from Phase 1, OR
                 (preview-only: scripts/inventory_surfaces.sh <TOOL> | wc -l)
prior_pass     = max(.passes[].pass) from manifest.json    # 0 if first run
last_apply_age = days since last passes[-1].applied_changes_count > 0 commit
                 (∞ if no apply pass yet)

Default = "full"        if total_surfaces ≤ 200 AND prior_pass ≤ 1
        = "full"        if total_surfaces ≤ 500 AND prior_pass == 0
        = "audit-only"  if total_surfaces > 500 (too big for one apply pass)
        = "audit-only"  if prior_pass ≥ 2 AND last_apply_age < 7 days
                        (recent apply; want re-scoring before more changes)
        = "full"        otherwise (resumed pass on aged work)
```

Rationale: small tools benefit most from full apply (quick win, low risk); large tools (gh: 1900+ surfaces, docker: 1100+) need a focused audit-only pass first to identify the highest-leverage 10-20 surfaces before applying. Recently-applied passes shouldn't immediately re-apply — let the change settle and verify uplift first.

The user can override at intake. The full/audit-only choice is also re-evaluated at start of each subsequent pass — passes 1 and 2 might be `full`, pass 3 might switch to `audit-only` once the easy wins are taken.

## Triangulation availability detection

`Triangulation appetite` defaults to `peer-claude` for `audit-only` and `multi-model` for `full` IF the latter is available. To detect availability deterministically:

```bash
have_multi_model=false

# Check 1: is the /multi-model-triangulation skill present?
if jsm list 2>/dev/null | grep -q '^multi-model-triangulation\b'; then
  have_multi_model=true
else
  for skill_root in "$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills" "./.claude/skills"; do
    if [ -d "$skill_root/multi-model-triangulation" ]; then
      have_multi_model=true
      break
    fi
  done
fi

# Check 2: are the underlying CLIs reachable? (the skill needs at least one)
if $have_multi_model; then
  if ! { command -v codex >/dev/null 2>&1 || command -v gemini >/dev/null 2>&1 || command -v grok >/dev/null 2>&1; }; then
    have_multi_model=false  # skill installed but no peer model on PATH
  fi
fi
```

Set `Triangulation appetite=multi-model` only when both checks pass. Otherwise default to `peer-claude` (two parallel Claude subagents — always available since this skill is itself running in Claude Code).

---

## Up-Front Confirmations (Ask Before Starting)

Use the intake template at `assets/intake-prompt.md` verbatim. The summary:

1. **Target CLI path?** Confirm absolute path or clone URL. If GitHub URL, clone to `/tmp/<basename>` first. **Never** clone into a path the user didn't approve.
2. **Sibling audit workspace?** Default name: `<target_basename>__agent_ergonomics_audit/`. Confirm OK to **create the sibling and `git init`** it for storing measurement artifacts. The sibling is the *audit/measurement* workspace; **the actual code changes happen in-tree on a feature branch of the target repo (`agent-ergonomics-pass-N`)**, not in the sibling.
3. **Mode?** `audit-only` (read-only, scoring + recommendations only, no code changes) or `full` (audit + apply + re-score + tests). For narrow tools, recommend `full` — cumulative re-scoring is where the methodology earns its keep. **Default: ask.**
4. **Resuming a prior run?** If `<sibling>/audit/manifest.json` exists, read its `pass` field; offer to start `pass N+1` (preserves all history) or `re-score current pass` (re-runs scoring against the same SHA).
5. **Toolchain consent.** If the target CLI is in a language whose toolchain isn't installed (e.g. Rust target, no `cargo`; Go target, no `go`), ask before installing it. Phase 1 needs to *invoke* the binary, so the toolchain must be present.
6. **Triangulation + CASS appetite** — confirm defaults above.
7. **Scope guardrails.** Confirm the user's "must not touch" list: features they don't want refactored, deprecation policies (e.g. "you may add but never remove"), config files that must remain backwards-compatible, etc. Persisted to `audit/phase0_scope_decision.md`.
8. **Feature branch name** — default `agent-ergonomics-pass-<N>`. Confirm. The branch is created in the **target repo**, not the sibling.

After the user answers, send the matching kickoff prompt from [references/methodology/KICKOFF-PROMPTS.md](references/methodology/KICKOFF-PROMPTS.md) verbatim.

If any helper SKILL referenced here is missing (`/operationalizing-expertise`, `/codebase-archaeology`, `/codebase-report`, `/multi-pass-bug-hunting`, `/multi-model-triangulation`, `/ubs`, `/dcg`, `/agent-mail`, `/beads-br`, `/beads-bv`, `/cass`, `/idea-wizard`, `/gh-cli`, `/cc-hooks`): if the user has `jsm` installed and authenticated, offer to `jsm install <name>` for each missing one. Don't block a phase if a polish skill is missing — note it and proceed with the inline fallback in [references/methodology/SKILL-FALLBACKS.md](references/methodology/SKILL-FALLBACKS.md).

`bun`, `cargo`, `uv`, `gh`, `git`, `jq`, `node` are TOOLCHAINS (binaries on PATH), not skills. Verify they're installed during pre-flight (Phase 0); if missing, instruct the user to install via the platform's package manager (`apt`, `brew`, `cargo install`, etc.). Do NOT attempt `jsm install bun` — `jsm` only ships skills.

---

## Skill Bootstrap (Phase 0.5 — right after inputs, before Phase 1)

**Order matters.** The scaffold creates `<sibling>/audit/`; the discover-cli output gets redirected INTO that directory; both feed check-skills. Run them in this exact order:

```bash
# 1. Create the audit workspace FIRST. Without this, the redirect on step 2
#    has nowhere to land.
./scripts/scaffold-workspace.sh <sibling> <target>
# Creates audit/, audit/regression_tests/, audit/agent_simulations/{pre,post_pass_N},
# audit/partial/, audit/.archive/, tools/, .gitignore (excludes pass-local
# scratch); git init the sibling; writes a populated audit/manifest.json
# seeded with tool_name, tool_repo, audit_workspace, current_pass: 1.

# 2. Run discover-cli, redirect its JSON to the now-existing audit dir.
./scripts/discover-cli.sh <target> > <sibling>/audit/phase0_cli.json
# Detects language, build system, binary entry points, completion-script paths,
# config-file schemas, env-var prefix conventions, embedded man pages.

# 3. Inventory helper skills (jsm state, /agent-mail availability, etc.).
./scripts/check-skills.sh <sibling>/audit
# Writes phase0_skill_inventory.json. Run last because it reads phase0_cli.json
# to decide which language-specific helper skills are relevant.
```

If skills are missing and `jsm` is installed + authenticated:

```bash
./scripts/install-referenced-skills.sh <sibling>/audit
```

If `jsm` isn't installed, offer the official installer (Linux/macOS):

```bash
curl -fsSL https://jeffreys-skills.md/install.sh | bash
```

Then `jsm login`. Requires a paid [jeffreys-skills.md](https://jeffreys-skills.md) subscription to install premium skills. The pipeline degrades gracefully without `jsm` — every helper skill has an inline fallback playbook.

Full bootstrap detail: **[references/methodology/SKILL-FALLBACKS.md](references/methodology/SKILL-FALLBACKS.md)**.

---

## Mode Router

Pick the primary mode first. The phase loop is the same; the **stop conditions and required artifacts** differ.

| Mode | Use when | Must finish with |
|------|----------|------------------|
| `audit-only` | Existing CLI; user wants a scorecard + recommendations only | `agent_surfaces.jsonl`, `scorecard.md`, `heatmap.svg`, `recommendations.jsonl`, `playbook.md`, `agent_simulations/pre/`, `manifest.json` (no code changes; no feature branch) |
| `full` | Existing CLI; user wants the gaps fixed with measurable uplift | everything in `audit-only` + per-recommendation applied changes on `agent-ergonomics-pass-N` branch + `regression_tests/` green + Phase 6 re-score showing uplift + Phase 9 post-pass simulation transcripts |
| `re-score-only` | Resumed run; user wants Phase 2 re-run against the current target HEAD with no other changes | new `scorecard_pass_N+1.md`, `uplift_diff.md`, `regression_alerts.md` for any surface that dropped > 50 points |
| `simulate-only` | Validation run; user wants a fresh-eyes agent to attempt canonical tasks against the current binary | `agent_simulations/post_pass_N/` with full transcripts + per-task pass/fail/round-trip counts |
| `single-surface-rescore` | Targeted; user changed one surface and wants to know the new score | one row appended to `agent_surfaces_pass_N+1.jsonl` for the named `surface_id`; everything else unchanged |

Auto-detect heuristics: `scripts/discover-cli.sh` looks for `audit/manifest.json` (resumed run), `Cargo.toml` / `go.mod` / `package.json` / `pyproject.toml` (language), and a `--robot-*` / `--json` / `capabilities` surface (existing maturity). Picks the mode and shows reasoning; user can override.

**Single-surface guard.** If the user asks for one bounded change (e.g. "just add `--json` to the `list` subcommand"), start in `single-surface-rescore` and only score that one `surface_id`. Escalate to `full` only when the change crosses a shared primitive: error-message format, exit-code contract, or `--help` template.

Full mode definitions, exit criteria, and required artifacts: **[references/methodology/OPERATING-MODES.md](references/methodology/OPERATING-MODES.md)**.

---

## The Phase Loop (Mandatory)

```
Phase 1  SURFACE INVENTORY & ARCHAEOLOGY     enumerate every agent surface (parallel by subcommand)
Phase 2  RUBRIC-DRIVEN SCORING               two scorers per surface + tiebreaker; median + spread
Phase 3  INTENT-INFERENCE STRESS TEST        naive-agent + savvy-agent corpora; corpus_id'd
Phase 4  RECOMMENDATION SYNTHESIS            propose fixes; merge; rank by priority; triangulate top 10
Phase 5  APPLY CHANGES (full mode)           per-recommendation bead; in-tree feature branch; reservations
Phase 6  RE-SCORE & UPLIFT VERIFICATION      regress against pre-pass; flag regressions; loop until quiet
Phase 7  FRESH-EYES BUG & ERGONOMIC REVIEW   the three calibrated prompts; ubs; lint; until clean twice
Phase 8  SELF-DOCUMENTATION HARDENING        ensure capabilities, robot-docs, --robot-*, schema export
Phase 9  AGENT-IN-THE-LOOP VERIFICATION      fresh subagent attempts canonical tasks; transcripts captured
Phase 10 HANDOFF & ITERATION-READINESS       HANDOFF.md, beads for next pass, idea-wizard, push the plane
```

**Phases 4, 5, 6, 7** are *reapply-until-quiet* — keep spawning passes until an entire pass produces only trivial edits (a typo, a comment, no surface scoring change > 25 points). Phase 7's two clean rounds are the explicit termination gate before Phase 8.

**Phase 11 (meta — self-application).** Optional. Apply this very skill to itself or to another Claude Code skill via `subagents/skill-self-applier.md` and `scripts/sw-self-audit.sh`. Use to keep the agent-ergonomics methodology honest: if the skill cannot pass its own polish bar, neither can anything it audits. See [methodology/SELF-APPLICATION.md](references/methodology/SELF-APPLICATION.md).

**Phase 7 fresh-eyes prompts** (use verbatim — they're calibrated):

1. *"Carefully read over all of the new code you just wrote and other existing code you just modified with 'fresh eyes' looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover."*
2. *"Sort of randomly explore the code files in this project, choosing code files to deeply investigate and trace their functionality and execution flows through the related code files which they import or which they are imported by. Once you understand the purpose of the code in the larger context of the workflows, do a super careful, methodical, and critical check with 'fresh eyes' to find any obvious bugs, problems, errors, silly mistakes. Comply with ALL rules in AGENTS.md and ensure that any code you write or revise conforms to the best practice guides referenced in AGENTS.md."*
3. *"Turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues. Diagnose underlying root causes using first-principle analysis. Don't restrict yourself to the latest commits — cast a wider net and go super deep."*

Repeat until two consecutive rounds come up clean except for trivial changes. Then run `ubs` (if available), the project's typecheck/lint/test suite, and the regression tests in `audit/regression_tests/`. Fix everything.

### Termination thresholds (Phase 4/5/6 loop exit criteria)

The loop terminates when ALL of:

- Median absolute uplift in the last pass is **< 25 points** across all surfaces.
- **No surface regressed** by more than 50 points (a regression > 50 is a **hard stop** — investigate before continuing).
- Phase 4 produced no new top-10 recommendation that wasn't a near-duplicate of one already applied.
- Phase 7 fresh-eyes ran clean two times in a row (only trivial edits).

Full per-phase playbook with exit criteria + exact prompts: **[references/methodology/PHASES.md](references/methodology/PHASES.md)** and **[references/methodology/AGENT-PROMPTS.md](references/methodology/AGENT-PROMPTS.md)**.

---

## Parallelism Model

The CLI's surface partitions naturally along subcommand and surface-class boundaries.

```
┌────────────────────────────────────────────────────────────────────────┐
│  PARTITION (Phase 1, by main agent)                                    │
│  ─> recursive --help walk: enumerate top-level subcommands             │
│  ─> assign one surface-inventorist subagent per subcommand subtree     │
│     plus dedicated agents for env vars, exit codes, error corpus,      │
│     completion scripts, config-file schemas, signal handlers           │
└────────────────┬───────────────────────────────────────────────────────┘
                 │
   ┌─────────────┼──────────────┬──────────────┬────────────────────────┐
   ▼             ▼              ▼              ▼                        ▼
┌────────┐  ┌─────────┐    ┌──────────┐   ┌──────────┐           ┌──────────────┐
│ subcmd │  │ subcmd  │    │ env-vars │   │ exit-    │           │ error-msg    │
│ inv. A │  │ inv. B  │ …  │ inv.     │   │ codes    │           │ corpus       │
└───┬────┘  └────┬────┘    └────┬─────┘   └────┬─────┘           └──────┬───────┘
    │            │              │              │                        │
    └────────────┴──────────────┴──────────────┴────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ Phase 2 SCORING          │  ≥2 scorers per surface, median;
                  │ (parallel by surface_id) │  warn at 200, tiebreak at ≥300
                  └──────────────┬───────────┘
                                 ▼
                Phase 3 INTENT STRESS (naive + savvy agents)
                                 ▼
                Phase 4 RECOMMENDATIONS (synthesis + triangulation)
                                 ▼
        Phase 5 APPLY (one bead per recommendation, in-tree branch, reservations)
                                 ▼
                Phase 6 RE-SCORE swarm (parallel by surface_id again)
                                 ▼
                Phase 7 FRESH-EYES swarm (multi-model if available)
                                 ▼
                Phase 9 SIMULATION (fresh agent, canonical tasks)
```

**Coordination.** Use [MCP Agent Mail](../agent-mail/SKILL.md) file reservations whenever a Phase 5 implementer touches a file another implementer is also editing (especially `--help` output strings, error-message catalogs, config schemas, and the canonical output-format module). Thread id: `agent-ergo-<pass>-<phase>-<surface_id>`.

**Orchestration tier** — pick based on tool size:

| Tier | Shape | When |
|------|-------|------|
| Solo | 1 worker, serial phases | Tiny tool, ≤ 5 subcommands, ≤ 30 flags |
| Pair | 2 workers, fan-out only on Phase 1/2/5 | Typical CLI, 6–15 subcommands |
| Squad | 4–6 workers, parallel by subcommand | Full CLI suite, 16–40 subcommands |
| Swarm | 8–12 workers, beads-driven + multi-model triangulation in Phase 4/7 | Multi-binary toolkit (e.g. cargo + cargo-audit + cargo-deny family); ≥ 41 subcommands; rewriting an entire CLI surface |

Triangulation is reserved for Phase 4 (synthesizing top-10 recommendations) and Phase 7 (fresh-eyes), where independent reads produce the highest signal. See **[references/methodology/ORCHESTRATION.md](references/methodology/ORCHESTRATION.md)**.

---

## The Eleven Scoring Dimensions

Every scorable surface ("**agent surface**" — a verb, subcommand, flag, argument, env var, exit code, error message, prompt, interactive confirmation, file format, lockfile, cache directory, signal handler, or side-effect surface) gets a 0–1000 score across each of these eleven dimensions. Rubric anchors at 0/250/500/750/1000 are in **[references/rubric/SCORING-RUBRIC.md](references/rubric/SCORING-RUBRIC.md)** with concrete examples drawn from `dcg`, `bv`, `am`, `ubs`, and `cass`.

| # | Dimension | The question it answers |
|---|-----------|-------------------------|
| 1 | **agent_intuitiveness** | Would the first command an agent guesses succeed, or be redirected with a useful hint? |
| 2 | **agent_ergonomics** | Minimum keystrokes / tool-calls / round-trips to accomplish the canonical task; macros vs. granular composition where relevant. |
| 3 | **agent_ease_of_use** | Discoverability without external docs (`--help`, `capabilities`, self-describing JSON, `robot-docs`). |
| 4 | **output_parseability** | Stable schema, `--json` / `--robot-*` mode, stdout-data / stderr-diagnostics separation, exit-code contract. |
| 5 | **error_pedagogy** | Does the error message teach? Suggest the safe alternative? Cite the exact flag the agent should have used? |
| 6 | **intent_inference** | How gracefully does the tool recover from a legible-but-wrong invocation (typos, deprecated flags, common mis-orderings)? |
| 7 | **safety_with_recovery** | Irreversible operations gated; safe alternatives always offered; reservations / leases / dry-runs available. |
| 8 | **determinism_and_reproducibility** | Stable output ordering, no wall-clock leakage, deterministic IDs, content-addressed where possible. |
| 9 | **self_documentation** | `--help` quality, embedded examples, `capabilities` endpoint, machine-readable schema export. |
| 10 | **composability** | Exit codes / stdout work cleanly in pipelines; no surprise interactive prompts in non-TTY mode; honors `NO_COLOR`, `CI`, `--yes`. |
| 11 | **regression_resistance** | Golden tests, snapshot tests, schema-pinned outputs that protect ergonomics from drift. |

**Threshold rule.** Any score > 700 requires concrete evidence cited in the surface record (file:line for source-defined behavior, or full `--help` excerpt + invocation transcript for runtime-discovered behavior). Scoring without evidence is rejected by `tools/validate_scorecard.sh`.

**Priority** is computed per-surface as: `priority = frequency × score_gap × blast_radius` where `frequency` is "how often agents hit this surface" (estimated from CASS mining + canonical-task usage), `score_gap = 1000 − weighted_avg(dimension_scores)`, and `blast_radius` is "how badly does it stay-bad if unfixed" (rubric in [references/rubric/PRIORITY-FORMULA.md](references/rubric/PRIORITY-FORMULA.md)).

**Recommendation block** (one per below-quartile surface): minimal diff sketch, expected score-after-fix per dimension, risk notes, test additions required.

The rubric and dimension list are **overridable** via `references/rubric/SCORING-RUBRIC.md` (which the skill ships with sensible defaults). Users extend it for their own taxonomy without forking the skill.

---

## The Polish Bar (Non-Negotiable)

Every shipped CLI must satisfy these on its primary surfaces. If a surface fails a dimension, that's a Phase 5 rework target.

| Dimension | Test |
|-----------|------|
| **First-try success** | `<tool>`, `<tool> --help`, `<tool> help <subcmd>` all produce useful output (never a stack trace, never silent exit, never a TUI that blocks an agent). |
| **JSON everywhere** | Every read-side command has `--json` or `--robot-*`. Output schema is documented. Stdout is data-only; stderr is diagnostics-only. |
| **Capabilities endpoint** | `<tool> capabilities --json` returns version, contract version, feature flags, command list, exit-code dictionary, env-var dictionary. |
| **Robot-docs endpoint** | `<tool> robot-docs guide` (and/or `--robot-help`) prints a paste-ready agent-targeted handbook in-tool — no external doc lookup required. |
| **Mega-command** | At least one `<tool> --robot-triage`-style mega-command returns multiple useful slices in a single call (quick_ref + recommendations + commands + health), with copy-paste-ready follow-up commands embedded. |
| **Exit-code contract** | 0 = success, ≥1 = documented categories (1=user-input-error, 2=safety-block, 3=tool-environment-error, …). Never use exit 1 to mean "ran fine, no results." |
| **Error pedagogy** | Every error message names: (a) what failed, (b) where (file:line if applicable), (c) the *exact* flag/command the agent should have used instead. No "see --help" on its own. |
| **Intent inference** | Common typos (`--jsno`, `--jason`), deprecated flag spellings, and mis-orderings either succeed-with-warning or produce a "did you mean" hint with the exact corrected command. |
| **Dangerous-op gating** | Every irreversible operation (delete, force-push, drop, reset, prune) requires explicit `--yes`/`--force`/`--confirm=<token>` AND offers a safe alternative (`--dry-run`, `--plan`) named in the error. |
| **Determinism** | Output ordering is stable (sorted or insertion-order). No raw timestamps in stdout (timestamps belong in JSON fields, not free text). IDs are deterministic where possible. Honors `SOURCE_DATE_EPOCH`. |
| **NO_COLOR / CI / non-TTY** | Tool detects non-TTY and skips ANSI codes, progress bars, interactive prompts. `NO_COLOR=1`, `CI=true`, `--no-color` all suppress styling. |
| **Regression test** | Every applied recommendation lands a golden/snapshot test in `audit/regression_tests/` named after the recommendation ID (`R-NNN__<short_description>`). |

If a surface can't satisfy these, it fails the bar. Full rubric, per-dimension queries, and dispute-resolution flowchart: **[references/methodology/POLISH-BAR.md](references/methodology/POLISH-BAR.md)**.

---

## Cognitive Operators (Agent-Ergonomic Thinking Moves)

Composable moves. Apply to any surface, any error message, any flag-design decision. **The full library is 33 operators** with triggers, failure modes, and prompt modules in **[references/methodology/OPERATORS.md](references/methodology/OPERATORS.md)**. The 17 below are the **most-used core**; OPERATORS.md adds 16 more (Recommended-Action `🪄`, Provenance-Field `🪟`, Schema-Pin `📐`, Doctor-Mode `🩻`, Telemetry-Disable `🔇`, Discovery-Footer `🎯`, Two-Phase-Latency `🪜`, Cross-Verb-Reference `🔗`, Identity-Friction-Collapse `🛂`, Stable-Envelope `📦`, Single-Step-Atomicity `🔬`, Idempotency-Pin `🧷`, Composable-Verbs `🧶`, Bulk-Friendly `🧮`, Drift-Guard `🧾`, Onboarding-Curve `🎓`).

| Glyph | Name | Question | Fix-pointer |
|-------|------|----------|-------------|
| `①` | **First-Try-Inevitability** | "If an agent that's never seen this tool guesses a command, does it work or get a useful redirect?" | Rubric §1, exemplar: `bv --robot-triage` |
| `Σ` | **Mega-Command** | "Can three round-trips collapse into one mega-call returning quick_ref + recommendations + commands?" | Rubric §2, exemplar: `bv --robot-triage` |
| `⟁` | **Intent-Infer-Then-Act** | "If the invocation is wrong but the intent is legible, can we infer-and-warn instead of error-and-stop?" | Rubric §6, exemplar: `dcg explain` |
| `🛡` | **Safe-Alternative-Always** | "For every dangerous op, is there a `--dry-run` / `--plan` / safe-alt named in the error?" | Rubric §7, exemplar: `dcg`'s "use git revert instead" hint |
| `📜` | **Self-Describing** | "Does `<tool> capabilities --json` exist and pin the contract?" | Rubric §9, exemplar: `cass capabilities --json` |
| `📖` | **In-Tool-Docs** | "Does `<tool> robot-docs guide` make external doc lookup unnecessary?" | Rubric §9, exemplar: `cass robot-docs guide` |
| `🚦` | **Exit-Code-Contract** | "Are non-zero exits a documented dictionary, not ad-hoc?" | Rubric §4, exemplar: `ubs` (0=safe, ≥1=fix) |
| `🪧` | **Stdout-Data-Stderr-Diag** | "Does `<tool> X --json | jq …` work without grep-filtering log lines?" | Rubric §4, §10, exemplar: all of `cass`, `bv`, `ubs` |
| `🧪` | **Pin-The-Contract-Test** | "Does this surface have a golden/snapshot test that fails if `--help` text or output schema drifts?" | Rubric §11, exemplar: cass `--robot-meta` schema-pinned |
| `🔀` | **Macros-vs-Granular** | "Is the canonical task a single macro? Is the granular path also exposed for control?" | Rubric §2, exemplar: `am macro_start_session` vs granular `register_agent` |
| `🆔` | **Stable-Handle** | "Does the tool give every artifact a stable, content-addressed handle (project_key, surface_id, request_id)?" | Rubric §8, exemplar: `am` project_key |
| `🩹` | **Error-Teaches** | "Does this error name the *exact* flag the agent should have used?" | Rubric §5, exemplar: `dcg` block message |
| `🚫` | **Never-Silent-Fail** | "If something goes wrong, does the user see *something* on stderr with non-zero exit?" | Rubric §5, §10, exemplar: rejected pattern in [references/exemplars/COUNTER-EXAMPLES.md](references/exemplars/COUNTER-EXAMPLES.md) |
| `⏱` | **Sub-Second-Hot-Path** | "Does the canonical first invocation return in < 1s?" | Rubric §2, exemplar: `dcg` quick-reject filter |
| `🌐` | **Honors-Env-Conventions** | "Does the tool honor `NO_COLOR`, `CI`, `TERM=dumb`, `SOURCE_DATE_EPOCH`, `XDG_*`?" | Rubric §10 |
| `🔢` | **Deterministic-Output** | "Same input → same output bytes? Stable ordering? No timestamp leakage?" | Rubric §8 |
| `🧭` | **Discoverable-From-Help** | "Does `--help` mention `--json`, `capabilities`, `robot-docs`, `--robot-*` modes?" | Rubric §9 |

Composition cheat-sheet (operator pipelines per failing dimension): [references/methodology/OPERATORS.md § Composition](references/methodology/OPERATORS.md).

---

## Audit Workspace Layout (the IO Contract)

```
<target>__agent_ergonomics_audit/
├── audit/
│   ├── manifest.json                              ← entry point: tool, target_sha, pass, paths
│   ├── phase0_scope_decision.md                   ← user's "must not touch" + branch name
│   ├── phase0_skill_inventory.json                ← which helper skills are installed
│   ├── phase0_cli.json                            ← language, build system, binaries detected
│   ├── surface_inventory.jsonl                    ← Phase 1: every agent surface, with surface_id
│   ├── agent_surfaces.jsonl                       ← Phase 2: every surface scored on 11 dims
│   ├── intent_inference_corpus.jsonl              ← Phase 3: wrong invocations + outcomes
│   ├── recommendations.jsonl                      ← Phase 4: ranked recs with applied:bool
│   ├── playbook.md                                ← Phase 4: top-10 narrative
│   ├── applied_changes.jsonl                      ← Phase 5: before/after evidence per change
│   ├── scorecard.md                               ← Phase 2/6: human-readable scorecard
│   ├── scorecard_pass_<N>.md                      ← Phase 6: per-pass historical scorecards
│   ├── heatmap.svg                                ← Phase 2: surfaces × dimensions, hot=low
│   ├── uplift_diff.md                             ← Phase 6: pass-N vs pass-N-1 deltas
│   ├── regression_alerts.md                       ← Phase 6: surfaces that dropped
│   ├── regression_tests/                          ← Phase 5/8: golden/snapshot tests
│   │   ├── R-001__capabilities_json_contract.test.sh
│   │   ├── R-007__exit_code_dictionary.test.sh
│   │   └── …
│   ├── agent_simulations/
│   │   ├── pre_pass_<N>/                          ← Phase 3: baseline transcripts
│   │   │   ├── task-01-<slug>.transcript.jsonl
│   │   │   └── …
│   │   └── post_pass_<N>/                         ← Phase 9: post-fix transcripts
│   │       ├── task-01-<slug>.transcript.jsonl
│   │       └── …
│   └── HANDOFF.md                                 ← Phase 10: queued for next pass
├── tools/                                         ← helper scripts (reusable across passes)
│   ├── rescore_surface.sh
│   ├── diff_scorecards.sh
│   ├── render_heatmap.sh
│   └── replay_simulation.sh
└── .gitignore
```

The target repo also gains:

```
<target>/
└── (on branch agent-ergonomics-pass-<N>)
    ├── (your applied diffs, one bead per recommendation)
    ├── tests/                                     ← golden tests added here too if project has tests/
    └── (no other side files; no V2 / _improved variants — see AGENTS.md)
```

Full per-artifact schema, including JSONL line shapes for `surface_inventory.jsonl`, `agent_surfaces.jsonl`, `recommendations.jsonl`, `applied_changes.jsonl`, and the manifest: **[references/methodology/IO-CONTRACTS.md](references/methodology/IO-CONTRACTS.md)**.

---

## Failure Modes (and Recovery)

| Symptom | Root cause | Recovery |
|---------|------------|----------|
| Phase 1 inventory has < 5 surfaces for a non-trivial CLI | `--help` not invoked recursively; subcommand walk shallow | Re-run with `scripts/inventory_surfaces.sh <tool-binary> --depth=999`; verify against `cargo run -- --help` etc. |
| Phase 2 reconciliation reports many tiebreakers or any escalations | Scorers using different rubric versions or rubric anchors are too loose | Pin `rubric_version` in `manifest.json`; re-score; handle tiebreaker/escalation rows per `references/methodology/RECONCILIATION-POLICY.md` |
| Phase 3 corpus has only "obvious" typos | Naive-agent prompt too constrained | Re-run with full `references/methodology/INTENT-CORPUS-GENERATION.md` prompt; add "savvy" agent pass |
| Phase 4 recommendations contradict each other | No synthesis pass | Run `subagents/synthesizer.md` to merge; resolve contradictions in `playbook.md` |
| Phase 5 applied change broke an existing user workflow | Missing deprecation path | Revert change; file as recommendation requiring `--legacy-<name>` flag with deprecation warning |
| Phase 6 shows a regression > 50 pts | Side-effect of unrelated change | **Hard stop**. Diagnose root cause before continuing. Investigate at `audit/regression_alerts.md`'s cited file:line. |
| Phase 7 fresh-eyes never goes quiet | Loop is touching cosmetic surfaces | Tighten "trivial change" definition: only typo/whitespace counts as trivial; rephrasing IS a change |
| Phase 9 simulation agent gets stuck on canonical task | Real intent-inference gap, not a Phase 3 oversight | File as P0 bead for next pass; **do not** mark Phase 9 complete |
| `--help` walk crashes the binary | Tool segfaults or panics on `--help` after some subcommand | This IS a finding (intuitiveness=0); record as critical; file in beads |
| Tool requires network for `--help` | Bad design (non-deterministic; agents may have no net) | Score 0 on determinism + composability; file as P0 |
| Tool prints to stdout *and* stderr for the same data | Stdout/stderr split violation | Score 0 on output_parseability; flag as Polish Bar fail |

Full failure-mode catalog with recovery scripts: **[references/methodology/TROUBLESHOOTING.md](references/methodology/TROUBLESHOOTING.md)**.

---

## Anti-Patterns (Never Do)

| ✗ | Why | Fix |
|---|-----|-----|
| Score a surface > 700 without evidence | Rubric is meaningless if anchored to vibes | `tools/validate_scorecard.sh` rejects unsourced high scores |
| Apply a change that breaks an existing working surface "to improve ergonomics" | Regression > 50 pts is the single hard-stop trigger | Add a deprecation path: keep old flag, emit warning, ship new flag |
| Write a recommendation without a minimal diff sketch | Phase 5 implementer can't tell intent from a vague "improve error message" | Recommendation block requires diff sketch + expected per-dim uplift + risk + test |
| Pass-1 audit overrides AGENTS.md ("just rm -rf the cache to start clean") | Per AGENTS.md, no destructive ops | Use the repo-approved safe path: inspect, back up, or ask; never stash/revert/delete peer work unless the local AGENTS.md and user explicitly allow it |
| Bundle feature work into an ergonomics pass | Conflates uplift measurement with feature scope | Feature work goes to beads for follow-up; never lands in pass-N |
| Score the same surface twice with different `surface_id` | Cumulative scoring across passes breaks | `surface_id` is content-derived (subcommand + flag + arg-name); use `tools/compute_surface_id.sh` |
| Generate the heatmap before scoring is done | Heatmap colors mislead recommendations | Make heatmap a Phase 2-end artifact, never mid-Phase-2 |
| Land Phase 5 changes without a regression test | The next pass can't tell "fixed" from "regressed-back" | `regression_tests/` is mandatory; `scripts/validate_pass.sh` checks this |
| Run Phase 9 against a simulator agent that has the audit's context | Defeats the purpose of "fresh eyes" | Spawn a fresh subagent (Agent tool, no prior context); record context-isolation in transcript |
| Land changes on `main` of the target repo | Per AGENTS.md and basic git hygiene | Always feature branch `agent-ergonomics-pass-<N>`; merge only with explicit user approval |
| Modify `audit/` files as part of Phase 5 (in-tree) | Audit workspace is the *measurement*; should be untouched by code changes | `audit/` is in the sibling, never in the target repo |
| Treat "no `--robot-*` mode" as a feature gap rather than a finding | The methodology IS to find these gaps | If `--robot-*` is missing, that's a P0 finding scored under self_documentation + output_parseability |

Full anti-pattern catalog: **[references/methodology/ANTI-PATTERNS.md](references/methodology/ANTI-PATTERNS.md)**.

---

## Pre-Flight & End Checklist

- [ ] Target CLI path confirmed; sibling audit workspace named & `git init`-ed
- [ ] Mode confirmed (`audit-only` | `full` | `re-score-only` | `simulate-only` | `single-surface-rescore`)
- [ ] Pass number determined (auto-incremented from manifest if resuming)
- [ ] Helper skills inventoried; missing ones offered via `jsm install` (non-blocking)
- [ ] CLI language + binaries discovered and recorded in `phase0_cli.json`
- [ ] Phase 1 produced `surface_inventory.jsonl` with ≥1 record per `--help` line; spot-check against runtime `--help` output
- [ ] Phase 2 produced `agent_surfaces.jsonl` with median scores + spreads; outliers tiebroken; rubric_version pinned
- [ ] Phase 3 produced `intent_inference_corpus.jsonl` with naive + savvy entries; per-entry outcome classified (silent-fail / useless-error / useful-hint / inferred-and-acted / skipped)
- [ ] Phase 4 produced `recommendations.jsonl` ranked by priority + `playbook.md` for top-10; multi-model triangulation if available
- [ ] Phase 5 (full mode) — feature branch `agent-ergonomics-pass-<N>` exists in target repo; one bead per applied recommendation; reservations via Agent Mail; `applied_changes.jsonl` populated; regression tests added per recommendation
- [ ] Phase 6 — `scorecard_pass_<N+1>.md` shows median uplift ≥ 25 pts AND no surface regressed > 50 pts
- [ ] Phase 7 fresh-eyes ran ≥ 2 times clean; `ubs` clean (if available); typecheck/lint/tests green; `audit/regression_tests/*.test.sh` green
- [ ] Phase 8 — `<tool> capabilities --json`, `<tool> robot-docs guide`, `<tool> --robot-*` for read-side commands all exist (or beads filed for missing ones)
- [ ] Phase 9 — `agent_simulations/post_pass_<N>/` populated with fresh-agent transcripts; per-task pass/fail/round-trip counts recorded
- [ ] Phase 10 — `HANDOFF.md` written; beads filed for queued work; sibling `git push` done; target feature branch pushed (no merge to main without user approval)
- [ ] `audit/manifest.json` updated with new `pass`, `target_sha`, summary stats, artifact list

---

## Reference Index

### Core methodology
| Need | File |
|------|------|
| Mode definitions + exit criteria | [methodology/OPERATING-MODES.md](references/methodology/OPERATING-MODES.md) |
| Per-phase playbook with exit criteria | [methodology/PHASES.md](references/methodology/PHASES.md) |
| Exact prompts for each parallel subagent | [methodology/AGENT-PROMPTS.md](references/methodology/AGENT-PROMPTS.md) |
| Per-mode kickoff prompts (verbatim) | [methodology/KICKOFF-PROMPTS.md](references/methodology/KICKOFF-PROMPTS.md) |
| **33 cognitive operators** (composition cheat-sheet by failing dim) | [methodology/OPERATORS.md](references/methodology/OPERATORS.md) |
| Polish Bar verification queries | [methodology/POLISH-BAR.md](references/methodology/POLISH-BAR.md) |
| Multi-agent orchestration tiers | [methodology/ORCHESTRATION.md](references/methodology/ORCHESTRATION.md) |
| Inline fallbacks for missing skills | [methodology/SKILL-FALLBACKS.md](references/methodology/SKILL-FALLBACKS.md) |
| Multi-model triangulation harness | [methodology/TRIANGULATION.md](references/methodology/TRIANGULATION.md) |
| IO contracts for every JSONL artifact | [methodology/IO-CONTRACTS.md](references/methodology/IO-CONTRACTS.md) |
| Intent-inference corpus generation prompts | [methodology/INTENT-CORPUS-GENERATION.md](references/methodology/INTENT-CORPUS-GENERATION.md) |
| Anti-pattern catalog | [methodology/ANTI-PATTERNS.md](references/methodology/ANTI-PATTERNS.md) |
| Failure-mode + recovery catalog | [methodology/TROUBLESHOOTING.md](references/methodology/TROUBLESHOOTING.md) |

### Implementation cookbooks (the agent-ergonomic uplift content)
| Need | File |
|------|------|
| **Per-language framework recipes** (Rust+clap, Go+cobra, Python+click/typer/argparse, TypeScript+commander/yargs/oclif, Bash, Ruby+thor) — concrete code for adding `--json`/`--robot-*`/`capabilities`/`robot-docs`/typo-correction to every framework | [methodology/LANGUAGE-RECIPES.md](references/methodology/LANGUAGE-RECIPES.md) |
| **Mega-command design library** (TRIAGE / DIAGNOSE / PLAN / CAPABILITIES shapes + JSON schemas + decision tree + per-language scaffolding) | [methodology/MEGA-COMMAND-DESIGN.md](references/methodology/MEGA-COMMAND-DESIGN.md) |
| **Error-message rewriting cookbook** (17 before/after translations: typo, missing arg, destructive op, network failure, lock conflict, etc.) | [methodology/ERROR-REWRITING-COOKBOOK.md](references/methodology/ERROR-REWRITING-COOKBOOK.md) |
| **JSON schema patterns** (universal envelope, meta field, capabilities schema, NDJSON, pagination, schema-pin tests) | [methodology/JSON-SCHEMA-PATTERNS.md](references/methodology/JSON-SCHEMA-PATTERNS.md) |
| **Observability + telemetry surfaces** (log levels, progress bars, NO_COLOR/CI/non-TTY, telemetry opt-out, trace files, crash dumps) | [methodology/OBSERVABILITY-AND-TELEMETRY-SURFACES.md](references/methodology/OBSERVABILITY-AND-TELEMETRY-SURFACES.md) |

### Specialty audits + advanced playbooks
| Need | File |
|------|------|
| **CLI archetype defaults** (15 archetypes: search tool, package manager, build tool, test runner, SCM, daemon, scaffolder, hook tool, issue tracker, etc. — per-archetype dimension weights, mega-command shape, anti-patterns) | [methodology/CLI-ARCHETYPES.md](references/methodology/CLI-ARCHETYPES.md) |
| **MCP server audit extension** (auditing MCP tools, resources, prompts; MCP-CLI parity checks; MCP-specific recommendations) | [methodology/MCP-SERVER-AUDIT.md](references/methodology/MCP-SERVER-AUDIT.md) |
| **Multi-tool family audit** (cargo + cargo-audit + cargo-deny family; cross-cut consistency; family-level recommendations) | [methodology/MULTI-TOOL-FAMILY-AUDIT.md](references/methodology/MULTI-TOOL-FAMILY-AUDIT.md) |
| **Deprecation patterns** (6 patterns for safe breaking changes: rename flag, rename verb, change exit code, change schema, change default, remove feature; staged rollout) | [methodology/DEPRECATION-PATTERNS.md](references/methodology/DEPRECATION-PATTERNS.md) |
| **Schema evolution** (versioning capabilities + tool contracts; contract_version semantics; migration tools; old-version client support) | [methodology/SCHEMA-EVOLUTION.md](references/methodology/SCHEMA-EVOLUTION.md) |

### Continuous improvement + drift guards
| Need | File |
|------|------|
| **Pre-commit drift guards** (cc-hooks / pre-commit / husky / lefthook recipes for capabilities-pin, --help footer, mutating-verb gates, stdout/stderr split) | [methodology/HOOKS-INTEGRATION.md](references/methodology/HOOKS-INTEGRATION.md) |
| **CI integration recipes** (GitHub Actions, GitLab CI workflows for regression_tests + scheduled re-audits; PR-time annotations) | [methodology/CI-INTEGRATION.md](references/methodology/CI-INTEGRATION.md) |
| **Continuous improvement playbook** (PR-time → weekly → monthly → quarterly → annual cadence; metrics timeseries; sunset criteria) | [methodology/CONTINUOUS-IMPROVEMENT.md](references/methodology/CONTINUOUS-IMPROVEMENT.md) |
| **Deep CASS mining recipes** (38+ targeted queries by failure class; per-archetype probe templates; frequency signal extraction) | [methodology/CASS-MINING-RECIPES-DEEP.md](references/methodology/CASS-MINING-RECIPES-DEEP.md) |

### Track A discipline + meta (operationalizing-expertise patterns)
| Need | File |
|------|------|
| **Track A artifact mapping** (this skill IS a Track A artifact: corpus + quote bank + triangulated kernel + operator library + validators; how to extend each) | [methodology/OPERATIONALIZING-EXPERTISE-TRACK-A.md](references/methodology/OPERATIONALIZING-EXPERTISE-TRACK-A.md) |
| **Agent API design first principles** (cognitive load, working memory, retry semantics, no-telepathy, least-surprise-on-failure, graceful degradation, deterministic-by-default, machine-first) | [methodology/AGENT-API-DESIGN-PRINCIPLES.md](references/methodology/AGENT-API-DESIGN-PRINCIPLES.md) |
| **Verification-first discipline** (don't claim a behavior without verifying; per-claim verification protocol; verification log; cross-pass freshness) | [methodology/VERIFICATION-FIRST.md](references/methodology/VERIFICATION-FIRST.md) |
| **Self-application meta-doc** (applying this skill to itself; applying to any Claude Code skill; Track A Level 6) | [methodology/SELF-APPLICATION.md](references/methodology/SELF-APPLICATION.md) |
| **Multi-pass bug-hunting for ergonomics** (audit-fix-rescan cycle applied to ergonomics; the three calibrated prompts; diminishing-returns curve) | [methodology/MULTI-PASS-BUG-HUNTING-FOR-ERGONOMICS.md](references/methodology/MULTI-PASS-BUG-HUNTING-FOR-ERGONOMICS.md) |
| **Worked operator compositions** (6 worked examples: applying 5+ operators to one surface as a single composed recommendation) | [methodology/WORKED-OPERATOR-COMPOSITIONS.md](references/methodology/WORKED-OPERATOR-COMPOSITIONS.md) |
| **Decision trees** (19 decision trees for "what next?" at common audit decision points: mode, tier, archetype, triangulation, defer/apply, operators, termination, verification, family, MCP, deprecation, Phase 9, cheat sheet, NTM, beads, HARD STOP, handoff) | [methodology/DECISION-TREES.md](references/methodology/DECISION-TREES.md) |
| **Failure mode catalog** (8 themes × ~30 failure modes: methodology drift, workflow drift, verification gap, apply failure, subagent confusion, cross-pass coherence, external skill drift, AGENTS.md violations) | [methodology/FAILURE-MODE-CATALOG.md](references/methodology/FAILURE-MODE-CATALOG.md) |
| **Polish Bar deep verification** (per-row jq + bash queries, weighted criticality, when bar can be relaxed) | [methodology/POLISH-BAR-DEEP.md](references/methodology/POLISH-BAR-DEEP.md) |
| **Beads workflow integration** (bead-per-rec, dependency staging, bv triage, mail thread alignment, br sync discipline, deferred work tracking) | [methodology/BEADS-WORKFLOW.md](references/methodology/BEADS-WORKFLOW.md) |
| **NTM + Agent Mail integration** (Squad/Swarm orchestration; spawning audit swarms; reservations; convergence detection; tending the swarm) | [methodology/NTM-AND-AGENT-MAIL-INTEGRATION.md](references/methodology/NTM-AND-AGENT-MAIL-INTEGRATION.md) |
| **Metrics + time series** (per-pass JSONL; cross-pass medians; per-dim trends; sparklines; archetype baselines; dashboard) | [methodology/METRICS-AND-TIMESERIES.md](references/methodology/METRICS-AND-TIMESERIES.md) |
| **TUI-mode audit extension** (gating bare invocation; charmbracelet/ratatui/frankentui patterns; TUI-CLI hybrid architectures) | [methodology/TUI-MODE-AUDIT.md](references/methodology/TUI-MODE-AUDIT.md) |
| **DSL-and-SDK audit** (auditing tools with embedded DSL like jq filters / kubectl JSONPath; auditing library/SDK surfaces; CLI-DSL-SDK alignment) | [methodology/DSL-AND-SDK-AUDIT.md](references/methodology/DSL-AND-SDK-AUDIT.md) |

### Agent profiles + advanced surface types
| Need | File |
|------|------|
| **Agent profiles** (Claude Code, Codex CLI, Gemini, smaller models, IDE-integrated; per-profile rubric weight overrides) | [methodology/AGENT-PROFILES.md](references/methodology/AGENT-PROFILES.md) |
| **Config-as-code patterns** (TOML/YAML config design for agents; schema export, config validate / show / set / get with `--json`; profiles, hierarchical configs, sensitive values) | [methodology/CONFIG-AS-CODE-PATTERNS.md](references/methodology/CONFIG-AS-CODE-PATTERNS.md) |
| **Plugin and extension surfaces** (auditing plugin-aware tools like cargo + cargo-audit; plugin manifests; cross-plugin alignment) | [methodology/PLUGIN-AND-EXTENSION-SURFACES.md](references/methodology/PLUGIN-AND-EXTENSION-SURFACES.md) |
| **Crash recovery and resumability** (long-running ops; idempotency tokens; state files; doctor-aware resume; transactional mutations; heartbeats) | [methodology/CRASH-RECOVERY-AND-RESUMABILITY.md](references/methodology/CRASH-RECOVERY-AND-RESUMABILITY.md) |

### Rubric
| Need | File |
|------|------|
| 11-dimension rubric with 0/250/500/750/1000 anchors | [rubric/SCORING-RUBRIC.md](references/rubric/SCORING-RUBRIC.md) |
| Priority formula (frequency × score_gap × blast_radius) | [rubric/PRIORITY-FORMULA.md](references/rubric/PRIORITY-FORMULA.md) |
| Per-surface-class scoring guidance (verb / flag / env var / exit code / error msg / config / lockfile / signal) | [rubric/SURFACE-CLASSES.md](references/rubric/SURFACE-CLASSES.md) |
| Regression-test patterns per dimension | [rubric/REGRESSION-TEST-PATTERNS.md](references/rubric/REGRESSION-TEST-PATTERNS.md) |
| **Rubric extensions** (per-project additional dims: security, performance, accessibility, internationalization, telemetry transparency, cross-platform consistency, SDK consistency) | [rubric/RUBRIC-EXTENSIONS.md](references/rubric/RUBRIC-EXTENSIONS.md) |

### Exemplars (Track A corpus — the source of truth for "what good looks like")
| Need | File |
|------|------|
| Canonical CLI exemplars distilled (`dcg`, `bv`, `am`, `ubs`, `cass`) — 25 numbered patterns | [exemplars/CANONICAL-EXEMPLARS.md](references/exemplars/CANONICAL-EXEMPLARS.md) |
| Counter-examples (CE-1 to CE-20 — real CLI anti-patterns to recognize) | [exemplars/COUNTER-EXAMPLES.md](references/exemplars/COUNTER-EXAMPLES.md) |
| CASS findings — surprising patterns from prior agent sessions | [exemplars/CASS-FINDINGS.md](references/exemplars/CASS-FINDINGS.md) |
| **Worked end-to-end audits** — Phase-by-phase walkthroughs of dcg / bv / am / ubs / cass + 10 widely-deployed CLIs (jq, ripgrep, gh, kubectl, npm, cargo, ffmpeg, terraform, aws, docker) | [exemplars/WORKED-EXAMPLES.md](references/exemplars/WORKED-EXAMPLES.md) |
| **Canonical task library** — pre-built task corpora per CLI archetype (15 archetypes × 4-5 tasks each) + 8 universal U-Tasks for Phase 9 simulators | [exemplars/CANONICAL-TASK-LIBRARY.md](references/exemplars/CANONICAL-TASK-LIBRARY.md) |
| **Canonical exemplars (deep)** — code-level analysis of dcg/bv/am/ubs/cass with real `--help` excerpts, capabilities snippets, code idioms (quick-reject filter, two-phase analysis, stable handles, provenance fields, recommended-action) | [exemplars/CANONICAL-EXEMPLARS-DEEP.md](references/exemplars/CANONICAL-EXEMPLARS-DEEP.md) |
| **Tier-scoped case studies** — T1 through T5 audit summaries; right-sizing the audit; ROI by tier; common audit shapes per tier | [exemplars/CASE-STUDIES.md](references/exemplars/CASE-STUDIES.md) |

### Source corpus (read-only evidence)
| Need | File |
|------|------|
| Source quote bank (Q-001 … Q-NNN) | [exemplars/QUOTE-BANK.md](references/exemplars/QUOTE-BANK.md) |
| AGENTS.md compliance checklist (live link) | [`AGENTS.md`](../../../AGENTS.md) (from the source corpus, not shipped with this skill) |

---

## Scripts

These run as part of the phase loop. They are reusable across passes; they all read `audit/manifest.json` to know which pass + target they're operating on.

> **Self-documentation contract.** Every script in `scripts/` and `tools/` responds to `--help` (or `-h`) with a clean usage block: synopsis, args, output, exit codes, and an example. The skill practices what it preaches — if you forget the args for any script, just append `--help`. Running with missing required args prints the same usage to stderr and exits 1 (no shell-jargon error, no stack trace).
>
> **`scripts/` vs `tools/`.** Files in `scripts/` are the explicit-arg phase-loop building blocks (every required path is a positional arg). Files in `tools/` are smart wrappers that auto-detect the sibling and current pass from `audit/manifest.json` — typically what you reach for ad-hoc once an audit is underway. Same-named pairs (`scripts/diff_scorecards.sh` / `tools/diff_scorecards.sh`) share behavior; the `tools/` version exec's the `scripts/` one with auto-resolved arguments.

| Script | Purpose |
|--------|---------|
| `scripts/check-skills.sh` | Detect referenced helper skills + jsm state; write `phase0_skill_inventory.json` |
| `scripts/install-referenced-skills.sh` | Bulk-install missing skills via jsm |
| `scripts/discover-cli.sh` | Detect language, build system, binary entry points, completion-script paths, embedded man pages |
| `scripts/scaffold-workspace.sh` | Create `audit/`, `regression_tests/`, `agent_simulations/` etc.; `git init` the sibling |
| `scripts/inventory_surfaces.sh` | Phase 1: recursive `--help` walk; emit `surface_inventory.jsonl` skeleton with surface_ids |
| `scripts/score_surface.sh` | Phase 2 **stub**: emits a placeholder partial JSONL line (all 500s, no evidence) for plumbing tests. Real scoring is LLM-driven via `subagents/scorer.md`; final aggregated rows are produced by `scripts/aggregate_scores.sh`. |
| `scripts/aggregate_scores.sh` | Phase 2: read per-scorer partials and emit final `agent_surfaces.jsonl` rows (median + spread + score_confidence) per IO-CONTRACTS schema |
| `scripts/generate_intent_corpus.sh` | Phase 3: deterministically generates the **naive** corpus (categories A/C/D/G — flag typos, spelling variants, tool-family confusion, env-var typos) from `surface_inventory.jsonl` into `audit/partial/intent_naive.jsonl`, then prints the spawn instruction for the LLM-driven savvy generator (categories H–M; needs source-level evidence). |
| `scripts/run_intent_corpus.sh` | Phase 3: invoke each corpus entry against the binary; classify outcome |
| `scripts/synthesize_recommendations.mjs` | Phase 4: deterministically **merge** recs with identical `diff_sketch` (union surface_ids, max per-dim uplift, max-component priority, shortest title), assign sequential R-NNN IDs, sort by priority desc. For semantic merging where prose differs but intent matches, follow up with `subagents/synthesizer.md`. |
| `scripts/render_heatmap.sh` | Render `agent_surfaces.jsonl` → `heatmap.svg` (surfaces × dims, hot=low) |
| `scripts/render_scorecard.sh` | Render `agent_surfaces.jsonl` → `scorecard.md` |
| `scripts/diff_scorecards.sh` | Compare two passes; emit `uplift_diff.md` + `regression_alerts.md` |
| `scripts/run_simulation.sh` | Phase 3/9 **stub orchestrator**: creates `audit/agent_simulations/<stage>_pass_<N>/` and prints the spawn instruction for `subagents/canonical-task-simulator.md`. The simulator subagent (LLM-driven, fresh context) attempts the canonical tasks and writes the transcripts. |
| `scripts/replay_simulation.sh` | Re-run a captured simulation transcript against the current binary |
| `scripts/validate_pass.sh` | Pre-flight + end checklist enforcement; exits non-zero if checklist incomplete |
| `scripts/manifest_update.sh` | Atomically update `audit/manifest.json` with new artifacts/scores/pass |
| `scripts/extract-known-flags.sh` | Extract canonical KNOWN_FLAGS list from source (Rust+clap, Go+cobra, Python+argparse/click, TS+commander, Bash) — keeps typo-correction in sync |
| `scripts/verify-stdout-stderr-split.sh` | Verify a tool's stdout is data-only and stderr is diagnostics-only |
| `scripts/verify-determinism.sh` | Verify --json output is byte-identical across re-runs (with SOURCE_DATE_EPOCH pinned) |
| `scripts/verify-non-tty-discipline.sh` | Verify NO_COLOR / CI=true / TERM=dumb / piped-stdout are honored; no prompts in non-TTY |
| `scripts/build-canonical-tasks.sh` | Generate audit/canonical_tasks.md for Phase 9 simulator from archetype + library |
| `scripts/sw-self-audit.sh` | Self-audit any Claude Code skill against the agent-ergonomics methodology |
| `scripts/measure-help-readtime.sh` | Estimate agent reading time for `--help` (lines + tokens + structural signals) |
| `scripts/audit-readme-vs-help.sh` | Detect README → `--help` drift (commands documented but missing; or vice versa) |

Each script either writes its documented phase artifact or emits documented stdout for redirection. JSON-only behavior is called out per script. All scripts honor `NO_COLOR`, exit 0 on success, ≥1 on failure with a stderr error message naming the next remediation step. The skill practices what it preaches.

## Tools (per-workspace utilities; reusable across passes)

| Tool | Purpose |
|------|---------|
| `tools/rescore_surface.sh <surface_id>` | Re-run Phase 2 scoring for one surface; useful after a targeted change |
| `tools/diff_scorecards.sh [sibling-dir]` | Print per-dimension delta table; auto-detects sibling + reads `current_pass` from manifest, diffs `(current_pass - 1)` → `current_pass`. For non-adjacent passes use `scripts/diff_scorecards.sh` directly. |
| `tools/render_heatmap.sh [sibling-dir] [pass]` | Render heatmap for the given pass (defaults to `current_pass`); writes `audit/heatmap.svg` |
| `tools/replay_simulation.sh <task-slug-or-id> [sibling-dir]` | Replay a captured Phase 9 simulation transcript against the current binary |
| `tools/compute_surface_id.sh <kind> [<subtree>] <name>` | Compute deterministic surface_id from descriptor (used by validators) |
| `tools/validate_scorecard.sh <agent_surfaces.jsonl>` | Reject scorecards with > 700 scores lacking evidence; also enforces `score_confidence` + `scored_at` per IO-CONTRACTS |
| `tools/flip_applied.sh <RECOMMENDATION_ID> [<COMMIT_SHA>] [<sibling>]` | Flip a recommendation's `applied` to `true` in `audit/recommendations.jsonl` (concurrent-safe via flock); used by `applier.md` Step 8 |

---

## Subagents

| Subagent | Phase | Purpose |
|----------|-------|---------|
| `subagents/cass-miner.md` | 0 | Mines user's prior cass sessions for tool-specific ergonomic complaints |
| `subagents/surface-inventorist.md` | 1 | Walks one subcommand subtree; emits surface records with citations |
| `subagents/scorer.md` | 2 | Scores one surface across all 11 dimensions with evidence |
| `subagents/scorer-tiebreaker.md` | 2 | Resolves per-dim spreads ≥ 300 between two scorers |
| `subagents/intent-stresser-naive.md` | 3 | Generates wrong invocations using only `--help` access (no source) |
| `subagents/intent-stresser-savvy.md` | 3 | Generates wrong invocations with full source access |
| `subagents/intent-runner.md` | 3 | Invokes each corpus entry; classifies outcome (silent-fail / useless-error / useful-hint / inferred-and-acted / skipped) |
| `subagents/recommender.md` | 4 | Proposes recommended_fix blocks for below-quartile surfaces |
| `subagents/synthesizer.md` | 4 | Merges overlapping recs, removes contradictions, ranks by priority |
| `subagents/triangulator.md` | 4 / 7 | Multi-model verification (Claude + Codex + Gemini) for top recs |
| `subagents/applier.md` | 5 | Implements one recommendation on the target's feature branch |
| `subagents/regression-test-author.md` | 5 / 8 | Writes the golden/snapshot test that pins the recommendation |
| `subagents/re-scorer.md` | 6 | Re-runs Phase 2 against the post-apply binary; computes uplift |
| `subagents/fresh-eyes.md` | 7 | Generic fresh-eyes review using the three calibrated prompts |
| `subagents/self-doc-hardener.md` | 8 | Adds missing `capabilities`, `robot-docs`, `--robot-*` surfaces |
| `subagents/canonical-task-simulator.md` | 9 | Fresh-context agent attempts canonical tasks against the binary; emits transcript |
| `subagents/handoff-writer.md` | 10 | Writes `HANDOFF.md` for the next pass |
| `subagents/idea-generator.md` | 10 | Surfaces second-order ergonomic improvements via `/idea-wizard` |
| `subagents/cli-archetype-classifier.md` | 0 | Classifies target CLI into archetype(s); picks dimension-weight overrides + canonical-task corpus |
| `subagents/parity-auditor.md` | 1 / 4 | For tools with both MCP server + CLI; audits MCP-CLI parity; files parity-gap recs |
| `subagents/family-cross-cut-auditor.md` | 1 / 4 | For multi-tool families; cross-cut consistency dimensions; family-level recs |
| `subagents/migration-planner.md` | 4 / 5 | Plans deprecation rollouts; sequences stages 0→1→2→3 across passes; produces migration scripts |
| `subagents/canonical-task-author.md` | 0 | Generates canonical task definitions from archetype + README + CASS for Phase 9 simulator |
| `subagents/skill-self-applier.md` | 11 (meta) | Applies this skill to itself or to other Claude Code skills |
| `subagents/cheat-sheet-builder.md` | 8 / 10 | Generates project-specific CHEAT-SHEET.md / agent quickref tailored to the audited tool |
| `subagents/benchmark-collector.md` | 10 | Appends per-pass metrics to `audit/metrics_timeseries.jsonl`; renders `metrics_timeseries.md` |
| `subagents/decision-tree-walker.md` | (helper) | Walks DECISION-TREES.md trees deterministically; returns "what next?" recommendations |

## Subagent spawn-args reference

When the main agent spawns a subagent via the Agent tool, it MUST pass these required arguments verbatim in the prompt's "Inputs" section. Args not listed here are filled by the subagent from sources stated in its own `## Inputs` block (e.g., reading `<SIBLING>/audit/manifest.json` for `<PASS>`).

| Subagent | Required spawn args |
|---|---|
| `applier` | `<RECOMMENDATION_ID>` `<SIBLING>` `<TARGET>` `<TARGET_SHA>` `<FEATURE_BRANCH>` |
| `benchmark-collector` | `<SIBLING>` `<N>` (pass number) |
| `canonical-task-author` | `<SIBLING>` `<TARGET>` |
| `canonical-task-simulator` | `<TOOL>` `<PASS>` `<TASK_LIST>` `<TRANSCRIPT_DIR>` `<SIBLING>` `<N>` |
| `cass-miner` | `<TOOL>` `<SIBLING>` |
| `cheat-sheet-builder` | `<SIBLING>` |
| `cli-archetype-classifier` | `<TARGET>` `<SIBLING>` |
| `decision-tree-walker` | `<DECISION_POINT>` `<SIBLING>` |
| `family-cross-cut-auditor` | `<SIBLING>` |
| `fresh-eyes` | `<TARGET>` `<SIBLING>` |
| `handoff-writer` | `<SIBLING>` `<N>` |
| `idea-generator` | `<TOOL>` `<SIBLING>` |
| `intent-runner` | `<TOOL>` `<SIBLING>` |
| `intent-stresser-naive` | `<TOOL>` |
| `intent-stresser-savvy` | `<TOOL>` `<TARGET_SHA>` `<SIBLING>` |
| `migration-planner` | `<SIBLING>` |
| `parity-auditor` | `<TARGET>` `<SIBLING>` |
| `recommender` | `<SURFACE_ID>` `<SIBLING>` |
| `regression-test-author` | `<RECOMMENDATION_ID>` `<TARGET>` `<POST_APPLY_BINARY>` `<SIBLING>` |
| `re-scorer` | `<SURFACE_ID>` `<TARGET_SHA>` `<RUBRIC_VERSION>` `<SIBLING>` |
| `scorer` | `<SURFACE_ID>` `<SCORER_ID>` `<TARGET_SHA>` `<RUBRIC_VERSION>` `<PASS>` `<SIBLING>` |
| `scorer-tiebreaker` | `<SURFACE_ID>` `<DIMENSION>` `<PASS>` `<SIBLING>` |
| `self-doc-hardener` | `<TOOL>` `<TARGET>` `<SIBLING>` |
| `skill-self-applier` | `<TARGET_SKILL>` `<SIBLING>` |
| `surface-inventorist` | `<TOOL>` `<SUBTREE>` `<TARGET_SHA>` `<SIBLING>` |
| `synthesizer` | `<SIBLING>` |
| `triangulator` | `<SUBJECT>` `<TARGET>` `<TRIANGULATION_ID>` `<SIBLING>` |

**Spawn pattern (parallel subagents).** When a phase calls for multiple subagents to run in parallel (e.g. Phase 2 spawns scorer-A + scorer-B for the same surface), invoke the Agent tool with **multiple tool-use blocks in a single message** — Claude Code runs them concurrently. Don't spawn them sequentially across multiple turns; that loses the parallelism the phase budget assumes.

## Assets

| Asset | Purpose |
|-------|---------|
| `assets/intake-prompt.md` | Use at very start of skill invocation to gather inputs |
| `assets/manifest-template.json` | Initial `audit/manifest.json` structure |
| `assets/surface-record-template.jsonl` | One-line example for `surface_inventory.jsonl` / `agent_surfaces.jsonl` |
| `assets/recommendation-template.jsonl` | One-line example for `recommendations.jsonl` |
| `assets/applied-change-template.jsonl` | One-line example for `applied_changes.jsonl` |
| `assets/scorecard-template.md` | Markdown template for human-readable scorecard |
| `assets/handoff-template.md` | Template for `HANDOFF.md` |
| `assets/regression-test-template.sh` | Template for golden/snapshot test in `audit/regression_tests/` |
| `assets/canonical-task-template.md` | Template for a Phase 9 canonical-task definition |

---

## Self-Test

Trigger phrases that should activate this skill:

- "Audit this CLI for agent ergonomics"
- "Make `<tool>` agent-friendly"
- "Score `<tool>` for how usable it is by an AI agent"
- "Add a `--robot-*` mode to my CLI"
- "Add `capabilities --json` and `robot-docs` to this tool"
- "Why does an agent always pick the wrong flag for `<tool>` — fix the intent inference"
- "Re-run the agent-ergonomics audit on `<tool>` and tell me which surfaces regressed"
- "Compare the pre-pass and post-pass agent simulations and tell me what got better"
- "Mine my prior agent sessions for places where this CLI's error messages didn't teach me anything, and prioritize those"
- "Build me a scorecard with a heatmap of every flag and exit code in this binary"
- "First command an agent tries should just work — make it so for `<tool>`"

Trigger-phrase probe + smoke test on a tiny CLI: [SELF-TEST.md](SELF-TEST.md).
