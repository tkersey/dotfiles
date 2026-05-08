# COUNTER-EXAMPLES — What < 250 looks like

For every score-anchor pattern in CANONICAL-EXEMPLARS.md, there's a counter-example: the surface anchored to 0–250 on the rubric. These are real failure modes from real CLIs.

Use this file to recognize "this surface is genuinely bad" vs. "this surface is just unfamiliar." Score against the bar, not the vibes.

---

## CE-1 — Bare invocation launches a TUI in non-TTY context

**Pattern.** `<tool>` with no args opens a terminal UI that consumes stdin and never returns when stdout is a pipe. Agents pasting `<tool> | jq .` get stuck.

**Why it's bad.** Blocks automation entirely. The agent times out or hangs forever.

**Anchor.** `agent_intuitiveness: 0`, `composability: 0`.

**Real-world hit.** Many database CLIs (without explicit `-c '<query>'`) drop into a REPL. Many graph-tracing tools open ncurses with no timeout.

**Recommendation pattern.** Detect non-TTY via `is_terminal()` / `isatty()`. If non-TTY: print a one-line guide pointing to `--robot-*` or `--json` and exit non-zero. Never block.

---

## CE-2 — Silent_fail on typo

**Pattern.** `<tool> --jsno` exits 0 with no output. Agent thinks it worked.

**Why it's bad.** Worst possible outcome on the four-class rubric. Agent moves on assuming success.

**Anchor.** `intent_inference: 0`, `error_pedagogy: 0`, `safety: 0`.

**Real-world hit.** Some Bash scripts with permissive `getopts`; some Python `argparse` configurations with `parse_known_args` and no error on unknown.

**Recommendation pattern.** Always exit non-zero on unknown flags. Never accept silently. Add levenshtein-1 hint as additional polish.

---

## CE-3 — Generic "syntax error" with no path forward

**Pattern.** `<tool> <verb> --bad-flag` errors with `error: syntax error near '--bad-flag'`. No suggestion.

**Why it's bad.** Useless_error class. Agent must guess.

**Anchor.** `error_pedagogy: 100`.

**Real-world hit.** Many shell-tool wrappers; sometimes Make targets; some old C tools.

**Recommendation pattern.** Levenshtein hint at minimum. "did you mean `--good-flag`?" Bonus: proceed-with-warning if confidence is high.

---

## CE-4 — `--help` is a wall of text with no examples

**Pattern.** `<tool> --help` is 200 lines of flag definitions. No "Examples" section. No agent-mode hint. No env-var docs.

**Why it's bad.** Agent reads but can't compose. Fails the discoverability dim.

**Anchor.** `agent_ease_of_use: 200`, `self_documentation: 200`.

**Real-world hit.** Many GNU classic tools.

**Recommendation pattern.** Add "EXAMPLES" section. Add "AUTOMATION / AGENT" section pointing to `--json` / `--robot-*` / `capabilities`.

---

## CE-5 — Stdout and stderr both carry data

**Pattern.** `<tool> X` prints log lines on stdout interspersed with the result. `<tool> X | jq .` fails because stdout has non-JSON.

**Why it's bad.** Pipeline-broken. Defeats `--json` mode.

**Anchor.** `output_parseability: 0`, `composability: 0`.

**Real-world hit.** Many older Python tools using `print()` for both progress and data; some Ruby gems.

**Recommendation pattern.** Move all log/progress lines to stderr. Stdout only carries the requested data. Document it.

---

## CE-6 — Exit 1 means three different things

**Pattern.** Exit 1 means: (a) user input error, (b) "ran fine, no results found," (c) tool internal error. Agent can't branch.

**Why it's bad.** Exit-code contract violation. Composability dies.

**Anchor.** `output_parseability: 100`, `composability: 100`.

**Real-world hit.** `grep` famously uses exit 1 for "no match" — actually a deliberate design but agents must remember it. Many search tools copy this without thought.

**Recommendation pattern.** Document the exit-code dictionary. If an exit value already means "no results" (like grep), keep it but document. If it's truly ambiguous, fork into different values: 0=success, 1=user-input-error, 2=safety-block, 3=tool-environment-error.

