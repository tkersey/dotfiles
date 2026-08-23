---
name: logophile
description: "Compile decision-bearing language—names, labels, commands, contracts, prompts, doctrine, error messages, and public claims—into precise wording without semantic drift. Invoke implicitly only when wording itself can change behavior, interface, authority, obligation, or interpretation. Explicit invocation may rewrite supplied text. Never run as a generic final pass."
---

# Logophile

## Intent

Compile language whose wording is part of the system.

Decision-bearing language includes names, commands, labels, prompts, doctrine,
public promises, contracts, recovery-directing errors, and other text whose
interpretation changes behavior, authority, obligation, interface use, or a
durable public meaning.

Ordinary prose quality is baseline model competence. Do not invoke `$logophile`
implicitly merely because text is human-facing, important, long, or final.

## Decision-bearing routing gate

Implicit invocation requires all three:

1. A concrete wording candidate or language decision exists now.
2. Changing only the wording, while holding the underlying facts constant,
   could materially change behavior, interface use, authority, obligation, or
   interpretation.
3. The language surface is stable, public, contractual, recovery-directing, or
   intentionally behavior-steering.

If any condition fails, do not invoke.

Explicit `$logophile` invocation bypasses the implicit gate for ordinary
rewriting, copyediting, compression, naming, terminology comparison, doctrine,
persona, or activation-language work.

## Explicit triggers

Use when the user explicitly asks to:

- rewrite, reword, tighten, sharpen, compress, polish, or choose final wording;
- name a skill, mode, role, state, artifact, command, API surface, or concept;
- compare terminology or adjudicate an old-versus-new wording change;
- find doctrine words, activation phrases, personas, or doctrine stacks;
- produce final PR, release, documentation, error, contract, or prompt copy.

## Implicit triggers

Use only for a live decision-bearing surface such as:

- public command, mode, role, state, or artifact names;
- API-visible labels, headings, errors, deprecations, or compatibility text;
- prompts and activation phrases intended to steer behavior;
- contract language where modality, scope, ownership, or authority matters;
- public promises, guarantees, dispositions, or claims;
- stable names for proofs, transitions, invariants, or interfaces.

## Non-triggers

Do not invoke implicitly for:

- generic final responses;
- routine implementation handoffs, landing reports, or status updates;
- factual bullet lists or mechanically generated summaries;
- ordinary code review, verification, or analysis with no wording decision;
- internal tool narration or progress commentary;
- machine-consumed syntax, identifiers, paths, flags, schemas, or protocol
  literals;
- a final pass merely because text will be read by a human.

## Core contract

- Preserve facts, obligations (`must` / `should` / `may`), uncertainty, agency,
  sequence, risk, scope, ownership, and authority.
- Preserve must-keep tokens: numbers, proper nouns, quotations, code,
  identifiers, paths, flags, URLs, schemas, and protocol literals.
- Prefer substitution before deletion or reordering. If no sharper wording is
  clearly safer and more exact, retain the incumbent.
- Context beats lexicon defaults. Do not force repository vocabulary when local
  wording is more precise.
- No thesaurus drift: every substitution must have a named precision gain.
- Preserve Markdown and machine-readable structure unless the user asks to
  reshape it and the result remains copy-paste safe.
- Never convert copyediting into a policy, product, architecture, review, or
  operational decision.
- Never silently rename code identifiers or modify machine-consumed artifacts.
- Load only the reference family required by the current language decision.
- Do not announce or manufacture a pass when no material language decision
  exists.
- `no change` is a successful result.

## Valid terminal results

Return exactly the smallest result the task needs:

```text
final artifact
candidate set
minimal delta
no change
```

Do not create a receipt merely to prove that `$logophile` ran. Use a receipt or
comparison artifact only when correctness, handoff, publication, authority, or
a behavioral-upgrade claim depends on it.

## Output modes

- `fast`: final artifact only; for an already optimal incumbent, return
  `no change`.
- `annotated`: final artifact plus concise substitution, structural, and
  meaning-safety notes.
