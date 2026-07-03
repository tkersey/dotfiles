---
name: logophile
description: "Precision language and doctrine compiler: sharpen wording, names, labels, headings, PR replies, commit/PR text, docs, explanations, and agent doctrine stacks without semantic drift. Trigger for wording, naming, terminology, phrasing, language polish, final copy, doctrine words, mode names, operator naming, human-facing text, or finding words that activate better agent behavior. Not for ordinary implementation, verification, code review, orchestration, or machine-consumed artifacts unless wording/naming/doctrine output is requested."
---

# Logophile

## Intent

Replace generic, bloated, or under-specified language with shorter, sharper phrasing without semantic drift.

For doctrine work, act as a **doctrine compiler**: choose words that activate useful agent behavior, cash them out into artifacts, and make the final doctrine block copy-pasteable.

`logophile` is a language-surface rail. It may be used implicitly for human-facing wording surfaces, but it must not silently change code behavior, operational scope, or machine-consumed syntax.

## Core contract

- Preserve meaning, obligations (`must` / `should` / `may`), uncertainty, agency, sequence, risk, scope, and ownership.
- Preserve must-keep tokens: numbers, proper nouns, quotes, code, identifiers, paths, flags, URLs, schemas, and protocol literals.
- Prefer substitution before deletion or reordering. A vague survivor is suspect if a safer, sharper phrase exists.
- Precision can beat brevity and register when it is more exact for the audience and local context.
- Context beats lexicon default. Use the lexicon as a strong default, not hard law.
- No thesaurus drift: if you cannot name the precision gain, do not swap the phrase.
- Preserve structure by default: Markdown primitives, lists, code fences, tables, YAML/TOML/JSON shape, and quoted blocks.
- Reshape only when scan-clarity improves without changing meaning or copy-paste safety.
- Do not force one canonical repo term for every concept; prefer the most exact phrase for the local text.
- Do not alter code semantics, identifiers, paths, flags, schemas, machine-consumed artifacts, or operational decisions unless the user explicitly asks for wording, naming, or doctrine help on that surface.

## Use when

- The user asks to rewrite, reword, rephrase, tighten, sharpen, compress, polish, or choose final wording.
- The task asks for names, titles, labels, headings, skill names, subagent names, mode names, doctrine words, or doctrine stacks.
- The requested output includes human-facing text: PR replies, review acknowledgements, rebuttals, commit messages, PR titles/bodies, release notes, docs, README prose, CLI help, error messages, user-facing explanations, summaries, or final copy.
- Another skill produces a human-facing action list, rebuttal, summary, agenda, route receipt, actuation receipt, ablation receipt, or closure bottom line that should be sharper before the user sees or pastes it.
- The user asks for “rigor words,” “doctrine words,” “mode words,” “word stacks,” “operator words,” “compressed rubrics,” or words that light up better agent behavior.

## Not for

- Ordinary implementation, verification, review, orchestration, incident analysis, or scope decisions unless wording, naming, or doctrine output is part of the requested result.
- Hidden rewriting of all outputs in the workspace.
- Changing code, identifiers, schemas, flags, paths, TOML/YAML/JSON fields, or protocol terms for style.
- Cases where a sharper term would overstate certainty, change ownership, alter obligations, or smuggle in repo jargon the surrounding text does not support.

## Motto

Precision through sophistication, brevity through vocabulary, clarity through structure.

- Do not print the motto unless the user explicitly invokes `$logophile` or asks for it.
- If printed, print it once per conversation and never in `fast` mode.

## Output modes

- `fast` (default for simple rewrite): revised text only. No `Mode:`, no motto, no recap, no commentary.
- `annotated`: revised text + `Edits:` bullets with `substitutions`, `structural`, and `meaning-safety`.
- `delta`: minimal-diff rewrite in a `diff` block; use when asked or when reduction is large enough that diff is clearer than prose.
- `naming`: return 3-7 candidates, best first, unless the user asks for one.
- `doctrine-fast`: recommended stack + prompt-ready doctrine block only.
- `doctrine`: task reading, pressure map, recommended stack, operator roles, cash-out artifacts, near misses, variants, words to avoid, and final doctrine block.
- `doctrine-annotated`: same as `doctrine`, plus per-word rationale and collision analysis.

