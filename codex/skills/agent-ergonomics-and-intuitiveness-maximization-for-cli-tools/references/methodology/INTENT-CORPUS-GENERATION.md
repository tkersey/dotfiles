# INTENT-CORPUS-GENERATION

How to build the Phase 3 corpus of plausibly-wrong invocations.

The corpus is the *ground-truth* test of whether the tool's intent-inference is good. Two generators (naive + savvy), one runner, five classification buckets.

---

## Why two generators?

**Naive generator** simulates a fresh agent that has never used the tool. Source: only `--help` output. Catches: typos, wrong subcommand order, family confusion (rm vs delete vs remove), spelling variants.

**Savvy generator** simulates an experienced agent with full source access. Catches: boundary cases the naive generator misses — interactions between flags, deprecated spellings the source mentions, unicode/shell-injection edge cases.

The intersection of "what naive misses but savvy catches" is the *valuable* part of the savvy corpus. Don't run savvy first — it'll bias you toward source-shaped tests and miss real agent failures.

---

## Naive generator prompt template

(Full prompt is in `AGENT-PROMPTS.md § intent-stresser-naive`. This file gives the *categories* the naive generator should cover.)

### Category A — typos in flag names

For every flag in `surface_inventory.jsonl` (kind=flag), generate at least one typo at edit-distance 1:

- `--json` → `--jsno`, `--jaon`, `--jsonn`
- `--verbose` → `--vebose`, `--verbos`, `--vrebose`
- `--quiet` → `--qiet`, `--quite`, `--quet`
- `--output` → `--ouput`, `--otuput`, `--outupt`
- `--help` → `--hlep`, `--hepl`, `--halp`

### Category B — wrong subcommand order

For verbs that take both args and flags:
- `<tool> <verb> <arg> --flag` (canonical) vs `<tool> <verb> --flag <arg>`
- `<tool> --flag <verb> <arg>` (flag before verb)
- `<tool> <verb> --flag=<value>` vs `<tool> <verb> --flag <value>`

### Category C — spelling variants

- US/UK: `--color`/`--colour`, `--license`/`--licence`, `--organize`/`--organise`
- Plural/singular: `--option`/`--options`, `--tag`/`--tags`
- Synonyms: `--silent`/`--quiet`, `--name`/`--label`, `--force`/`--yes`

### Category D — tool-family confusion

For verbs that other tools name differently:
- `<tool> ls` (Unix) vs `<tool> list` (POSIX-y)
- `<tool> rm` vs `<tool> delete` vs `<tool> remove` vs `<tool> destroy`
- `<tool> mv` vs `<tool> move` vs `<tool> rename`
- `<tool> cp` vs `<tool> copy` vs `<tool> clone`
- `<tool> mk` vs `<tool> create` vs `<tool> new` vs `<tool> add`

### Category E — missing required positional args

For every verb that takes required positional args:
- Run with no args: `<tool> <verb>`
- Run with too few args: `<tool> <verb> <only-the-first>`

### Category F — common mis-modelings

- `<tool> --help <verb>` (POSIX would run `<verb>` and pass --help; Unix would print top-level help)
- `<tool> help <verb>` vs `<tool> <verb> --help`
- `<tool> -h` vs `<tool> --help` (does both work?)
- `<tool> -V` vs `<tool> --version`

### Category G — env-var typos

For every env var in `surface_inventory.jsonl` (kind=env):
- Drop the prefix when the resulting key is not runner-denylisted:
  `<TOOL_PREFIX>_CONFIG` → `CONFIG`. Collisions with protected process
  variables such as `HOME` are documented as design risks, but the deterministic
  runner must not execute corpus rows that set them.
- Typo the prefix: `<TOOL_PREFIX>_HOME` → `<TOOL_PREFIIX>_HOME`
- Wrong case: `<TOOL_PREFIX>_HOME` → `<tool_prefix>_home`

---

## Savvy generator prompt template

(Full prompt is in `AGENT-PROMPTS.md § intent-stresser-savvy`. Categories below are *boundaries*, not surface scans.)

### Category H — almost-but-not-quite matches

Identify flags in the source that:
- Have a near-duplicate in another subcommand: does each subcommand handle its own correctly?
- Differ from a competitor tool's flag by one letter (`--threads` vs `--thread`, `--max-depth` vs `--maxdepth`)
- Are aliased in the source (e.g. `--quiet` aliases `--silent`) — does the alias still work? Was it accidentally dropped in a refactor?

### Category I — flag interactions

For pairs of flags that "should" be mutually exclusive or order-dependent:
- `--json --pretty` (do both work? does the schema differ?)
- `--quiet --verbose` (which wins?)
- `--no-color --color always` (last-flag-wins, or error?)
- `--count 5 --limit 10` (which is authoritative?)

### Category J — boundary numeric/string args

