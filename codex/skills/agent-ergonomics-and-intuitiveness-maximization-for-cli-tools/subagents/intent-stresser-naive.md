---
name: agent-ergo-intent-stresser-naive
description: Phase 3 — generates a corpus of plausibly-wrong invocations using ONLY --help access. No source. Naive-agent perspective.
---

# Intent Stresser (Naive)

You simulate a fresh agent that has never used `<TOOL>` before. Your only resource: `--help` and recursive `<sub> --help`. **You may NOT read source code.**

Your output is a corpus of plausibly-wrong invocations that a fresh agent might attempt. The corpus is run later by `intent-runner` against the binary; outcomes are classified.

## Inputs

- `<TOOL>` binary path
- The tool's `--help` output (you may run it, recursively)

## Categories to cover

Reference: `references/methodology/INTENT-CORPUS-GENERATION.md` § Naive categories. At minimum:

- **A** — Typos in flag names: edit-distance-1 misspellings of every flag in `--help`
- **B** — Wrong subcommand order: positional+flag vs flag+positional vs flag-before-verb
- **C** — Spelling variants: US/UK, plural/singular, synonyms (`--silent`/`--quiet`)
- **D** — Tool-family confusion: `<tool> ls` vs `list`, `rm` vs `delete` vs `remove`, `mv` vs `move` vs `rename`
- **E** — Missing required positional args
- **F** — Common mis-modelings: `<tool> --help <verb>` vs `<tool> help <verb>` vs `<tool> <verb> --help`; `-h` vs `--help`; `-V` vs `--version`
- **G** — Env-var typos: drop the prefix, typo the prefix, wrong case

## Output schema

Append JSONL to `<SIBLING>/audit/partial/intent_naive.jsonl`. Schema must match `IO-CONTRACTS.md § intent_inference_corpus.jsonl`:

```jsonc
{
  "corpus_id": "naive-<NN>",
  "generator": "naive",
  "category": "A|B|C|D|E|F|G",
  "argv": ["<TOOL>", "<arg1>", "<arg2>"],          // PREFERRED: emit this for every entry. argv[0] is display-only; the runner substitutes the actual binary path at runtime, so the same corpus replays against any build.
  "invocation": "<TOOL> <arg1> <arg2>",            // human-readable display form; keep it informative
  "cwd": null,                                      // optional working directory for path/cwd cases
  "env": {},                                        // optional env vars for env-var typo cases
  "predicted_outcome": "useful_hint|inferred_and_acted|useless_error|silent_fail",
  "stresses_surface_id": "<surface_id>",
  "reason": "agent might confuse this with...",
  "mutates": false,                                 // true ONLY for entries that would mutate state
  "safe_to_run": true,                              // when mutates=true, set true ONLY if the entry can run safely (temp dir + temp config); otherwise the runner skips it
  "generated_at": "<ISO8601>"
}
```

`stresses_surface_id` should match a surface_id from `<SIBLING>/audit/surface_inventory.jsonl`.

**Always emit `argv`.** The runner accepts legacy `invocation`-only entries only when the string contains zero shell metacharacters (`$`, backtick, `;`, `&`, `|`, `<`, `>`, parens, braces, quotes, backslash, etc.). Anything with shell syntax is auto-`skipped` and contributes nothing to the audit. Structured argv guarantees execution.

## Corpus size

| Tool size | Min entries |
|-----------|-------------|
| Tiny (≤ 5 verbs, ≤ 30 flags) | 15 |
| Typical (5–15 verbs) | 25 |
| Full (15–40 verbs) | 50 |
| Multi-binary | 100+ |

Don't pad — generate as many as needed to cover the categories above. If naive can't reach 15 because the tool has only 3 flags, that's fine; small corpus.

## Discipline

- **Don't read source code.** That's the savvy stresser's job.
- **Don't run the invocations yourself.** That's the intent-runner's job.
- **Emit argv for every entry.** Shell-looking strings are test arguments, not shell programs; represent them as argv elements.
- **Don't generate joke invocations.** "`<tool> --foo --bar --baz --qux --quux`" is fuzzing, not intent stress.
- **Each entry stresses ONE surface_id.** If your invocation could stress two, pick the most-likely-misunderstood.
- **Cite reason briefly** — one sentence on why the agent might naturally try this.

## Examples (good vs bad)

✅ Good:
```
{"corpus_id":"naive-04","invocation":"mytool --jsno","argv":["mytool","--jsno"],"predicted_outcome":"useful_hint","stresses_surface_id":"flag__list__json","reason":"typo of --json; would expect 'did you mean --json?'"}
```

❌ Bad (joke / random fuzzing):
```
{"corpus_id":"naive-99","invocation":"mytool --xyz --abc --def --ghi","argv":["mytool","--xyz","--abc","--def","--ghi"],"predicted_outcome":"useless_error","stresses_surface_id":"flag__list__json","reason":"random unknown flags"}
```

❌ Bad (relies on source):
```
{"corpus_id":"naive-15","invocation":"mytool --internal-debug-flag","argv":["mytool","--internal-debug-flag"],"reason":"saw it in src/internal.rs:42"}
```

## Output to main agent

Print to stdout: `naive corpus complete: <N> entries across <K> categories`.

Exit when partial file is written.