Accept “rigor words” as user phrasing for doctrine mode. Do not expose old `rigor-*` mode names; `doctrine` is canonical.

## CLI-tail-weighted output

- In multi-part outputs, put the most actionable wording at the end.
- In naming outputs, end with `Best Pick:`.
- In doctrine outputs, end with `Use This:` and a copy-pasteable doctrine block, followed by `Operationalization:`.
- For PR/comment/reply outputs, end with the final paste-ready text.
- In `fast` mode, keep revised-text-only for the artifact itself.

## AGENTS.md compatibility

- If repo-level `AGENTS.md` requires a surrounding response wrapper such as `Echo:`, preserve that wrapper outside generated text.
- The `fast` revised-text-only contract applies to the rewritten artifact, not necessarily to the entire assistant chat response.
- Do not include repo response wrappers inside PR bodies, commit messages, emails, generated files, machine-consumed text, or copy-paste artifacts.

## Inputs (ask only if blocked)

Fields: `must_keep`, `must_not_change`, `tone`, `audience`, `length_target`, `format`, `keywords_include`, `keywords_avoid`, `structure`.

Defaults:

- `must_keep`: all facts, numbers, quotes, code, identifiers, paths, flags, URLs, and schema fields.
- `must_not_change`: obligations, risks, scope, uncertainty, agency, ownership, and ordering.
- `tone`: preserve original unless the user asks otherwise.
- `audience`: infer from local context.
- `format`: preserve.
- `structure`: preserve.
- `length_target`: minimum safe.

Additional doctrine fields: `task`, `stakes`, `target_agent`, `failure_pressures`, `stack_size`, `mode_strength`, `words_must_include`, `words_must_avoid`, `artifact_target`, `desired_behavior_shift`.

Doctrine defaults:

- `stakes`: infer.
- `target_agent`: local context.
- `failure_pressures`: infer.
- `stack_size`: 3-6 words.
- `mode_strength`: balanced.
- `artifact_target`: infer from task.
- `desired_behavior_shift`: infer from task.

## Workflow: Distill -> Detect -> Substitute -> Shape -> Verify

- Distill: write a one-sentence intent internally; mark must-keep tokens; identify obligations, risks, uncertainty markers, responsible actors, and audience.
- Detect: mark vague verbs, vague nouns, weak modifiers, generic process phrases, scaffolding, and unclear pronouns.
- Substitute: replace the weakest phrases first using [precision_lexicon.md](references/precision_lexicon.md). If no sharper phrase is clearly correct, keep the original wording.
- Shape: tighten syntax after substitutions land; prefer shorter scaffolding only when the sharper phrase is already in place.
- Verify: re-check semantic hotspots: negation, modality, numbers/units, comparatives, conditionals, scope words such as `only` / `at least`, agency, ownership, and formatting.

## Naming mode

- Goal: shorter, more specific, and more distinctive.
- Output: 3-7 candidates; put the best first and repeat it at the end as `Best Pick:` for multi-part answers.
- Keep each <= 3 words unless the domain requires more.
- Rubric: name the axis, then the object.
- Avoid `util`, `manager`, `stuff`, vague containers, and novelty abbreviations unless the repo already uses them.
- Prefer names that encode the job, operator, artifact, or success condition, not the plumbing.
- Check doctrine grammar before finalizing: a strong mode name should work in forms like `<word> mode`, `<word> pass`, `<word> ledger`, `<word> receipt`, `<word> gate`, or `<word> doctrine`.

## Doctrine compiler mode

Doctrine mode is not word suggestion. It is operator selection.

A good doctrine word must compile into:

```text
trigger -> operator -> artifact -> receipt -> proof
```

For each recommended word, define:

- **trigger**: when to use it;
- **operator**: what behavior it activates;
- **artifact**: what it produces;
- **receipt**: what proves it fired;
- **failure mode**: what goes wrong if omitted.

A doctrine word is strong when it changes frame, route, proof obligation, owner boundary, deletion/collapse decision, review disposition, actuation path, or closure gate.

A doctrine word is weak when it only changes tone, sophistication, or vibe.

## Doctrine mode

Goal: find semantically dense words that compress a useful operating doctrine for a task.

Treat words as compressed rubrics, not decorative synonyms. Each chosen word must earn its place by adding a distinct procedural gain: failure detection, reasoning discipline, scope control, execution control, verification pressure, routing pressure, or reporting discipline.

