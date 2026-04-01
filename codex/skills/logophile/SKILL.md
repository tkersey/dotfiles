---
name: logophile
description: "Precision rewrites + naming: replace vague phrasing with sharper wording before generic tightening, while preserving meaning. Triggers: `$logophile`, rewrite/reword/rephrase, tighten/sharpen/compress wording, choose final wording/phrasing, rename titles/labels/headings/skill names. In operational turns, use only when wording or naming output is explicitly requested."
---

# Logophile

## Intent
Replace generic, bloated phrasing with shorter, sharper phrasing without semantic drift.

## Contract (invariants)
- Preserve meaning, obligations (must/should/may), uncertainty, agency, and sequence.
- Preserve must-keep tokens: numbers, proper nouns, quotes, code/identifiers, paths/flags/URLs.
- Prefer substitution before deletion or reordering. A vague survivor is suspect if a safer, sharper phrase exists.
- Precision can beat brevity and register when it is more exact for the audience and local context.
- Context beats lexicon default. Use the lexicon as a strong default, not as hard law.
- No thesaurus drift: if you cannot name the precision gain, do not swap the phrase.
- Do not force one canonical repo term for every concept; prefer the most exact phrase for the local text.
- Preserve structure by default (Markdown primitives, lists, code fences); reshape only when scan-clarity improves without changing meaning.
- `fast` mode returns revised text only. No `Mode:`, no motto, no recap, no commentary.
- `annotated` mode must call out major substitutions explicitly.

## Use when
- The user asks to rewrite, reword, rephrase, tighten, sharpen, compress, or choose final wording.
- Text is verbose, vague, repetitive, or full of generic verbs/nouns that should become more exact.
- Names, titles, labels, headings, or skill names need refinement.
- Another skill explicitly needs a wording pass; compose with `$logophile` directly instead of assuming hidden style policy.

## Not for
- Operational workflows, scope decisions, validation checklists, incident analysis, or code review unless the user explicitly requests wording or naming help.
- Hidden default rewriting for all skills or all outputs in the workspace.
- Cases where a sharper term would overstate certainty, change ownership, or smuggle in repo jargon that the surrounding text does not support.

## Motto
Precision through sophistication, brevity through vocabulary, clarity through structure.
- Do not print the motto unless the user explicitly invokes `$logophile` or asks for it.
- If printed, print it once per conversation and never in `fast` mode.

## Output
- `fast` (default): revised text only.
- `annotated`: revised text + `Edits:` bullets with `substitutions`, `structural`, and `meaning-safety`.
- `delta`: minimal-diff rewrite in a `diff` block; use when asked or when reduction is large enough that the diff is clearer than prose.
- naming tasks: return 3-7 candidates (best first) unless the user asks for a single name.

## Examples

### fast
Input:
```text
We should iterate on improvements to the skill until it gets better.
```

Output:
```text
Find accretive changes to the skill until the contract is tighter.
```

### annotated
Input:
```text
We need to handle malformed inputs better.
```

Output:
```text
We need to reject malformed inputs fail-closed.
```
Edits:
- substitutions: `handle` -> `reject`; `better` -> `fail-closed`.
- structural: removed the generic helper phrase.
- meaning-safety: kept the same obligation and scope.

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
Defaults: must_keep=all facts/numbers/quotes/code/identifiers; must_not_change=obligations/risks/scope/uncertainty/agency; tone=original; audience=local context; format=preserve; structure=preserve; length_target=min safe.

## Workflow (Distill -> Detect -> Substitute -> Shape -> Verify)
- Distill: write a 1-sentence intent; mark must-keep tokens; identify obligations, risks, uncertainty markers, responsible actors, and audience.
- Detect: mark vague verbs, vague nouns, weak modifiers, generic process phrases, scaffolding, and unclear pronouns.
- Substitute: replace the weakest phrases first using [precision_lexicon.md](references/precision_lexicon.md). If no sharper phrase is clearly correct, keep the original wording.
- Shape: tighten syntax after substitutions land; prefer shorter scaffolding only when the sharper phrase is already in place.
- Verify: re-check semantic hotspots (negation, modality, numbers/units, comparatives, conditionals, scope words like `only`/`at least`, agency/ownership) and confirm required tokens + formatting survive.

## Naming mode (when the task is renaming)
- Goal: shorter, more specific, and more distinctive.
- Output: 3-7 candidates; put the best first; keep each <= 3 words unless the domain requires more.
- Rubric: name the axis, then the object; avoid `util`, `manager`, `stuff`, or novelty abbreviations unless the surrounding repo already uses them.

## Precision policy
- Prefer phrase upgrades over cosmetic synonym swaps.
- Ask: what got more exact? Valid gains include scope, ownership, failure behavior, evidence, sequence, or action type.
- Allowed sharper terms in this repo include `accretive`, `fail-closed`, and `prove` when they are more exact than the generic phrase they replace.
- Do not force those terms when nearby text points to a different, more exact phrase.
- Keep the lexicon small, sharp, and revisable; bad mappings should be pruned quickly.

## Resources
- [precision_lexicon.md](references/precision_lexicon.md): guarded phrase replacements and context rules.
- [probe_cases.md](references/probe_cases.md): acceptance probes for substitutions, output shape, and safety.
- [composition.md](references/composition.md): how other skills should compose with `$logophile` explicitly.
