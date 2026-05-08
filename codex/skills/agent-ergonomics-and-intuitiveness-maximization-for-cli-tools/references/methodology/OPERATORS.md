# OPERATORS — Cognitive Moves for Agent-Ergonomic Work

Composable cognitive moves. Each operator is a question that, if it fails, names a section to fix. Apply them to any surface, any error message, any flag-design decision. Operators overlap deliberately — a single `--help` line typically deserves three or four.

Adapted from `/operationalizing-expertise` Track A. The point is to reduce "improve this CLI" into "apply these 5 operators to these surfaces." Dramatically more reproducible than vibes-based editing.

---

## Card 01 — `①` First-Try-Inevitability

**Question.** "If an agent that's never seen this tool guesses a command, does it work or get a useful redirect?"

**Trigger.** Phase 1 surface inventory; reviewing top-level subcommand naming; reviewing the bare invocation (`<tool>` with no args).

**Failure modes.**
- Bare `<tool>` launches a TUI that blocks an automated agent.
- Bare `<tool>` exits 0 with no output (silent_fail).
- `<tool> help` prints `<tool>: command 'help' not found`. (Should redirect to `--help`.)
- `<tool> ls` doesn't redirect to `<tool> list`.

**Fix-pointer.** Rubric §1 (agent_intuitiveness). Exemplar: `bv --robot-triage`. Counter-example: bare `bv` launches a TUI that blocks Claude Code.

**Prompt module.**
> Imagine you've never seen this tool before. Without reading docs, what would you type to start? Now what would you type if your first guess didn't work? What about your third guess? At what point does the tool start helping you? If "never," that's a finding.

---

## Card 02 — `Σ` Mega-Command

**Question.** "Can three round-trips collapse into one mega-call returning quick_ref + recommendations + commands?"

**Trigger.** Reviewing read-side verbs that an agent typically chains.

**Failure modes.**
- Agent must call `<tool> status`, then `<tool> list`, then `<tool> next` to plan a session.
- The mega-call exists but doesn't include copy-paste-ready commands for next steps.
- The mega-call returns data but the data isn't actionable without further parsing.

**Fix-pointer.** Rubric §2 (agent_ergonomics). Exemplar: `bv --robot-triage` returns `quick_ref` + `recommendations` + `quick_wins` + `blockers_to_clear` + `project_health` + `commands` (copy-paste-ready) in one call. Same idea: `cass capabilities --json` collapses "what version, what features, what limits" into one read.

**Prompt module.**
> What's the canonical agent task for this tool? List the 3+ commands an agent runs to complete it. Can they collapse into one mega-command that returns all the slices the agent needs? If yes, propose the mega-command's JSON shape.

---

## Card 03 — `⟁` Intent-Infer-Then-Act

**Question.** "If the invocation is wrong but the intent is legible, can we infer-and-warn instead of error-and-stop?"

**Trigger.** Reviewing error messages, deprecated flag handling, alias support.

**Failure modes.**
- `<tool> --jsno` errors with "unknown flag --jsno" without suggesting `--json`.
- `<tool> ls` errors with "unknown command ls" instead of running `list` (with a one-line warning).
- Deprecated flag spelling errors out instead of warning + proceeding.

**Fix-pointer.** Rubric §6 (intent_inference). Exemplar: `dcg explain` interprets the agent's intent on a blocked command and explains what to use instead. Pattern: levenshtein-distance-1 typo → "did you mean X?" hint AND if confidence is high enough, just proceed-with-warning.

**Prompt module.**
> Pick three plausibly-wrong invocations of this surface (a typo, a wrong subcommand order, a deprecated spelling). For each: does the tool infer-and-act, give a useful hint, give a useless error, or silent-fail? Anything below "useful hint" is a finding.

---

## Card 04 — `🛡` Safe-Alternative-Always

**Question.** "For every dangerous op, is there a `--dry-run` / `--plan` / safe-alt named in the error?"