### Doctrine constraints

- Choose 3-6 non-overlapping words by default.
- Prefer task-fit over novelty.
- Prefer words that imply checks, constraints, proof obligations, receipts, or execution discipline.
- Reject ornamental, merely high-register, or praise-only words.
- Pair every recommended stack with an unpacked doctrine block; a naked word list is incomplete.
- Do not turn doctrine mode into hidden policy for unrelated operational turns.
- Do not preserve a word merely because it is impressive; preserve it because it activates behavior.

### Actuation test

For every doctrine word, ask:

- What behavior does this word activate?
- What route would it change?
- What artifact does it require?
- What failure mode does it prevent?
- What proof or receipt shows it worked?

Reject the word if it only improves tone, sophistication, or rhetorical force.

### Receipt bias

Prefer doctrine words that naturally imply a receipt.

Strong doctrine words tend to answer:

- What must be named?
- What must be counted?
- What must be proved?
- What must be rejected?
- What state changed?
- What route was selected?
- What surface was removed?
- What remains open?

Weak doctrine words merely make the prose sound smarter.

### Mode collision check

Before finalizing a doctrine stack, check for collisions:

- Does one word push preservation while another authorizes removal?
- Does one word push exhaustive search while another demands direct action?
- Does one word imply local minimality while another implies structural rewrite?
- Does one word preserve behavior that the task intends to retire?
- Does one word name a proof relation while another names a reduction operator?

Resolve collisions in the doctrine block. Example: `isomorphic` is a strict preservation relation, not a reduction operator; use `refinement-preserving` when valid behavior is preserved while obsolete, invalid, or unrequired behavior may disappear.

### Doctrine grammar

Prefer doctrine words that work naturally in these slots:

- `<WORD> mode`
- `<WORD> pass`
- `<WORD> ledger`
- `<WORD> receipt`
- `<WORD> gate`
- `<WORD> doctrine`

Use:

- adjectives for posture: `accretive`, `ablative`, `forensic`, `canonical`;
- gerunds for active operators: `actuating`, `reifying`, `winnowing`, `quotienting`, `rebaselining`;
- nouns for artifacts: `witness`, `ledger`, `receipt`, `kernel`, `certificate`.

A verb may be excellent inside the instruction but weaker as the doctrine label. Example: use `ACTUATING` as the mode and `actuate the lever` as the command.

### Doctrine workflow: Read -> Pressure Map -> Candidate Bank -> Stack -> Unpack -> Verify

- Read: classify the task family, audience, stakes, and likely failure surfaces.
- Pressure Map: rank the dominant failure pressures.
- Candidate Bank: generate semantically dense words that encode procedural behavior, not just tone.
- Stack: choose 3-6 non-overlapping words; include different roles when useful: failure, reasoning, execution, verification, routing, reduction, reset, or knowledge extraction.
- Unpack: translate each chosen word into observable instructions.
- Verify: remove overlap, ornament, jargon drift, and mode collisions; confirm the doctrine block would change behavior, not merely style.

### Doctrine output shape

Use this for `doctrine` / `doctrine-annotated`:

```md
Task Reading
Dominant Failure Pressures
Recommended Stack
Operator Roles
Cash-Out Artifacts
Why These Words
Near Misses
Stricter Variant
Lighter Variant
Words to Avoid
Use This:
[copy-pasteable doctrine block]
Operationalization:
[artifact/gate/ledger/receipt produced]
```

In `doctrine-fast`, return only:

```md
Recommended Stack
Use This:
[copy-pasteable doctrine block]
Operationalization:
[artifact/gate/ledger/receipt produced]
```

### Near misses

Use `Near Misses` to explain why adjacent words were rejected.

Examples:

- `actuate`: strong verb, weaker doctrine label; prefer `actuating` as mode.
- `tractable`: useful state, weaker operator; prefer `tractabilizing` when the task is problem-shaping.
- `isomorphic`: strong proof relation, not a reduction objective; use `winnowing`, `quotienting`, or `ablative` for reduction.
- `rigor`: broad effect, weak artifact; replace with the specific doctrine operator.

## Doctrine alpha vocabulary policy

Doctrine mode should optimize for words that create executable artifacts.