---

## CE-7 — ANSI codes leak into piped stdout

**Pattern.** `<tool> X | cat` shows escape sequences. `<tool> X > file.txt` writes them to disk. Agents that grep see noise.

**Why it's bad.** Composability fail.

**Anchor.** `composability: 0`.

**Real-world hit.** Many tools that use `colored::*` Rust crate without conditional. Some npm scripts.

**Recommendation pattern.** Use `is-terminal` / `term::isatty()`. Honor `NO_COLOR=1`. Detect piped stdout. Suppress ANSI when not interactive.

---

## CE-8 — Output ordering depends on hashmap iteration

**Pattern.** `<tool> X --json` returns `{"items": ["a", "b", "c"]}` once and `{"items": ["b", "c", "a"]}` next time. Same input.

**Why it's bad.** Determinism fail. Tests that pin output break randomly.

**Anchor.** `determinism: 0`, `regression_resistance: 0`.

**Real-world hit.** Many Go tools that range over `map`. Many Rust tools using `HashMap` without sorting.

**Recommendation pattern.** Sort iteration order before serializing. Use `BTreeMap` or sort the output. Pin the expected ordering in tests.

---

## CE-9 — Wall-clock timestamps in non-JSON output

**Pattern.** `<tool> X` prints `[2026-05-06 14:32:11] item1`. Each run differs.

**Why it's bad.** Determinism fail. Tests can't pin output.

**Anchor.** `determinism: 100`.

**Real-world hit.** Many CI tools. Many logging frameworks.

**Recommendation pattern.** Move timestamps to JSON `meta.ts` field; never embed in prose stdout. Honor `SOURCE_DATE_EPOCH`.

---

## CE-10 — Destructive op runs on first invocation

**Pattern.** `<tool> delete <thing>` deletes immediately. No `--yes`. No `--dry-run`. No confirmation.

**Why it's bad.** Safety fail. One typo destroys data.

**Anchor.** `safety_with_recovery: 0`.

**Real-world hit.** Some package-cleanup tools. Old `rm` on early Unix.

**Recommendation pattern.** Add `--yes` gate. Add `--dry-run` flag. Error message names the safe alt.

---

## CE-11 — `<tool> --version` prints a 50-line banner

**Pattern.** `<tool> --version` prints version + license + copyright + URL + ascii art. Agents parsing it grep noise.

**Why it's bad.** Output parseability fail.

**Anchor.** `output_parseability: 250`.

**Real-world hit.** Some old GNU tools; some self-aggrandizing modern Rust tools.

**Recommendation pattern.** `--version` prints just the version. Add `--version --verbose` for the banner if needed. Or move the banner to `<tool> info`.

---

## CE-12 — Errors print to stdout, not stderr

**Pattern.** `<tool> X 2>/dev/null` shows the error message anyway because it was printed to stdout.

**Why it's bad.** Composability + parseability fail. `<tool> X | jq .` errors don't filter out.

**Anchor.** `composability: 0`.

**Real-world hit.** Some Python tools using `print(..., file=sys.stdout)` instead of stderr.

**Recommendation pattern.** Errors → stderr. Always.

---

## CE-13 — Non-deterministic IDs

**Pattern.** `<tool> add foo` generates a random ID `id-abc123`. Re-running creates a new ID, no deduplication.

**Why it's bad.** Determinism fail. Idempotency impossible.

**Anchor.** `determinism: 0`.

**Real-world hit.** Some "session" tools that create new sessions on every invocation.

**Recommendation pattern.** IDs are content-addressed (hash of inputs) or explicit (`--id <user-provided>`). Re-runs detect existing IDs.

---

## CE-14 — Tool requires network for `--help`

**Pattern.** `<tool> --help` makes an HTTP call to fetch documentation. Offline agent gets a hang or timeout.

**Why it's bad.** Determinism + ergonomics + composability fail.

**Anchor.** `composability: 0`.

**Real-world hit.** A few cloud-vendor CLIs that try to be "smart" about latest docs.

