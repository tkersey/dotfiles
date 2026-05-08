# SKILL-FALLBACKS — Inline replacements for missing helper skills

The skill composes many helper skills. If `jsm` isn't installed or the user doesn't have a subscription, the pipeline degrades gracefully — every helper skill has an inline fallback playbook below.

`scripts/check-skills.sh` outputs `phase0_skill_inventory.json` with `present:bool` per skill; if `present:false`, this file's playbook is the substitute.

---

## Skill creation / validation → fallback

Use this skill's own `references/` directory as the template. The minimum scaffold for a child skill is:

- `SKILL.md` with frontmatter (`name`, `description`, `Use when` triggers, durable artifact paths)
- `SELF-TEST.md` with trigger probes
- `references/methodology/PHASES.md` with phase loop
- `assets/intake-prompt.md`

Validation checks to run manually:
- `head -10 SKILL.md | grep -E '^name:|^description:'`
- `for f in references/**/*.md; do test -f "$f" || echo MISSING $f; done`
- `for s in scripts/*.sh; do [ ! -x "$s" ] && echo NOT_EXEC $s; done`

See SELF-TEST.md. Skip if not extending the skill itself.

---

## `/operationalizing-expertise` → fallback

The skill IS a Track A artifact already. The corpus is `references/exemplars/CANONICAL-EXEMPLARS.md` + `CASS-FINDINGS.md` + `QUOTE-BANK.md`. The triangulated kernel is the One Rule + the 11 dimensions. The operator library is `OPERATORS.md`. The validators are `tools/validate_scorecard.sh` + the regression tests.

If you want to extend the corpus: add a quote to QUOTE-BANK.md with a `[Q-NNN]` ID, propose a kernel addition (rare), or add a new operator card.

---

## `/codebase-archaeology` → fallback

If `/codebase-archaeology` is missing, use `/codebase-report` patterns inline:

1. List the source root: `find <target> -name 'Cargo.toml' -o -name 'go.mod' -o -name 'package.json' -o -name 'pyproject.toml' -o -name 'setup.py'`
2. Identify entry points: read each manifest's `[[bin]]` / `cmd/*` / `bin` / `entry_points`.
3. For Rust: `cargo run -- --help` then walk every clap subcommand.
4. For Go: read `cmd/*/main.go`; cobra command tree.
5. For Python: read `argparse` / `click` / `typer` decorators; trace `os.environ.get`.
6. For TypeScript: read `commander` / `yargs` / `oclif` definitions; trace `process.env`.
7. For Bash: parse `case "$1" in ...`; `getopts` invocations.

Output: a one-paragraph summary of the tool's architecture saved to `audit/phase1_archaeology.md`.

---

## `/codebase-report` → fallback

For Phase 1 archaeology: build a per-subtree summary covering:
- entry point file:line
- subcommand list with their files
- shared modules (config, env, output formatting, error types)
- which files own --help text
- which files own JSON serialization
- exit-code sites

Append to `audit/phase1_archaeology.md`.

---

## `/multi-pass-bug-hunting` → fallback

Phase 7 fresh-eyes prompts are calibrated. Use them verbatim from `PHASES.md § Phase 7`. Repeat until two clean rounds.

---

## `/multi-model-triangulation` → fallback

If `/multi-model-triangulation` isn't available, use **peer-claude** instead: spawn two distinct Claude subagents via the Agent tool with different `subagent_type`s (e.g. `general-purpose` + `Explore`) and reconcile their findings. Catches a surprising fraction of single-model blind spots.

---

## `/ubs` → fallback

If `ubs` binary isn't installed: skip the UBS pass. Run the project's native linter / typechecker / security scanner instead:
- Rust: `cargo clippy --all-targets -- -D warnings`
- Go: `go vet ./...; staticcheck ./...; golangci-lint run`
- Python: `ruff check .; mypy .`
- TypeScript: `tsc --noEmit; eslint .`
- Bash: `shellcheck *.sh`

Phase 7 termination requires these to be green.

---

## `/dcg` → fallback

dcg is the canonical example of agent-ergonomic safety. If `dcg` isn't installed for the user, the skill still references its patterns in CANONICAL-EXEMPLARS.md and applies them to the target tool's dangerous-op surfaces.

---

## `/agent-mail` → fallback

Without Agent Mail, file-reservation coordination becomes manual:

- Solo / Pair tier: skip reservations; serialize work on shared files.
- Squad / Swarm tier: use a simple flat-file lock convention: `audit/.locks/<surface_id>.lock` (write your subagent ID; check before editing; remove when done).

---

## `/beads-br` (beads_rust) → fallback

Without `br`, track recommendations in `recommendations.jsonl` only (no separate bead store). The applier subagent cites the recommendation_id in commit messages instead of a bead ID. HANDOFF.md lists deferred recs by `recommendation_id`.

For Phase 10 land-the-plane, replace `br sync --flush-only` with a no-op; commit the audit workspace + target feature branch directly.

---

## `/beads-bv` → fallback

Without `bv`, skip the graph-aware triage step. The synthesizer's priority ranking (frequency × score_gap × blast_radius) does the work `bv` would do automatically.

---

## `/cass` → fallback

Without `cass`, set CASS appetite to `skip`. Document in `audit/phase0_scope_decision.md` that CASS findings are unavailable; rely entirely on the rubric + intent corpus.

If the user has `cass` but doesn't have rich session history (fresh user, fewer than ~30 sessions), the `quick` queries will produce thin results — that's fine. Stick with rubric-driven scoring.

---

## `/idea-wizard` → fallback

For Phase 10 second-order improvements: spawn a fresh subagent with this prompt:

```
You are an idea generator. The audit at <SIBLING>/audit/ is complete for Pass <N>. Read HANDOFF.md, scorecard.md, and the top-10 playbook.md.

Brainstorm 5 second-order improvements that the rubric didn't surface — things that would make the tool feel inevitable to use, beyond the dimensions we've already scored.

Don't propose features. Propose ergonomic moves: new shortcuts, new compositions, deprecation paths for legacy verbs, schema changes that improve introspection.

Output: 5 numbered ideas. Each idea: (a) one-sentence statement, (b) which dimension(s) it would lift, (c) estimated uplift in points.
```

File the top 2–3 as supplementary recommendations for next pass.

---

## `/bun`, `/cargo`, `/uv`, `/gh`, `/gh-cli`, `/cc-hooks` → fallbacks

These are toolchain skills. If missing, use the underlying tool directly; the skill doesn't strictly need them. Note in `phase0_scope_decision.md` if any are missing so future agents know.

---

## When fallbacks aren't enough

If a *critical* skill is missing AND the inline fallback can't substitute (e.g. you're trying to triangulate but `/multi-model-triangulation` is missing AND peer-claude isn't an acceptable substitute for stakes reasons), pause and ask the user:

1. Install the skill via `jsm install <name>`?
2. Proceed with the inline fallback (lower-quality but unblocked)?
3. Skip this pass step entirely (mark as `n/a` in HANDOFF.md)?

Default to option 2 if the user doesn't say.