**Trigger.** Reviewing any verb that mutates state (delete, drop, prune, reset, force-push, kill).

**Failure modes.**
- Destructive op runs immediately on first invocation.
- Destructive op requires `--force` but doesn't suggest `--dry-run` first.
- Error message blocks the op without naming the safe alternative ("use `git revert` instead of `git reset --hard`" — say that explicitly).

**Fix-pointer.** Rubric §7 (safety_with_recovery). Exemplar: `dcg` block messages always name a safe alternative (e.g. "use git stash; or git revert; or backup first"). Exemplar: `am file_reservation_paths` (advisory leases instead of locks).

**Prompt module.**
> List every verb in this CLI that mutates state. For each: is there a `--dry-run`? A `--plan`? A `--yes`-required gate? Does the error message (when it blocks) name the safe alternative? Anything missing is a finding.

---

## Card 05 — `📜` Self-Describing

**Question.** "Does `<tool> capabilities --json` exist and pin the contract?"

**Trigger.** Reviewing whether an agent can introspect the tool without external docs.

**Failure modes.**
- No `capabilities` endpoint.
- `capabilities` exists but doesn't include version, contract_version, features, exit codes, env vars.
- `capabilities` JSON has no schema; consumers can't validate.

**Fix-pointer.** Rubric §9 (self_documentation). Exemplar: `cass capabilities --json` returns crate_version, api_version, contract_version, features, connectors, limits.

**Prompt module.**
> Pretend you're an agent that needs to know what this tool can do without reading any docs. Run `<tool> capabilities --json`. Does the result tell you everything you need (version, features, limits, exit codes, env vars)? If anything is missing or in prose-only `--help` text, that's a finding.

---

## Card 06 — `📖` In-Tool-Docs

**Question.** "Does `<tool> robot-docs guide` make external doc lookup unnecessary?"

**Trigger.** Reviewing whether the agent can complete the canonical task using only the tool's own surfaces.

**Failure modes.**
- No in-tool agent handbook.
- `--help` is the only docs and is too long / too short.
- Agent must read README.md to know how to use `--robot-*` mode.

**Fix-pointer.** Rubric §9. Exemplar: `cass robot-docs guide` returns a paste-ready agent handbook in-tool with output formats, search contracts, default modes, doctor branches, safety hints.

**Prompt module.**
> Run `<tool> robot-docs guide` (or `--robot-help`). Could a fresh agent complete the canonical task using only this output, plus `--help` for specific verbs? If they need to read the README, that's a finding.

---

## Card 07 — `🚦` Exit-Code-Contract

**Question.** "Are non-zero exits a documented dictionary, not ad-hoc?"

**Trigger.** Reviewing the exit-code corpus from Phase 1; reviewing pipeline composability.

**Failure modes.**
- Tool uses exit 1 to mean BOTH "user input error" AND "ran fine, no results."
- Exit codes aren't documented anywhere except in source.
- Tool prints to stdout AND exits non-zero (mixed signals).

**Fix-pointer.** Rubric §4 (output_parseability). Exemplar: `ubs` exit 0 = safe, ≥1 = fix; documented in `--help`. Exemplar: `dcg` exit 0 = allowed, exit 2 = blocked (Codex-compatible).

**Prompt module.**
> List every exit-code site in the source. Group by exit value. For each group: what's the contract? Is it documented? Does any value mean "different things in different contexts"? Anything ad-hoc is a finding.

---

## Card 08 — `🪧` Stdout-Data-Stderr-Diag

**Question.** "Does `<tool> X --json | jq …` work without grep-filtering log lines?"

**Trigger.** Reviewing read-side verbs; reviewing pipeline composability.

**Failure modes.**
- Tool prints log lines and JSON output to the same stream.
- `--verbose` adds log lines that contaminate stdout.
- Errors print to stdout instead of stderr.