**Recommendation pattern.** `--help` is offline. Period. If you want online docs, that's `<tool> docs --online`.

---

## CE-15 — `<tool> capabilities` doesn't exist

**Pattern.** No way to introspect the tool's version + features + exit codes + env vars. Agent must read source or website.

**Why it's bad.** Self-doc fail.

**Anchor.** `self_documentation: 250`.

**Real-world hit.** Most CLIs older than 2024. Many "we'll add it later" tools.

**Recommendation pattern.** Add `<tool> capabilities --json`. Document required keys (version, contract_version, features, commands, exit_codes, env_vars).

---

## CE-16 — Verbose mode contaminates stdout

**Pattern.** `<tool> X --json --verbose` interleaves log lines with JSON on stdout. `jq .` errors on the log lines.

**Why it's bad.** Composability + parseability fail. Defeats the point of `--verbose`.

**Anchor.** `composability: 100`.

**Real-world hit.** Many tools that use `--verbose` to "show more output" without splitting streams.

**Recommendation pattern.** `--verbose` writes to stderr. Stdout still pure data. (Or: `--verbose` only matters when stdout is human-targeted.)

---

## CE-17 — Hardcoded TUI on non-interactive verb

**Pattern.** `<tool> show <id>` opens a pager (`less`-style) even when stdout is a pipe.

**Why it's bad.** Composability fail.

**Anchor.** `composability: 100`.

**Real-world hit.** `git log` defaults to pager (use `git --no-pager log` or `PAGER=cat`).

**Recommendation pattern.** Detect non-TTY → no pager. Or always-no-pager and let the user pipe to `less` themselves.

---

## CE-18 — Inconsistent JSON across verbs

**Pattern.** `<tool> list --json` returns `{"items": [...]}`, `<tool> show --json` returns `{"data": {...}}`, `<tool> get --json` returns just the value (no wrapper). Agents can't write generic parsers.

**Why it's bad.** Schema chaos.

**Anchor.** `output_parseability: 200`.

**Real-world hit.** Tools that grew organically without a single output module.

**Recommendation pattern.** Single canonical envelope: `{"ok": true, "data": ..., "meta": {...}}`. Every verb uses it.

---

## CE-19 — Required arg comes AFTER an optional flag

**Pattern.** `<tool> --json <required-arg>` works; `<tool> <required-arg> --json` errors with "unknown command." Agent's natural ordering fails.

**Why it's bad.** Intent-inference fail. Mis-orderings should succeed.

**Anchor.** `intent_inference: 250`.

**Real-world hit.** Some hand-rolled arg parsers; some clap configurations.

**Recommendation pattern.** Use a parser that's order-insensitive (clap, cobra, click do this by default). Reject only genuinely ambiguous orderings.

---

## CE-20 — Exit code differs between `--json` and human modes for the same input

**Pattern.** `<tool> X` exits 0; `<tool> X --json` exits 1 because the JSON serialization fails on a unicode character. Same data, different exit.

**Why it's bad.** Determinism + composability fail. Agents can't trust the exit code.

**Anchor.** `composability: 100`, `determinism: 250`.

**Real-world hit.** Edge cases in JSON serialization (NaN, infinity, non-UTF-8).

**Recommendation pattern.** Output mode does NOT affect exit code. If JSON serialization fails, that's a tool bug — fix the serializer, don't change the exit.

---

## How to use this file

When scoring:
- A surface that exhibits any of CE-1 through CE-20 patterns scores ≤ 250 on the relevant dimension.
- A surface that exhibits multiple patterns scores 0 with the worst-pattern's anchor as evidence.
- The recommendation for each pattern is in the corresponding row above.

When recommending:
- Cite the CE-NN counter-example AND the corresponding CANONICAL-EXEMPLARS pattern (e.g. "CE-2 → Pattern 2 of dcg's error-pedagogy anchor").
- The diff sketch should move the surface from CE territory to canonical territory.

Counter-examples are **rubric anchors at the bottom**, just as canonical exemplars are anchors at the top.
