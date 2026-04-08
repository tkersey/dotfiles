---
name: logophile
description: "Precision rewrites + naming + doctrine synthesis: replace vague phrasing with sharper wording before generic tightening, while preserving meaning; choose names; and derive task-specific rigor words / doctrine stacks when wording, naming, or doctrine output is explicitly requested. Triggers: `$logophile`, rewrite/reword/rephrase, tighten/sharpen/compress wording, choose final wording/phrasing, rename titles/labels/headings/skill names, derive rigor words/modes/word stacks/doctrine for a task. In operational turns, use only when wording, naming, or doctrine output is explicitly requested."
---

# Logophile

## Intent
Replace generic, bloated phrasing with shorter, sharper phrasing without semantic drift. When asked for doctrine, derive semantically dense words that compress a useful operating mode for a task.

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
- In doctrine mode, preserve the task's actual stakes, uncertainty, and scope; do not smuggle in stronger guarantees, stricter obligations, or repo jargon the task does not support.
- In doctrine mode, each selected word must correspond to a distinct procedural gain: failure detection, reasoning discipline, scope control, execution control, or verification pressure.
- Prefer compact stacks over exhaustive dumps; more words usually means more overlap.
- A doctrine stack is incomplete without an unpacked doctrine block.
- Do not silently turn doctrine mode into hidden policy for unrelated operational turns.

## Use when
- The user asks to rewrite, reword, rephrase, tighten, sharpen, compress, or choose final wording.
- Text is verbose, vague, repetitive, or full of generic verbs/nouns that should become more exact.
- Names, titles, labels, headings, or skill names need refinement.
- The user asks for rigor words, doctrine words, mode words, word stacks, compressed rubrics, or wording that will push an agent into a sharper thinking mode.
- Another skill explicitly needs a wording pass or doctrine-word pass; compose with `$logophile` directly instead of assuming hidden style policy.

## Not for
- Operational workflows, scope decisions, validation checklists, incident analysis, or code review unless the user explicitly requests wording, naming, or doctrine help.
- Hidden default rewriting for all skills or all outputs in the workspace.
- Cases where a sharper term would overstate certainty, change ownership, or smuggle in repo jargon that the surrounding text does not support.
- Replacing implementation, review, or orchestration skills with doctrine synthesis.
- Suggesting smart-sounding words that cannot be justified as a real procedural upgrade.

## Motto
Precision through sophistication, brevity through vocabulary, clarity through structure.
- Do not print the motto unless the user explicitly invokes `$logophile` or asks for it.
- If printed, print it once per conversation and never in `fast` mode.

## Output
- `fast` (default): revised text only.
- `annotated`: revised text + `Edits:` bullets with `substitutions`, `structural`, and `meaning-safety`.
- `delta`: minimal-diff rewrite in a `diff` block; use when asked or when reduction is large enough that the diff is clearer than prose.
- naming tasks: return 3-7 candidates (best first) unless the user asks for a single name.
- `doctrine-fast`: recommended stack + prompt-ready doctrine block only.
- `doctrine`: 
  - Task Reading
  - Dominant Failure Pressures
  - Recommended Stack
  - Prompt-Ready Doctrine Block
  - Stricter Variant
  - Lighter Variant
  - Words to Avoid
- `doctrine-annotated`: same as `doctrine` + per-word rationale.
- Backward-compatible aliases:
  - `rigor-fast` -> `doctrine-fast`
  - `rigor` -> `doctrine`
  - `rigor-annotated` -> `doctrine-annotated`

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

### doctrine-fast
Input:
```text
Find the words to push a coding agent toward minimal, verified bug fixes.
```

Output:
```text
unsound
mechanistic
accretive
traceable

Operate in UNSOUND, MECHANISTIC, ACCRETIVE, and TRACEABLE mode.
- Reject unsupported conclusions and surface missing premises.
- Explain the bug as a causal chain before editing.
- Prefer the smallest additive change that fixes root cause.
- Tie claims to tests, logs, diffs, or file evidence.
```

### doctrine-annotated
Input:
```text
Find the doctrine words for a research memo on AI coding agents.
```

