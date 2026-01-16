---
name: gen-mindset
description: "Mine Codex sessions to synthesize your top software design heuristics (no quotes, no evidence)."
metadata:
  short-description: "Generate a design mindset from session logs"
---

# gen-mindset

## Intent
Synthesize a **ranked list of software design heuristics** by mining your Codex session logs.

This skill is optimized for:
- **Design-only** heuristics (types/invariants, testing/validation, error handling, readability/complexity, abstraction discipline).
- **Signal-weighted** ranking: what shows up often and what the user appears to approve.
- **Low leakage** output: **list only** (no scores, no quotes, no file paths).

## When to use
- You want to distill the design principles that actually recur in your working style.
- You’re updating or drafting another mindset skill (e.g., `$tk`) and want evidence from your own sessions.

## Defaults
- Sessions corpus: `~/.codex/sessions`
- Output: top 20 heuristics
- Evidence: **suppressed** (no counts, no quotes)
- Approval detection: explicit positives + short approvals + next-step directives

## Inputs
Ask only if the user hasn’t specified:
1. `top N` (default 20)
2. sessions path override (default `~/.codex/sessions`)

Do **not** ask about scoring/evidence unless the user requests it.

## Output contract
- Output only a bullet list of the top `N` heuristics.
- Do **not** include scores, weights, quotes, or snippets.
- Do **not** include paths into sessions.
- If fewer than `N` heuristics are detected, output what you have and state that fewer were found.

## Method (what the script does)
1. Scan `~/.codex/sessions/**/*.jsonl`.
2. Extract assistant messages (stripping the leading `Echo:` line when present).
3. Match against a curated set of design-heuristic patterns.
4. Weight by:
   - frequency across assistant messages
   - plus additional weight when the next user message looks like approval

### Approval detection rules
A user message counts as approval if it is **not** a clear complaint and matches any:
- Approval keywords: `thanks`, `great`, `lgtm`, `ok`, `yes`, `continue`, etc.
- Short acknowledgements (very short messages)
- Next-step directives (imperative “do X next” instructions)

## Execution
Run the helper script and return the list.

Recommended invocation:
- `python3 ~/.codex/skills/gen-mindset/scripts/gen-mindset.py --top 20`

If you prefer `uv`:
- `uv run python ~/.codex/skills/gen-mindset/scripts/gen-mindset.py --top 20`

## Hard rules
- Explicit-only skill: do not auto-trigger.
- Don’t invent principles that aren’t in the corpus.
- Keep the list phrased as **heuristics** (“Prefer…”, “Treat…”, “When…”) not slogans.
- No scope creep: don’t update other skills unless asked.