**Fix-pointer.** Rubric §4 + §10. Exemplar: `cass` "stdout is data-only, stderr is diagnostics; exit code 0 means success." All major Unix tools (jq, fd, rg) do this.

**Prompt module.**
> Run `<tool> X --json 2>/dev/null | jq .`. Does it work? Now run `<tool> X --json 2>&1 | jq .` — should fail or be filtered. If stderr ever contaminates stdout, that's a finding. Test with `--verbose` too.

---

## Card 09 — `🧪` Pin-The-Contract-Test

**Question.** "Does this surface have a golden/snapshot test that fails if `--help` text or output schema drifts?"

**Trigger.** Phase 5 / Phase 8 — every applied change.

**Failure modes.**
- No regression test for the new behavior.
- Test exists but pins the wrong thing (e.g. pins exit_code only; misses stdout schema drift).
- Test pins exact ANSI escape codes (will break with a NO_COLOR change).

**Fix-pointer.** Rubric §11 (regression_resistance). Exemplar: `cass --robot-meta` includes `requested_search_mode`, `search_mode`, `semantic_refinement` — pinning the contract.

**Prompt module.**
> For every applied change, write down what would silently regress if no test existed. Pick the smallest assertion that catches that regression. Use `assert_eq!` / `expect(...).toEqual(...)` / golden-file diff. Avoid pinning incidental fields (timestamps, request IDs, ANSI codes — strip those first).

---

## Card 10 — `🔀` Macros-vs-Granular

**Question.** "Is the canonical task a single macro? Is the granular path also exposed for control?"

**Trigger.** Designing new verbs; reviewing read-side composition.

**Failure modes.**
- Only granular tools exist; agent must orchestrate (slow + error-prone).
- Only macros exist; agent can't customize for edge cases.
- Macro and granular have inconsistent shapes (different naming, different output schemas).

**Fix-pointer.** Rubric §2. Exemplar: `am macro_start_session` collapses identity/registration friction; granular `register_agent`, `file_reservation_paths`, `send_message` exist for control.

