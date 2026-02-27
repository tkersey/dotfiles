---
name: codex-upcoming-features
description: Fetch and summarize upcoming unreleased Codex features using a durable local clone synced from GitHub, with source-file mining as primary evidence. Use when asked for latest upcoming/openai-codex features, what is coming next but not in the latest stable release, or a live release-gap summary with links and as-of timestamp.
---

# Codex Upcoming Features

## Overview

Sync a durable local clone of `openai/codex` and produce an exhaustive summary of unreleased features and notable improvements since the latest stable (non-prerelease) release tag.

Primary evidence comes from source files that define feature stages and user-facing metadata. Commit/PR analysis is secondary supporting context.

## Workflow

1. Run `gh auth status` and fail closed if GitHub CLI is not authenticated.
2. Resolve durable local clone path:
- default: `$CODEX_HOME/repos/<owner>-<repo>` (fallback: `~/.codex/repos/<owner>-<repo>`)
- override: `--local-repo <path>`
3. If clone is missing, clone from `https://github.com/<owner>/<repo>.git`.
4. Sync local clone on every run (`git fetch --tags --prune origin`, checkout default branch, `git pull --ff-only`).
5. Mine these source files on every run (fail closed if missing):
- `codex-rs/core/src/features.rs`
- `codex-rs/tui/src/chatwidget.rs`
- `codex-rs/core/src/codex.rs`
- `codex-rs/app-server/src/codex_message_processor.rs`
- `codex-rs/app-server-protocol/src/protocol/v2.rs`
- `codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json`
- `codex-rs/app-server/README.md`
- `codex-rs/tui/src/tooltips.rs`
- `announcement_tip.toml`
6. Extract source-derived upcoming feature data from `features.rs`:
- `Stage::Experimental` (beta/user-facing now)
- `Stage::UnderDevelopment` (upcoming but not broadly ready)
- include `name`, `menu_description`, and `announcement` where available
7. Extract structured supporting evidence from each other mined source file (UI wiring, app-server mapping, protocol enum/schema, docs contract, tooltip/announcement pipeline).
8. Record analyzed commit SHA from synced local clone (`git rev-parse HEAD`) and include it in output.
9. Resolve repo default branch and latest stable release tag (exclude draft/prerelease).
10. Compute unreleased range from local git history: `stable_tag..origin/default_branch`.
11. Classify each unreleased commit into one of:
- `feature`
- `notable_improvement`
12. Exclude entries that are clearly non-user-impacting (for example docs/chore/test-only).
13. Emit an exhaustive report with:
- UTC as-of timestamp
- local repo path used
- analyzed commit SHA
- stable baseline tag and compare link
- source files mined
- source-derived feature list (primary)
- cross-file source evidence (primary)
- per-item PR/commit evidence links

## Commands

Run markdown summary (default):

```bash
uv run python scripts/summarize_upcoming.py --repo openai/codex
```

Run JSON output:

```bash
uv run python scripts/summarize_upcoming.py --repo openai/codex --output json
```

Override baseline tag if needed:

```bash
uv run python scripts/summarize_upcoming.py --repo openai/codex --base-tag rust-v0.106.0
```

Override durable local clone path:

```bash
uv run python scripts/summarize_upcoming.py --repo openai/codex --local-repo ~/workspace/cache/openai-codex
```

## Output Contract

Always include:
- `As of (UTC)` timestamp
- local repo path used for summarization
- analyzed commit SHA
- `Stable baseline` tag
- compare URL
- source files mined
- source-derived upcoming feature sections (`beta` + `underDevelopment`)
- source-derived cross-file evidence section covering all required files
- exhaustive list of included items
- source links for each item

When there is a conflict between source-derived feature data and commit text, source-derived data wins.

JSON mode returns:
- `as_of_utc`
- `repo`
- `local_repo`
- `analyzed_commit_sha`
- `stable_tag`
- `compare_url`
- `source_files_mined[]`
- `source_primary.beta_features[]` and `source_primary.under_development_features[]`
- `source_primary.supporting_evidence` (structured extraction for every required source file)
- `items[]` with `kind`, `title`, `commit_sha`, `commit_url`, `pr_number`, `pr_url` (secondary)

## Classification Rules

Read [references/classification-rules.md](references/classification-rules.md) before changing filtering behavior. Keep inclusion deterministic and biased toward user-visible changes.

## Guardrails

- Do not use stale local commit snapshots; clone if missing and sync (fetch/pull) on every run.
- Fail closed if local repo origin does not match the requested `owner/repo`.
- Keep release resolution live (GitHub API), source feature extraction local (from mined files), and commit extraction local (synced git history).
- Treat commit messages as supporting evidence only; never treat commits as primary feature truth when source files disagree.
- Do not infer future roadmap from open issues or open PRs in this skill version.
- Fail closed with actionable errors when API/auth/rate-limit calls fail.