- `--limit 0`, `--limit -1`, `--limit 999999999` (overflow?), `--limit ""`
- `--name "  "` (whitespace), `--name ""` (empty), `--name $'\x00'` (NUL byte), `--name "$(rm -rf /)"` (command injection -- shell-quote test). Represent shell-looking values as argv data, for example: `{"invocation":"mytool --name '$(rm -rf /)'","argv":["mytool","--name","$(rm -rf /)"]}`.
- Unicode: `--name 日本語`, `--name 🚀`, `--name "right-to-left العربية"`

### Category K — path / cwd handling

- Relative paths from a different cwd: set the corpus row's `cwd` field and use `argv:["<TOOL>","--config","./config.toml"]` (does it find it relative to cwd?)
- `~/path` (does the tool expand ~?)
- Symlinks (does it resolve?)
- `..` traversal (does it sanitize?)

### Category L — deprecated spellings the source still mentions

Search source comments for "deprecated", "legacy", "old name", "alias for". For each found:
- Try the deprecated spelling. Does it work? Does it warn? Does it silently use the new name?

### Category M — aliases that other similar tools have but this doesn't

Compare to "tools in the same family":
- If this is a search tool: try `<tool> grep`, `<tool> find`, `<tool> rg` aliases.
- If this is a package manager: try `<tool> add`, `<tool> install`, `<tool> i` aliases.
- If this is a git-flavored tool: try `<tool> co` (checkout), `<tool> br` (branch), `<tool> ci` (commit) aliases.

---

## Classification rubric (for `intent-runner`)

For each invocation, examine:
1. Exit code
2. Stdout (was anything emitted?)
3. Stderr (was a useful message produced?)
4. State change (did the tool *do* something, or only print?)

| Outcome | Pattern |
|---------|---------|
| `silent_fail` | exit 0 + no stdout + no stderr + no state change. The tool did nothing and didn't say so. (Worst.) |
| `useless_error` | exit ≠ 0 + stderr is generic ("syntax error", "invalid argument", "see --help"). (Bad.) |
| `useful_hint` | exit ≠ 0 + stderr names the *exact* flag/command/env-var that would have worked. (Acceptable.) |
| `inferred_and_acted` | exit 0 (or ≠ 0 with a non-error explanation) + state change matches agent intent + (optional) stderr warns about the canonical form. (Best.) |
| `skipped` | runner intentionally did not execute because the row would mutate state without `safe_to_run:true`, referenced a missing `cwd`, or used unsafe legacy shell text without `argv`. |

**Edge cases:**
- Tool launches a TUI in non-TTY context → classify as `silent_fail` (the agent is blocked).
- Tool prompts for input in non-TTY context → classify as `silent_fail` (same reason; the prompt never returns).
- Tool succeeds (exit 0) but did the *wrong* thing (e.g. interpreted `<tool> ls` as "create a file named ls") → classify as `silent_fail` if no stderr warning, else `useless_error` if stderr-warned but still wrong.
- Shell-injection-shaped values are corpus arguments, not shell code. The runner executes `argv` directly and never evaluates `invocation` with `bash -c`.

---

## Corpus size targets

| Tool size | Min naive entries | Min savvy entries | Total |
|-----------|--------------------|---------------------|-------|
| Tiny (≤ 5 verbs, ≤ 30 flags) | 15 | 10 | 25 |
| Typical (6–15 verbs) | 25 | 20 | 45 |
| Full (16–40 verbs) | 50 | 40 | 90 |
| Multi-binary | 100+ | 80+ | 180+ |

Don't pad — generate as many as needed to cover the categories above for THIS tool. If naive can't reach 15 because the tool has only 3 flags, that's fine; it's a small corpus.

---

## Re-running across passes

The corpus is **stable**: same `corpus_id` across passes (so the runner can detect "this entry was previously useless_error; now it's useful_hint"). When re-running:

1. Load `audit/intent_inference_corpus.jsonl` from the prior pass.
2. Re-run every entry against the new binary.
3. Append new outcomes with `pass: <N+1>` (don't overwrite prior outcomes).
4. Compute per-entry classification delta. The percentage of `useless_error → useful_hint`/`inferred_and_acted` transitions is the **intent-inference uplift** metric.

If a new pass adds new categories (e.g. user added a new subcommand), generate fresh entries for that subcommand and append; preserve prior `corpus_id`s.

---

## Anti-patterns

- **Don't generate "obviously broken" invocations** like `<tool> --foo --bar --baz --qux --quux` (10 unknown flags). The corpus is for *plausibly-wrong*, not random fuzzing. (Fuzzing is a different audit; not this skill's scope.)
- **Don't grade success on whether the agent felt good.** Grade on the four classes above. Subjective notes go in `notes`.
- **Don't run with `--interactive` or anything that blocks.** The runner is automated; blocking inputs are findings.
- **Don't re-generate the corpus on every pass.** The corpus is stable; only outcomes change.