- `delta`: minimal unified diff when a delta is clearer than a full artifact.
- `naming`: 3-7 candidates, best first, ending with `Best Pick:`.
- `persona`: mode, persona noun, core command, artifact, and near misses.
- `activation-fast`: 1-5 terse phrases, strongest first, no explanation.
- `activation-annotated`: phrase, intended shift, best use, and shadow risk.
- `activation-stack`: smallest non-overlapping phrase sequence plus its
  progression.
- `doctrine-fast`: recommended stack and copy-pasteable doctrine only.
- `doctrine`: task pressure, stack, operator roles, artifacts when needed, near
  misses, and final doctrine block.
- `doctrine-annotated`: `doctrine` plus per-word rationale and collision
  analysis.
- `upgrade-fast`: `retain | replace | specialize | pair | sequence | benchmark`
  plus final runtime wording.
- `upgrade-annotated`: full incumbent-versus-candidate behavioral verdict.
- `upgrade-benchmark`: matched benchmark plan or blinded verdict from supplied
  outputs.

Accept “rigor words” as user phrasing for doctrine mode. `doctrine` remains the
canonical mode name.

## CLI-tail-weighted output

- Put the most actionable wording at the end of multi-part outputs.
- End naming outputs with `Best Pick:`.
- End persona outputs with `Use This Persona:`.
- End activation outputs with the shortest effective phrase or stack.
- End doctrine outputs with `Use This:` and, only when required,
  `Operationalization:`.
- End PR, comment, reply, and contract work with the paste-ready artifact.

## AGENTS.md compatibility

- Preserve any required outer response wrapper, such as `Echo:`, outside the
  generated artifact.
- Never place repository response wrappers inside PR bodies, commit messages,
  emails, generated files, schemas, or other copy-paste artifacts.

## Inputs

Ask only when blocked. Relevant fields are:

```text
must_keep
must_not_change
tone
audience
length_target
format
keywords_include
keywords_avoid
structure
```

Default to preserving the source tone, format, structure, facts, obligations,
uncertainty, agency, scope, ownership, and ordering.

## Rewrite workflow

```text
DISTILL -> DETECT -> SUBSTITUTE -> SHAPE -> VERIFY
```

- **Distill:** identify intent, audience, must-keep tokens, obligations, risks,
  uncertainty, agency, and ownership.
- **Detect:** locate vague verbs and nouns, weak modifiers, bloated scaffolding,
  overloaded terms, and unclear references.
- **Substitute:** replace the weakest phrase first. Keep the incumbent when no
  candidate is clearly more exact.
- **Shape:** tighten syntax only after the semantic substitution is safe.
- **Verify:** re-check negation, modality, numbers, units, comparatives,
  conditionals, scope, agency, ownership, and formatting.

Use [precision_lexicon.md](references/precision_lexicon.md) for guarded phrase
replacements and [probe_cases.md](references/probe_cases.md) for baseline
acceptance and routing probes.

## Naming and persona work

- Prefer names that encode the job, operator, artifact, or success condition,
  not plumbing such as `manager`, `helper`, or `processor`.
- Keep names to three words or fewer unless the domain requires more.
- Keep mode and persona distinct: `ADJUDICATIVE` is a mode; `Arbiter` is a
  persona.
- Do not invent a persona noun when the adjective or gerund is clearer.

## Doctrine compiler

Doctrine work is operator selection, not decorative synonym generation.

A formal doctrine word should compile through:

```text
trigger -> operator -> artifact when needed -> proof or stopping condition
```

Activation doctrine uses the lighter path:

```text
phrase -> intended posture -> task fit -> shadow risk
```

- Design activation language expansively; invoke it tersely.
- Do not require an artifact merely to justify a terse phrase.
- Prefer task fit over rarity, register, or apparent sophistication.
- Reject words that change only tone or confidence.
- Preserve the distinct roles in a doctrine stack and check for collisions.