**Prompt module.**
> List the canonical agent tasks. For each, identify: is there a one-call macro? If not, why not? Is the granular composition also exposed (for cases where the macro doesn't fit)? Macro should be the default; granular should be the escape hatch.

---

## Card 11 — `🆔` Stable-Handle

**Question.** "Does the tool give every artifact a stable, content-addressed handle?"

**Trigger.** Reviewing how the tool refers to its own internal entities (projects, agents, beads, sessions).

**Failure modes.**
- Tool uses sequential IDs that change across runs.
- Tool uses random IDs that aren't reproducible.
- Tool refers to entities by relative path (cwd-dependent).

**Fix-pointer.** Rubric §8 (determinism). Exemplar: `am` `project_key` is the absolute path (stable across agent migrations). Exemplar: `cass` `request_id` for cursor pagination.

**Prompt module.**
> List every entity the tool refers to (projects, runs, sessions, IDs, items). For each: is the handle stable across re-runs? Is it content-addressed (deterministic from inputs)? Does it survive a cwd change? Anything that breaks under re-run is a finding.

---

## Card 12 — `🩹` Error-Teaches

**Question.** "Does this error name the *exact* flag the agent should have used?"

**Trigger.** Reviewing every error message in the corpus.

**Failure modes.**
- "see --help" without naming the right flag.
- "syntax error" / "invalid argument" without explaining why.
- Generic messages from the framework (clap/cobra/argparse) without project-specific guidance.

**Fix-pointer.** Rubric §5 (error_pedagogy). Exemplar: `dcg` block messages name the safe alternative explicitly. Exemplar: `cass` parse-failure messages include the matching flag and an example.

**Prompt module.**
> For each error message: does it name (a) what failed, (b) where (file:line if applicable), (c) the *exact* flag/command the agent should have used? Generic clap-style "unknown flag" errors are a finding even though the framework wrote them — they need to be wrapped with project-specific guidance.

---

## Card 13 — `🚫` Never-Silent-Fail

**Question.** "If something goes wrong, does the user see *something* on stderr with non-zero exit?"

**Trigger.** Reviewing every code path; reviewing the intent-inference corpus.

**Failure modes.**
- Tool exits 0 with no output when the requested operation didn't happen.
- Tool catches an exception, prints nothing, exits 0.
- Empty result set looks identical to "didn't run."

**Fix-pointer.** Rubric §5 + §10. Hard rule: every "did nothing" outcome must produce a stderr line. Empty result sets should distinguish themselves from "tool didn't run" (e.g. `{"items": [], "ok": true}` vs no output at all).

**Prompt module.**
> Run the tool against an empty input / unmatchable query / nonexistent target. Does it produce output that's distinguishable from "tool crashed before doing anything"? If not, that's a finding.

---

## Card 14 — `⏱` Sub-Second-Hot-Path

**Question.** "Does the canonical first invocation return in < 1s?"

**Trigger.** Reviewing performance of read-side verbs; reviewing what an agent has to wait for.

**Failure modes.**
- `<tool> --help` takes > 500ms (suggests heavy import / network call on startup).
- `<tool> <verb> --json` triggers a full re-scan when an incremental query would do.
- The hot path triggers a network roundtrip that could be cached.

**Fix-pointer.** Rubric §2. Exemplar: `dcg` quick-reject filter (memchr) eliminates 99%+ of commands before regex. Exemplar: `cass` two-tier search (lexical fast path + opportunistic semantic).

**Prompt module.**
> Time `<tool> --help`, `<tool> --version`, `<tool> capabilities --json`. Each should be < 200ms. Then time the canonical agent invocation. If > 1s on warm cache, that's a finding (file as perf bead).

---

## Card 15 — `🌐` Honors-Env-Conventions

**Question.** "Does the tool honor `NO_COLOR`, `CI`, `TERM=dumb`, `SOURCE_DATE_EPOCH`, `XDG_*`?"

**Trigger.** Reviewing styling, output, cache locations.

**Failure modes.**
- ANSI codes in output even when stdout is a pipe.
- `NO_COLOR=1` ignored.
- Cache stored at `~/.<tool>/` instead of `$XDG_CACHE_HOME/<tool>/`.

**Fix-pointer.** Rubric §10 (composability). The shared community standards are documented at no-color.org, clig.dev, etc.

**Prompt module.**
> Run `<tool> X` once with stdout to a pipe (`<tool> X | cat`) and once interactively. Color difference? Now `NO_COLOR=1 <tool> X | cat` — should be plain. Now `CI=true <tool> X` — should suppress prompts. Where the tool ignores conventions: finding.

---

## Card 16 — `🔢` Deterministic-Output

**Question.** "Same input → same output bytes? Stable ordering? No timestamp leakage?"

**Trigger.** Reviewing JSON output stability; reviewing iteration order; reviewing test pinability.

**Failure modes.**
- Output ordering depends on hashmap iteration (non-deterministic).
- Timestamps in stdout (only OK in JSON fields, never in free text).
- IDs aren't reproducible from inputs.

**Fix-pointer.** Rubric §8. The output is content-addressable test fodder if and only if it's deterministic. Exemplar: `bv --robot-insights` includes `data_hash` (fingerprint of source jsonl) so consumers know if it changed.

**Prompt module.**
> Run `<tool> X --json` twice in a row. Diff the outputs. Anything but byte-identical is a finding (or document the non-determinism — wall-clock fields, request IDs — and ensure they're isolated to known fields, not interleaved through prose).

---

## Card 17 — `🧭` Discoverable-From-Help

**Question.** "Does `--help` mention `--json`, `capabilities`, `robot-docs`, `--robot-*` modes?"

**Trigger.** Reviewing top-level `--help` and every subcommand's `--help`.

**Failure modes.**
- Tool has `--robot-*` mode but `--help` doesn't mention it.
- `capabilities` subcommand exists but isn't in the verb list of `--help`.
- Agent must guess that `<tool> robot-docs guide` exists.

**Fix-pointer.** Rubric §9. The agent should be able to discover every other surface from `--help`'s footnotes.

**Prompt module.**
> Read `<tool> --help`. Does it mention every machine-readable surface (`--json`, `--robot-*`, `capabilities`, `robot-docs`)? If not, agents will miss them. Add a "AGENT/AUTOMATION" section to `--help`.

---

---

## Card 18 — `🪄` Recommended-Action

**Question.** "Does the tool's status / health / doctor output include a `recommended_action` field telling the agent what to do?"

**Trigger.** Reviewing tools with state (daemons, indexes, caches). Reviewing `doctor`/`status`/`health` verbs.

**Failure modes.**
- `doctor` output lists symptoms but doesn't recommend a fix.
- `recommended_action` exists but isn't structured (free text instead of `{"command": "...", "rationale": "..."}`).
- Agents read the data and have to deduce the next move.

**Fix-pointer.** Rubric §5 (error_pedagogy) + §9 (self_documentation). Exemplar: `cass health/status` `recommended_action` field is authoritative ([Q-402]).

**Prompt module.**
> Run `<tool> doctor --json`. Does the output include a `recommended_action` field with `command`, `rationale`, `is_destructive`, `alternatives`? If not, the agent has to deduce the next move from raw state. That's a finding.

---

## Card 19 — `🪟` Provenance-Field

**Question.** "When the tool runs in a degraded / fallback mode, does it report `--robot-meta`-style provenance so agents can detect it?"

**Trigger.** Tools with hybrid pipelines (lexical + semantic, cache + remote, etc.). Tools that have any "best effort" mode.

**Failure modes.**
- Tool falls back to lexical-only without telling the agent (silent degradation).
- Output looks identical whether semantic enrichment ran or not.
- Cache hit / cache miss not surfaced.

**Fix-pointer.** Rubric §4 (output_parseability) + §8 (determinism). Exemplar: `cass --robot-meta` returns `requested_search_mode`, `search_mode`, `semantic_refinement`, `fallback_tier`, `fallback_reason` ([Q-401]).

**Prompt module.**
> Find every place the tool can degrade gracefully. For each, does the output's `--robot-meta` (or equivalent) report what mode actually ran? If an agent can't distinguish "full-quality result" from "fallback-quality result," they may build downstream logic on incorrect assumptions. That's a finding.

---

## Card 20 — `📐` Schema-Pin

**Question.** "Is there a regression test that fails if `capabilities --json` schema changes without bumping `contract_version`?"

**Trigger.** Reviewing the durability of agent contracts across releases.

**Failure modes.**
- `capabilities --json` exists but no test pins it.
- Schema changes silently between v0.4 → v0.5; agents break in production.
- `contract_version` bumps not enforced.

**Fix-pointer.** Rubric §11 (regression_resistance). Pattern 9 from `REGRESSION-TEST-PATTERNS.md`.

**Prompt module.**
> List every "agent-facing schema" the tool ships: `capabilities --json`, `robot-docs guide` headers, `--robot-*` output schemas. For each, is there a regression test that fails on uncoordinated change? Schema drift is the silent killer of cross-version agent compatibility.

---

## Card 21 — `🩻` Doctor-Mode

**Question.** "Does the tool ship a `<tool> doctor` (or `health` / `status`) that diagnoses self-consistency and reports `operation_outcome.kind`?"

**Trigger.** Stateful tools (daemons, indexes, caches, distributed components).

**Failure modes.**
- Tool has internal state but no way to introspect it.
- `doctor` exists but only prints prose; no `operation_outcome.kind` enum.
- Output requires NLP to parse.

**Fix-pointer.** Rubric §9 + §5. Exemplar: `cass doctor` branches on `doctor.operation_outcome.kind` (kebab-case) ([Q-302]).

**Prompt module.**
> Stateful tools need a doctor verb that returns a machine-readable diagnosis: `success | health-failure | usage-error | lock-busy | repair-failure`. If your tool has any state across runs and no doctor verb, that's a finding.

---

## Card 22 — `🔇` Telemetry-Disable

**Question.** "Can the tool be run with telemetry / network calls / phone-home disabled?"

**Trigger.** Reviewing tools that emit telemetry, check for updates, or fetch online docs.

**Failure modes.**
- Tool phones home on every run; no opt-out.
- Opt-out env var exists but undocumented.
- Tool blocks for telemetry timeout when offline.

**Fix-pointer.** Rubric §10 (composability) + §8 (determinism). The community standard env vars: `DO_NOT_TRACK=1`, `<TOOL>_TELEMETRY=0`. Document in `capabilities.env_vars`.

**Prompt module.**
> Run the tool with no network. Does it work? Does it block? Does it warn? Run with `DO_NOT_TRACK=1`. Does that suppress telemetry? Document the answers; agents working offline must know.

---

## Card 23 — `🎯` Discovery-Footer

**Question.** "Does `<tool> --help` end with an 'AGENT/AUTOMATION' footer pointing to `--json`, `capabilities`, `robot-docs`?"

**Trigger.** Reviewing top-level + every subcommand's `--help`.

**Failure modes.**
- `--help` mentions `--robot-*` only in the top-level (not in subcommand `--help`).
- Agent reads subcommand `--help` and doesn't realize there's a JSON mode.
- `capabilities` exists but no `--help` references it.

**Fix-pointer.** Rubric §9 + Operator `🧭`. The footer should be a 3–5 line block at the bottom of every `--help` output:

```
AGENT/AUTOMATION:
  --json                    Emit JSON to stdout (every read-side verb supports it).
  --robot                   Force machine-readable output globally.
  capabilities --json       Print machine-readable capability dictionary.
  robot-docs guide          Paste-ready agent handbook.

EXIT CODES: 0=success, 1=user-input, 2=safety-block, 3=env, 4=transient
```

**Prompt module.**
> Run `<tool> --help` and `<tool> <verb> --help` for every verb. Does each one end with the AGENT/AUTOMATION footer? If not, agents will miss the agent-targeted surfaces and get lost in human-style help.

---

## Card 24 — `🪜` Two-Phase-Latency

**Question.** "Does the mega-command emit cheap slices first (sync) and slow ones with a per-metric `status: computed | timeout | skipped`?"

**Trigger.** Mega-commands or any verb that touches expensive computation (graph metrics, network, cross-correlation).

**Failure modes.**
- Mega-command blocks for 10s on graph centrality before returning anything.
- No way to opt out of expensive metrics.
- All-or-nothing latency.

**Fix-pointer.** Rubric §2 (ergonomics) + §10 (composability). Exemplar: `bv --robot-insights` two-phase pattern (Pattern 10).

**Prompt module.**
> Time the mega-command's components. The cheap ones (counts, sums) should return < 100ms; the expensive ones (centrality, betweenness) should be optional or have a per-metric timeout. If the whole call blocks for the slowest, that's a finding.

---

## Card 25 — `🔗` Cross-Verb-Reference

**Question.** "Does each verb's `--help` cross-reference related verbs?"

**Trigger.** Reviewing `--help` quality per verb.

**Failure modes.**
- `<tool> add --help` doesn't mention `<tool> list` (the obvious follow-up).
- `<tool> show --help` doesn't say "see also: <tool> diff, <tool> log."
- Agents can't traverse the verb graph from a single `--help`.

**Fix-pointer.** Rubric §9. Add a "SEE ALSO" section:

```
SEE ALSO:
  list    list items (use to find IDs for 'show')
  diff    show changes between two states
  log     history of changes
```

**Prompt module.**
> Read every verb's `--help`. Does it mention the related verbs? An agent who knows about `add` but doesn't know about `list` is stuck. Cross-references make the tool self-traversable.

---

## Card 26 — `🛂` Identity-Friction-Collapse

**Question.** "Can an agent start a session in one call, or do they have to register, ensure-project, login, etc. separately?"

**Trigger.** Reviewing tools with identity / authentication / session concepts. (MCP servers, multi-agent coordination, anything with `register_*` verbs.)

**Failure modes.**
- Agent must call 4+ identity-setup verbs before the first useful action.
- The setup-verbs aren't idempotent (re-running fails).
- "Already registered" errors instead of "got it; you're good."

**Fix-pointer.** Rubric §2 (ergonomics). Exemplar: `am macro_start_session` ([Q-201]) collapses identity friction.

**Prompt module.**
> What's the minimum sequence to start a useful session? If it's > 1 call AND no macro exists, build one. The "first useful action" should be ≤ 1 call away from a fresh agent's first invocation.

---

## Card 27 — `📦` Stable-Envelope

**Question.** "Does every JSON-emitting verb use the same top-level envelope (`{ok, data, meta, warnings, commands}`)?"

**Trigger.** Reviewing JSON output across multiple verbs.

**Failure modes.**
- `list --json` returns `{"items": [...]}`.
- `show --json` returns `{"data": {...}}`.
- `get --json` returns the value directly (no wrapper).
- Agents need a different parser per verb.

**Fix-pointer.** Rubric §4 + §11. Pattern: standardize on a single envelope:

```jsonc
{
  "ok": true,
  "tool_version": "...",
  "data": { /* the verb-specific payload */ },
  "meta": { /* provenance, data_hash, request_id */ },
  "warnings": [],
  "commands": []
}
```

**Prompt module.**
> Pick a top-level envelope and use it consistently. Refactor any divergent verbs (with deprecation paths). Test that every `--json` output matches the envelope schema.

---

## Card 28 — `🔬` Single-Step-Atomicity

**Question.** "Does each mutating verb either fully succeed or fully fail? No partial side effects?"

**Trigger.** Reviewing mutating verbs (writes, deletes, syncs, migrates).

**Failure modes.**
- `<tool> import file.json` writes half the records, then errors.
- No transaction; agent must re-run and dedupe.
- Failure leaves system in an inconsistent state.

**Fix-pointer.** Rubric §7 (safety_with_recovery) + §8 (determinism). Use transactions / write-then-rename / advisory locks. The error message should say whether any writes occurred.

**Prompt module.**
> Force a failure mid-mutation (kill the tool, network drop, disk full). What state is left behind? Can the agent re-run safely? If not, atomicity is broken.

---

## Card 29 — `🧷` Idempotency-Pin

**Question.** "Can the agent safely re-run any mutating verb with the same args?"

**Trigger.** Reviewing every mutating verb.

**Failure modes.**
- Re-running `<tool> add foo` creates a duplicate.
- Re-running `<tool> sync` triggers a full replay.
- Network retries duplicate the side effect.

**Fix-pointer.** Rubric §7. Pattern: content-addressed IDs, idempotency tokens (`--idempotency-key=<hash>`), or "already done" detection.

**Prompt module.**
> Pick a mutating verb. Run it. Run it again with same args. Does the second run skip? Error? Duplicate? Anything but skip-with-noop is a finding.

---

## Card 30 — `🧶` Composable-Verbs

**Question.** "Can the output of one verb be piped directly into another without manual reshaping?"

**Trigger.** Reviewing pipelines.

**Failure modes.**
- `<tool> list --json | <tool> update --from-list` doesn't exist.
- Each verb's output schema differs; agents need jq surgery between calls.
- No "stdin = JSON list of IDs" mode.

**Fix-pointer.** Rubric §10 (composability). Pattern: every mutating verb accepts `--from-stdin` or `--ids-file=-` to consume the output of read verbs.

```bash
<tool> list --json --filter active | <tool> update --from-stdin --field=status --value=closed
```

**Prompt module.**
> Look at the canonical pipelines an agent might want. For each, can output flow directly into input? If they need jq surgery, add a `--from-stdin` mode.

---

## Card 31 — `🧮` Bulk-Friendly

**Question.** "When the agent has a list of N IDs, can they operate on all N in one call?"

**Trigger.** Reviewing per-item verbs.

**Failure modes.**
- Agent must loop in shell: `for id in $(...); do <tool> close "$id"; done`.
- Per-call overhead × N is the latency floor.
- Partial failures aren't reported atomically.

**Fix-pointer.** Rubric §2 + §10. Pattern: `<tool> close X-001 X-002 X-003` AND `<tool> close --from-stdin`. Bulk output is `{"ok": true, "results": [{"id": "X-001", "status": "closed"}, ...]}`.

**Prompt module.**
> If an agent has 50 IDs, what's the canonical way to operate on all of them? If it requires a shell loop, that's a finding. Bulk verbs are table stakes for agent ergonomics at scale.

---

## Card 32 — `🧾` Drift-Guard

**Question.** "Are critical agent-facing surfaces (capabilities schema, exit-code dict, --help footer) protected by drift-guard tests?"

**Trigger.** Reviewing CI / regression test coverage.

**Failure modes.**
- `capabilities --json` schema test absent.
- Exit-code dict tested per verb but not as a whole.
- A future PR can silently change the contract.

**Fix-pointer.** Rubric §11. See `HOOKS-INTEGRATION.md` for pre-commit drift guards and `CI-INTEGRATION.md` for PR checks.

**Prompt module.**
> List every agent-contract artifact (capabilities, robot-docs, --help footer, exit codes, env-var list). For each, is there a CI test that fails on uncoordinated drift? Anything unprotected can silently regress.

---

## Card 33 — `🎓` Onboarding-Curve

**Question.** "How many `--help` reads does a fresh agent need before completing the canonical task?"

**Trigger.** Phase 9 simulation review.

**Failure modes.**
- Fresh agent reads top-level `--help`, then verb `--help`, then can't proceed without docs.
- The path from "first invocation" to "useful work" is > 3 reads.
- Critical info (the mega-command, the `--robot-*` flag) buried below the fold.

**Fix-pointer.** Rubric §1 + §3 + §9. Combined with Operator `🎯` (Discovery-Footer). The fresh agent should reach "useful work" in ≤ 2 reads.

**Prompt module.**
> Watch the Phase 9 simulator's transcript. Count `--help` invocations before the first non-help command. If > 2, the onboarding curve is too steep.

---

## Composition cheat-sheet

For each failing dimension, apply this operator pipeline:

| Dimension | Operators (in order) |
|-----------|----------------------|
| agent_intuitiveness | ① ⟁ 🩹 🎓 |
| agent_ergonomics | Σ 🔀 ⏱ 🛂 🧮 🪜 |
| agent_ease_of_use | 🧭 📖 📜 🎯 🔗 |
| output_parseability | 🪧 🚦 🔢 📦 🪟 |
| error_pedagogy | 🩹 ⟁ 🚫 🪄 |
| intent_inference | ⟁ 🩹 🚫 |
| safety_with_recovery | 🛡 🩹 🔬 🧷 |
| determinism | 🔢 🆔 🌐 🪟 |
| self_documentation | 📜 📖 🧭 🎯 🩻 |
| composability | 🪧 🚦 🌐 🚫 🧶 🧮 🔇 |
| regression_resistance | 🧪 📐 🧾 |

Apply operators in the listed order. Don't skip; each operator catches a different failure mode. If an operator would break an existing user contract, deploy 🛡 (Safe-Alternative-Always) — add a deprecation path rather than a breaking change.
