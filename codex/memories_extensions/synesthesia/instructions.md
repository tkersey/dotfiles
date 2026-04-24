# Synesthesia memory extension

Use this extension only during Codex memory consolidation. It interprets evidence about the user's synesthetic software-reasoning preferences; it is not a runtime prompt and is not a replacement for `AGENTS.md` or the existing `synesthesia` skill.

## Source contract

This extension represents durable preferences, stable mappings, reusable heuristics, failure shields, and repo-scoped vocabulary for synesthetic software reasoning.

Its job is to help Codex remember:

- when the synesthetic lens is useful,
- when it should stay dormant,
- which sensory mappings are user-endorsed and stable,
- how sensory language must translate back into engineering language,
- which repo-specific metaphors or vocabularies should remain local,
- which failure modes to avoid when using this style,
- when to route into the `synesthesia` skill.

`instructions.md` is classification guidance, not evidence. Do not promote a mapping merely because it appears in this file or in the skill. Promote only from active consolidation evidence: user messages, corrections, repeated accepted outputs, learnings rows, rollout summaries, or other durable evidence.

If no durable signal is available, make no memory change.

## Core contract to preserve when evidenced

These rules are load-bearing. Promote them when the evidence shows the user wants them remembered, and otherwise leave them in the skill rather than duplicating them into memory.

- Synesthetic reasoning is an available diagnostic lens, not a mandatory output style.
- Metaphor is never evidence.
- Every useful metaphor must translate back into concrete engineering implications.
- Literal technical correctness outranks sensory style.
- Strong analysis pattern: literal read -> sensory render -> dissonances -> engineering translation -> recommended changes.
- For implementation work, use the lens briefly only if it improves decisions, then execute literally.

## Promotion gate

Promote a candidate only when all four checks pass:

1. Evidence: the signal comes from user endorsement/correction, repeated use, a tagged learning, or clear acceptance in a task outcome.
2. Stability: it is likely to apply beyond the single sentence/session where it appeared.
3. Utility: it improves future routing, diagnosis, communication, or failure avoidance.
4. Reversibility: the sensory phrase can be translated into a concrete technical pattern.

After the gate passes, promote when at least one is true:

- the user explicitly marks it as durable, such as “remember this,” “from now on,” “always do this,” or “this is my preference,”
- the same mapping, activation boundary, or workflow recurs across multiple sessions or repos,
- the user corrects a mapping and the correction is clearly intended to persist,
- the pattern saves prompting, correction, retries, explanation time, or skill-routing effort,
- it prevents a recurring failure mode,
- it materially improves when/how the `synesthesia` skill should trigger.

Do not promote a metaphor just because it sounded good once. Assistant-generated metaphors are not durable memory unless the user accepts, repeats, corrects, or operationalizes them.

## Good candidates for durable memory

Promote information like this:

- stable activation boundaries,
- stable non-activation boundaries,
- user-endorsed sensory mappings,
- stable output-format preferences,
- repo-specific metaphor vocabularies that recur,
- reusable diagnostic cues,
- failure shields that prevent decorative or vague metaphor,
- routing cues that say when to use the `synesthesia` skill.

Examples of durable memories:

- Use synesthetic reasoning for architecture review, weird bugs, cohesion/readability critique, performance “feel,” or compare-by-feel analysis.
- Avoid synesthetic framing for exact syntax questions, narrow command execution, security sign-off, legal/compliance interpretation, or literal-only requests.
- The user prefers stable mappings over novelty.
- The user wants sensory language tied to evidence.
- The user wants direct engineering translation every time the sensory layer is used.

## Mapping confidence and scope

Store mappings with the narrowest correct scope:

- `global_default`: repeated or explicitly endorsed across contexts.
- `repo_scoped`: applies to one repo, service, path family, or domain vocabulary.
- `task_family_scoped`: applies to architecture review, debugging, performance triage, onboarding, etc.
- `tentative`: not enough for durable memory; normally skip unless it is useful as an explicit open question.

If a mapping is repo-specific, keep it repo-specific. Do not globalize local vocabulary unless later evidence makes it a cross-repo default.

When candidates conflict, prefer:

1. the latest explicit user instruction,
2. repo-scoped guidance over global guidance for that repo,
3. repeated user-endorsed evidence over single-session impressions,
4. concrete engineering utility over aesthetic vividness.

If a new rule supersedes an old one, preserve only the current rule unless the older one remains a scoped exception.

## Candidate mapping ontology

Use these as classification defaults when reinforced by evidence. This table is not itself evidence and must not be stored as immutable doctrine.