Output:
```text
Task Reading
- Produce a public-source research memo for an executive audience.

Dominant Failure Pressures
- shallow source quality
- vague competitive framing
- overclaiming from weak evidence
- bloated synthesis

Recommended Stack
- adversarial
- source-disciplined
- calibrated
- synthetic

Prompt-Ready Doctrine Block
Operate in ADVERSARIAL, SOURCE-DISCIPLINED, CALIBRATED, and SYNTHETIC mode.
- Challenge first-pass claims before accepting them.
- Prefer primary and authoritative sources over commentary.
- Match confidence to evidence and label uncertainty.
- Compress many signals into a concise comparative synthesis.

Stricter Variant
- adversarial
- source-disciplined
- calibrated
- exhaustive

Lighter Variant
- source-disciplined
- calibrated
- concise

Words to Avoid
- insightful
- nuanced
- sophisticated
```
Edits:
- substitutions: selected words that change procedure, not just tone.
- structural: split the answer into pressure map, stack, and doctrine block.
- meaning-safety: kept the task's audience, uncertainty, and evidence burden intact.

## Inputs (ask only if blocked)
Fields: must_keep; must_not_change; tone; audience; length_target; format; keywords_include; keywords_avoid; structure.
Defaults: must_keep=all facts/numbers/quotes/code/identifiers; must_not_change=obligations/risks/scope/uncertainty/agency; tone=original; audience=local context; format=preserve; structure=preserve; length_target=min safe.
Additional doctrine fields: task; stakes; target_agent; failure_pressures; stack_size; mode_strength; words_must_include; words_must_avoid.
Doctrine defaults: stakes=infer; target_agent=local context; failure_pressures=infer; stack_size=4; mode_strength=balanced.

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

## Doctrine mode (when the task is to find thinking-posture words)
- Goal: find semantically dense words that compress a useful operating doctrine for a task.
- Output: 1-3 doctrine stacks, best first; each stack should usually be 3-6 words.
- Rubric:
  - each word must add a distinct procedural gain
  - prefer task-fit over novelty
  - prefer words that imply checks, constraints, action types, or verification pressure
  - avoid generic praise words unless they are made operational by surrounding text
- Treat words as compressed rubrics, not as decorative synonyms.
- Distinguish, when useful:
  - failure-mode words
  - reasoning-mode words
  - execution-mode words
  - verification-mode words
- Reject ornamental, merely high-register, or thesaurus-driven words.
- Pair every recommended stack with an unpacked doctrine block; a naked word list is incomplete.
- Canonical mode name: `doctrine`
- Accepted user aliases: `rigor`, `rigor words`, `rigor mode`, `mode stack`, `doctrine stack`

## Doctrine workflow (Read -> Pressure Map -> Candidate Bank -> Stack -> Unpack -> Verify)
- Read: classify the task family, audience, stakes, and likely failure surfaces.
- Pressure Map: rank the dominant failure pressures using [task_pressure_map.md](references/task_pressure_map.md) as a default, not a hard law.
- Candidate Bank: generate semantically dense words that encode procedural behavior, not just tone, using [doctrine_word_bank.md](references/doctrine_word_bank.md).
- Stack: choose 3-6 non-overlapping words; include different roles when useful (failure, reasoning, execution, verification).
- Unpack: translate each chosen word into an instruction an agent can act on.
- Verify: remove overlap, ornament, and jargon drift; confirm the doctrine block would change behavior, not merely style.

## Precision policy
- Prefer phrase upgrades over cosmetic synonym swaps.
- Ask: what got more exact? Valid gains include scope, ownership, failure behavior, evidence, sequence, or action type.
- Allowed sharper terms in this repo include `accretive`, `fail-closed`, and `prove` when they are more exact than the generic phrase they replace.
- Do not force those terms when nearby text points to a different, more exact phrase.
- Keep the lexicon small, sharp, and revisable; bad mappings should be pruned quickly.
- In doctrine mode, prefer words that imply checks, constraints, action types, or verification pressure.
- In doctrine mode, reject generic praise words (`smart`, `deep`, `thoughtful`, `nuanced`) unless the user explicitly wants tone rather than procedure.

## Resources
- [precision_lexicon.md](references/precision_lexicon.md): guarded phrase replacements and context rules.
- [probe_cases.md](references/probe_cases.md): acceptance probes for substitutions, output shape, and safety.
- [composition.md](references/composition.md): how other skills should compose with `$logophile` explicitly.
- [doctrine_word_bank.md](references/doctrine_word_bank.md): rigor/doctrine words grouped by procedural gain.
- [task_pressure_map.md](references/task_pressure_map.md): task-family defaults for dominant failure pressures.
- [doctrine_probe_cases.md](references/doctrine_probe_cases.md): acceptance probes for doctrine stacks, mode fit, and overlap control.
