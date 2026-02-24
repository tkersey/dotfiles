---
name: logophile
description: "Precision copy edits + naming: compress and clarify without changing meaning. Triggers: `$logophile`, rewrite/reword/rephrase, shorten, rename titles/labels/headings. Avoid operational scope/validation tasks unless rewriting is explicit."
---

# Logophile

## Intent
Maximize semantic density without semantic drift.

## Contract (invariants)
- Preserve meaning, obligations (must/should/may), and uncertainty (keep epistemic hedges; delete filler hedges).
- Preserve agency/ownership: do not change who does/owns/approves what; avoid active/passive rewrites that reassign responsibility.
- Preserve must-keep tokens: numbers, proper nouns, quotes, code/identifiers, paths/flags/URLs.
- Preserve ordering when it encodes sequence/priority.
- Preserve structure by default (Markdown primitives, lists, code fences); reshape only when it improves scan-clarity and does not change meaning.
- Default to minimal surface area: delete > reorder > substitute; add only to prevent ambiguity.
- Prefer consistency over variety: reuse the same term for the same concept.

## Use when
- The user asks to rewrite/reword/rephrase, tighten language, or shorten text.
- Text is verbose/repetitive or slow to scan (<30s) and meaning must stay intact.
- Names/titles/labels/headings need refinement or renaming.

## Not for
- Operational workflows (scope minimization, validation checklists, incident analysis, code review) unless the user explicitly requests a wording/naming rewrite.

## Motto
Precision through sophistication, brevity through vocabulary, clarity through structure.
- Do not print the motto unless the user explicitly invokes `$logophile` or asks for it.
- If printed, print it once per conversation (single line), then proceed.

## Output
- fast (default): revised text only; no preamble, no recap, no commentary (beyond any required host wrapper).
- annotated: revised text + `Edits:` bullets (lexical; structural; meaning-safety).
- delta: minimal-diff rewrite in a `diff` block; only if asked or reduction > 40% (words/chars).
- naming tasks: return 3-7 candidates (best first) unless the user asks for a single name.

## Examples

### fast
Input:
```text
At this point in time, we are able to proceed.
```

Output:
```text
Now we can proceed.
```

### annotated
Input:
```text
We think the issue is probably due to cache configuration.
```

Output:
```text
The issue is likely due to cache configuration.
```
Edits:
- lexical: removed filler hedges; kept uncertainty.
- meaning-safety: did not increase certainty.

### delta
Input:
```text
In order to proceed, we need to verify access to staging.
```

Output:
```diff
-In order to proceed, we need to verify access to staging.
+To proceed, verify access to staging.
```

### naming
Input:
```text
Things to Do Before Release
```

Output:
```text
Pre-Release Checklist
Release Prep
Release Readiness
Pre-Release Tasks
```

## Inputs (ask only if blocked)
Fields: must_keep; must_not_change; tone; audience; length_target; format; keywords_include; keywords_avoid; structure.
Defaults: must_keep=all facts/numbers/quotes/code/identifiers; must_not_change=obligations/risks/scope/uncertainty/agency; tone=original; audience=implied; format=preserve; structure=preserve; length_target=min safe.

## Workflow (Distill -> Densify -> Shape -> Verify)
- Distill: write a 1-sentence intent; mark must-keep tokens; identify obligations, risks, uncertainty markers, and responsible actors.
- Densify: delete filler; verbify nominalizations; unify terminology; replace vague verbs/adjectives with precise ones (see ladder).
- Shape: lead with action/result; keep sentences atomic; parallelize lists; remove ambiguous pronouns ("this/that") by naming the referent; prefer punctuation over scaffolding.
- Verify: meaning unchanged; re-check semantic hotspots (negation, modality, numbers/units, comparatives, conditionals, scope words like only/at least, agency/ownership); required tokens + formatting preserved.

## Naming mode (when the task is renaming)
- Goal: shorter, more specific, consistent with existing conventions.
- Output: 3-7 candidates; put the best first; keep each <= 3 words unless the domain requires more.
- Rubric: name the axis (what differs?), then the object; avoid "util/manager/stuff"; avoid novel abbreviations; reuse existing terms.

## Elevation (precision ladder)
- Step: vague word -> axis (what changes?) -> exact verb/property -> object.
- Axes: correctness | latency/throughput | cost | reliability | security | privacy | UX | scope | consistency.
- Swaps (only if true): improve->simplify/stabilize/accelerate/harden; handle->parse/validate/normalize/route/retry/throttle; robust->bounded/idempotent/deterministic/fail-closed.
- Term-of-art rule: use 1 domain term if it is standard for the audience and replaces >= 3 tokens; otherwise keep the phrase.

## High-ROI compressions
- in order to -> to; due to the fact that -> because; at this point in time -> now; is able to -> can.
- there is/are -> concrete subject + verb.
- nominalization -> verb (conduct an analysis -> analyze).
- delete: throat-clearing, apologies, self-reference, empty intensifiers.
- token-aware: prefer short, common words; digits + contractions if tone allows.