Prefer words and phrases that naturally imply ledgers, gates, witnesses, maps, receipts, certificates, or selection rows:

- `fixed-point` -> reopenable stop condition;
- `governing invariant` -> owner boundary and invariant-defending proof;
- `canonical witness` -> one trusted proof path tied to the canonical owner;
- `resolve-selection` -> act / validate-only / proof-only / no-change / blocked map;
- `unwitnessed guarantee` -> missing proof object or claim to downgrade;
- `illegal inhabitant` -> impossible state admitted by a representation or producer;
- `partial handler` -> eliminator that is not total over the intended domain;
- `tail proof` -> CLI-visible proof and next action at the bottom of output;
- `actuating` -> Actuation Receipt with target state, control point, lever, action, proof, and next bottleneck;
- `ablative` -> Ablation Activation Receipt plus Ablation Ledger or evidence-backed `not-required`;
- `winnowing` -> Winnowing / Reduction Certificate with factors, retained obligations, removed factors, and recomposition proof;
- `quotienting` -> quotient relation, congruence witnesses, merged distinctions, and retained distinction witnesses;
- `rebaselining` -> Baseline Receipt tying current authority, stale assumptions, valid prior work, invalidated artifacts, and next action;
- `reifying` -> behavior algebra: constructors, payloads, total interpreter, and preservation proof;
- `forensic` -> provenance map separating observations, claims, memories, summaries, speculation, and evidence strength.

Demote standalone `rigor`, ornamental `adversarial`, isolated `mechanistic`, and any dense word that cannot name its artifact.

In doctrine output, add a final `Operationalization:` line that names the exact artifact the doctrine should produce: ledger, gate, validator, proof receipt, truth-owner graph, resolve-selection map, route receipt, actuation receipt, reduction certificate, behavior algebra, or closure criterion.

## Precision policy

- Prefer phrase upgrades over cosmetic synonym swaps.
- Ask: what got more exact? Valid gains include scope, ownership, failure behavior, evidence, sequence, obligation, action type, proof relation, route, or artifact.
- Allowed sharper terms in this repo include `accretive`, `ablative`, `actuating`, `rebaselining`, `winnowing`, `quotienting`, `reifying`, `forensic`, `fail-closed`, `unwitnessed`, `ill-typed`, `canonical`, `fixed-point`, and `prove` when they are more exact than the generic phrase they replace.
- Do not force those terms when nearby text points to a different, more exact phrase.
- Keep lexicons small, sharp, and revisable; prune bad mappings quickly.

## Composition

Use `logophile` as a final language pass when another workflow produces human-facing language:

- after review adjudication through `$review-fold`, sharpen reviewer replies, rebuttals, acknowledgements, disposition summaries, and review-comment Bottom Lines.
- after `fixed-point-driver`, sharpen Route Receipts, Fixed-Point Bottom Lines, closure notes, and PR-facing summaries.
- after ablation-heavy workflows, ensure `ablation: not-required`, Ablation Ledger, keep/delete/canonicalize decisions, and Ablative Isomorphism Cards are precise rather than decorative.
- after `$actuating`, sharpen the Actuation Bottom Line so the lever, action, proof, and next bottleneck are unmistakable.
- after `$seq`, sharpen forensic/cartographic summaries without losing provenance.
- after bounded implementation workflows, sharpen PR-facing final summaries, closure notes, and handoffs.
- before finalizing skill names, subagent names, mode names, doctrine stacks, headings, or labels.

Do not use `logophile` to replace implementation, review, adjudication, or closure work.

## Resources

- [precision_lexicon.md](references/precision_lexicon.md): guarded phrase replacements and context rules.
- [doctrine_word_bank.md](references/doctrine_word_bank.md): doctrine words and type-theoretic, reduction, reset, action, and knowledge-extraction vocabulary.
- [task_pressure_map.md](references/task_pressure_map.md): task-to-pressure defaults.
- [doctrine_compiler.md](references/doctrine_compiler.md): operator/artifact/receipt model for doctrine synthesis.
- [probe_cases.md](references/probe_cases.md): acceptance probes for rewriting, naming, and safety.
- [doctrine_probe_cases.md](references/doctrine_probe_cases.md): doctrine-mode trigger and quality probes.
- [composition.md](references/composition.md): composition guidance with other skills.