- hot / red / bright -> churn, contention, overloaded responsibilities, hot paths, concentrated risk
- cold / blue / quiet -> waiting, latency, passive complexity, distant dependencies, hidden lag
- flicker / stutter / static -> race conditions, flakiness, timing sensitivity, intermittent corruption
- muddy / bleeding colors -> mixed concerns, boundary leakage, coupled abstractions
- sharp / glassy / brittle -> unforgiving APIs, edge-case fragility, low error tolerance
- heavy / dense / gravitational -> dependency weight, slow builds, cognitive load, over-abstraction
- hollow / echoing -> indirection without value, ceremony without payoff
- smooth / clean geometry -> coherent interfaces, predictable data flow, stable testability
- noise / clash / dissonance -> naming inconsistency, branching sprawl, duplicated logic, conflicting invariants
- long corridor / drag / distance -> serialized waits, chatty calls, amplified latency
- sticky / viscous -> stateful coupling, hidden caches, mutation-heavy logic, hard rollback

The user may refine, replace, or scope any mapping.

## What not to preserve

Do not preserve:

- one-off poetic phrases,
- vivid but non-reusable metaphors,
- transient bugs or current incident details,
- branch names, issue ids, temporary task state, or sprint context,
- raw chat chronology,
- speculative assumptions about the user's taste,
- security-sensitive material,
- secrets, credentials, tokens, or private keys,
- repo-local metaphors that have not proven durable,
- the full `synesthesia` skill procedure.

A sentence like “this payment service felt like wet cardboard today” is not durable memory. A rule like “for payment-service latency chains in this repo, the user likes `long corridor` to mean serialized waits” can be durable memory if repeated or explicitly endorsed.

## Compression rules

Summarize aggressively. Do not copy raw session notes, long examples, or generated prose into Codex memory.

Prefer compact rules:

- `When X, use the synesthetic lens briefly because it surfaces Y.`
- `In repo R/path P, metaphor M means technical pattern T.`
- `Use skill synesthesia for trigger family K; translate results into engineering actions.`
- `Avoid sensory framing for task family N unless the user asks for it.`

Preserve only the minimum retrieval anchors needed:

- repo name,
- service or path family,
- stable mapping tag,
- failure pattern,
- exact trigger phrase,
- related skill name,
- learning id when available.

Keep examples and history in the underlying evidence artifacts, not memory.

## Artifact targeting

Follow the base memory schema and update existing task groups when possible.

### `memory_summary.md`

Put only compact, always-useful defaults here:

- activation boundaries,
- non-activation boundaries,
- “metaphor is never evidence,” when evidenced as a durable user preference,
- the requirement to translate sensory observations back into engineering language,
- the default routing rule toward the `synesthesia` skill.

Do not paste the mapping ontology into `memory_summary.md`.

### `MEMORY.md`

Put richer operational guidance here:

- stable mapping tables that are evidence-backed,
- repo-specific vocabularies,
- reusable diagnostic cues,
- failure shields,
- nuanced routing notes,
- scoped exceptions.

Use the required `# Task Group` structure from the base consolidation prompt. Keep mapping bullets compact and scoped.

### `skills/*`

Do not recreate the existing `synesthesia` skill in memory. The skill owns the full runtime procedure.

Create or update a memory-root skill only if repeated evidence shows a new reusable sub-workflow beyond the current skill, for example:

- a repeatable log-to-rhythm triage workflow,
- a repo-specific architecture color-mapping workflow,
- a stable compare-by-feel review procedure with a proven verification checklist.

If the pattern is useful but not yet strong enough for a skill, keep it as a concise `MEMORY.md` note.

## Cross-extension handling

- If a `learnings` row reinforces a synesthetic preference or mapping, consolidate the durable signal here and avoid duplicating it in the learnings memory.
- If a `learnings` row is a general workflow failure shield with no sensory preference, let the learnings extension own it.
- If both extensions point to the same durable rule, keep one memory entry and include the most useful retrieval anchor, such as the learning id, repo, path, or trigger phrase.

## Routing guidance

Codex memory should help answer:

- does this task benefit from the synesthetic lens,
- what default boundaries apply,
- which stable mappings should be reused,
- what failure mode should be avoided,
- which repo-local vocabulary is relevant,
- when should the `synesthesia` skill be preferred.

Use durable memory to route into the skill. Do not duplicate the skill's full working instructions.

## Failure modes to guard against

Promote concise shields against recurring mistakes:

- using sensory language without concrete technical translation,
- overusing metaphor on literal tasks,
- switching mappings too often,
- sounding artistic instead of diagnostic,
- globalizing a repo-local metaphor,
- storing one-off clever phrases as durable preferences,
- letting the sensory layer replace testing, debugging, profiling, or verification,
- treating assistant-generated metaphors as user preference without user evidence.

## Output preference for consolidation

When consolidating, write plain operational memory. Do not write the memory itself in lush metaphor.

Good durable memory is:

- compact,
- scoped,
- reusable,
- evidence-aware,
- easy for future Codex sessions to apply.

If a candidate memory does not clearly improve future behavior, skip it.