Read [doctrine_compiler.md](references/doctrine_compiler.md),
[doctrine_word_bank.md](references/doctrine_word_bank.md), and
[task_pressure_map.md](references/task_pressure_map.md) for general doctrine
work. Read specialized references only when their trigger is live.

For explicit requests about changing what counts as adjacent, topology,
neighborhood structure, making distant concepts local, or automobile-not-faster-
horses moves, read
[retopologizing_doctrine.md](references/retopologizing_doctrine.md) and
[retopologizing_probe_cases.md](references/retopologizing_probe_cases.md). Treat
`CHANGE WHAT COUNTS AS ADJACENT!!` as the runtime incumbent unless Behavioral
Upgrade adjudication supports replacement.

## Behavioral upgrades

When proposed wording may replace an incumbent that already steers behavior,
read [behavioral_upgrade.md](references/behavioral_upgrade.md) and
[behavioral_upgrade_probe_cases.md](references/behavioral_upgrade_probe_cases.md).

The baseline is the incumbent. Semantic density is evidence, not victory.
`retain`, `specialize`, and `benchmark` are successful outcomes. Do not claim a
behavioral winner from semantics alone.

## Composition boundary

Read [composition.md](references/composition.md) only when another workflow emits
a decision-bearing language surface. Do not add `$logophile` as an ambient
postprocessor for routine summaries, closure notes, status reports, or final
answers.

`$logophile` owns terminology, wording, preservation checks, and human-facing
articulation. It does not execute, review, adjudicate, select architecture,
authorize mutation, verify, or publish.

## Resources

### Core language and routing

- [precision_lexicon.md](references/precision_lexicon.md): guarded phrase
  replacements and context rules.
- [probe_cases.md](references/probe_cases.md): rewrite, naming, routing, and
  semantic-safety probes.
- [composition.md](references/composition.md): conditional composition with
  owning workflows.

### General doctrine

- [doctrine_word_bank.md](references/doctrine_word_bank.md): broad doctrine
  vocabulary and operator distinctions.
- [computer_science_doctrine.md](references/computer_science_doctrine.md): formal
  computer-science terms and proof burdens.
- [task_pressure_map.md](references/task_pressure_map.md): task-to-pressure
  defaults.
- [doctrine_compiler.md](references/doctrine_compiler.md): operator, artifact,
  receipt, and proof model.
- [doctrine-alpha.md](references/doctrine-alpha.md): evidence-backed doctrine
  design principles.
- [doctrine_phrases.md](references/doctrine_phrases.md): terse activation
  language optimized for behavioral leverage per token.
- [doctrine_probe_cases.md](references/doctrine_probe_cases.md): general
  doctrine-mode acceptance probes.

### Behavioral comparison

- [behavioral_upgrade.md](references/behavioral_upgrade.md): incumbent-first
  wording adjudication.
- [behavioral_upgrade_probe_cases.md](references/behavioral_upgrade_probe_cases.md):
  replacement, specialization, and benchmark probes.

### Specialized doctrine families

- [architectonic_doctrine.md](references/architectonic_doctrine.md) and
  [architectonic_probe_cases.md](references/architectonic_probe_cases.md).
- [breakthrough_doctrine.md](references/breakthrough_doctrine.md) and
  [breakthrough_probe_cases.md](references/breakthrough_probe_cases.md).
- [depth_deliberation_doctrine.md](references/depth_deliberation_doctrine.md) and
  [depth_deliberation_probe_cases.md](references/depth_deliberation_probe_cases.md).
- [metanoetic_doctrine.md](references/metanoetic_doctrine.md) and
  [metanoetic_probe_cases.md](references/metanoetic_probe_cases.md).
- [pusillanimity_doctrine.md](references/pusillanimity_doctrine.md) and
  [pusillanimity_probe_cases.md](references/pusillanimity_probe_cases.md).
- [retopologizing_doctrine.md](references/retopologizing_doctrine.md) and
  [retopologizing_probe_cases.md](references/retopologizing_probe_cases.md).
