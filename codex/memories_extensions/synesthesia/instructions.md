# Synesthesia memory extension

Place this file at:
- `~/.codex/memories_extensions/synesthesia/instructions.md`, or
- `<your-memory-root-sibling>/synesthesia/instructions.md`

Use this file only for Codex memory consolidation.
This is **not** a general runtime prompt and it is **not** a replacement for `AGENTS.md`.

## What this source is

This extension represents durable preferences, stable mappings, reusable heuristics, and repo-scoped vocabulary for **synesthetic software reasoning**.

Its job is to help Codex remember:
- when the synesthetic lens is useful,
- which sensory mappings are stable and worth reusing,
- how to translate sensory language back into engineering language,
- which repo-specific metaphors or vocabularies should stay local,
- which failure modes to avoid when using this style.

`instructions.md` is the only required file for this extension.
Do not assume a sibling `resources/` directory or generated digest exists.
Use durable evidence that is already present in the active memory inputs for the current consolidation run.
Treat raw session notes, transcripts, scratchpads, and chat history as supporting evidence only.
Never edit or rewrite raw source notes from the memory pipeline.

## Goal

Distill this source into durable Codex memory.

Promote only information that will help future sessions:
- automatically route into the existing `synesthesia` skill when appropriate,
- apply the user's stable defaults without extra prompting,
- keep metaphor disciplined and technically useful,
- avoid repeated misunderstandings or over-stylized responses,
- preserve repo-specific vocabulary only where it materially improves work.

If there is no durable signal, make no memory change.

## Core contract to preserve

The following rules are load-bearing and should be promoted aggressively when reinforced:
- Synesthetic reasoning is a **default available lens**, not a mandatory output style.
- Metaphor is **never evidence**.
- Any useful metaphor must translate back into concrete engineering implications.
- Literal technical correctness outranks style.
- Strong output pattern: **literal read -> synesthetic render -> dissonances -> engineering translation -> recommended changes**.
- For implementation work, use synesthetic framing only briefly if it helps, then switch back to ordinary literal execution.

## Good candidates for durable memory

Promote information like this:
- stable activation boundaries,
- stable non-activation boundaries,
- user-endorsed sensory mappings,
- stable output-format preferences,
- repo-specific metaphor vocabularies that recur,
- reusable diagnostic cues,
- failure shields that prevent drift into vague or decorative metaphor,
- routing cues that say when to use the `synesthesia` skill.

Examples of durable memories:
- use synesthetic reasoning for architecture review, weird bugs, cohesion/readability critique, performance “feel,” or compare-by-feel analysis,
- avoid it for exact syntax questions, narrow command execution, security sign-off, legal/compliance interpretation, or literal-only requests,
- the user prefers stable mappings over novelty,
- the user wants sensory language tied to evidence,
- the user wants direct engineering translation every time the sensory layer is used.

## Promotion rules

Promote a candidate into `memory_summary.md` or `MEMORY.md` only when at least one is true:
- the user explicitly marks it as durable, such as “remember this,” “from now on,” “always do this,” or “this is my preference,”
- the same mapping, boundary, or workflow recurs across multiple sessions or repos,
- the user corrects the mapping and the correction is clearly intended to persist,
- the pattern reliably saves prompting, correction, retries, or explanation time,
- it prevents a recurring failure mode,
- it materially improves skill routing.

Do **not** promote a metaphor just because it sounded good once.
Promote only user-endorsed, repeated, or operationally useful mappings.

## Conflict and precedence rules

When candidates conflict, prefer:
1. the latest explicit user instruction,
2. repo-scoped guidance over global guidance for that repo,
3. repeated evidence over single-session impressions,
4. concrete engineering utility over aesthetic vividness.

If a mapping is repo-specific, keep it repo-specific.
Do not globalize local vocabulary unless it clearly becomes a cross-repo default.

If a new rule supersedes an old one, preserve only the current rule unless the older one is still needed as a scoped exception.

## Stable mappings worth preserving when reinforced

These are good durable defaults when the user repeatedly accepts them:
- **hot / red / bright** -> churn, contention, overloaded responsibilities, hot paths, concentrated risk
- **cold / blue / quiet** -> waiting, latency, passive complexity, distant dependencies, hidden lag
- **flicker / stutter / static** -> race conditions, flakiness, timing sensitivity, intermittent corruption
- **muddy / bleeding colors** -> mixed concerns, boundary leakage, coupled abstractions
- **sharp / glassy / brittle** -> unforgiving APIs, edge-case fragility, low error tolerance
- **heavy / dense / gravitational** -> dependency weight, slow builds, cognitive load, over-abstraction
- **hollow / echoing** -> indirection without value, ceremony without payoff
- **smooth / clean geometry** -> coherent interfaces, predictable data flow, stable testability
- **noise / clash / dissonance** -> naming inconsistency, branching sprawl, duplicated logic, conflicting invariants
- **long corridor / drag / distance** -> serialized waits, chatty calls, amplified latency
- **sticky / viscous** -> stateful coupling, hidden caches, mutation-heavy logic, hard rollback

Do not store these as immutable doctrine.
Store them as defaults that the user can refine, replace, or scope.

## What not to preserve

Do not preserve:
- one-off poetic phrases,
- vivid but non-reusable metaphors,
- transient bugs or current incident details,
- branch names, issue IDs, temporary task state, or sprint context,
- raw chat chronology,
- speculative assumptions about the user's taste,
- security-sensitive material,
- secrets, credentials, tokens, or private keys,
- repo-local metaphors that have not yet proven durable.

A sentence like “this payment service felt like wet cardboard today” is **not** durable memory.
A rule like “for payment-service latency chains in this repo, the user likes ‘long corridor’ to mean serialized waits” **can** be durable memory if repeated or explicitly endorsed.

## Compression rules

Summarize aggressively.
Do not copy raw session notes, long examples, or generated prose into Codex memory.

Prefer compact rules of the form:
- `When X, prefer Y because Z.`
- `In repo R, metaphor M means technical pattern T.`
- `Use skill S for trigger family K.`

Preserve only the minimum anchors needed for retrieval, such as:
- repo name,
- service or path family,
- stable mapping tag,
- failure pattern,
- routing cue.

Keep detailed examples and history in the underlying evidence artifacts, not in Codex memory.

## Artifact targeting

Use the memory artifacts like this:

### `memory_summary.md`
Put compact, always-useful defaults here:
- activation boundaries,
- non-activation boundaries,
- the “metaphor is never evidence” rule,
- the requirement to translate back into engineering language,
- the default routing rule toward the `synesthesia` skill.

### `MEMORY.md`
Put richer operational guidance here:
- mapping tables that have become stable,
- repo-specific vocabularies,
- reusable diagnostic cues,
- failure shields,
- nuanced routing notes,
- scoped exceptions.

### `skills/*`
Do **not** recreate the existing `synesthesia` skill in memory.
Create or update a skill only if repeated evidence shows a **new** reusable sub-workflow beyond the current skill, for example:
- a repeatable log-to-rhythm triage workflow,
- a repo-specific architecture color-mapping workflow,
- a stable “compare-by-feel” review procedure with a proven verification checklist.

If the pattern is useful but not yet strong enough for a skill, keep it as a concise `MEMORY.md` note.

## Routing guidance

Codex memory should help answer:
- does this task benefit from the synesthetic lens,
- what default boundaries apply,
- which stable mappings should be reused,
- what failure mode should be avoided,
- which repo-local vocabulary is relevant,
- when should the `synesthesia` skill be preferred.

Use durable memory to route **into** the skill.
Do not duplicate the skill’s full working instructions here.

## Failure modes to guard against

Promote concise shields against these recurring mistakes:
- using sensory language without concrete technical translation,
- overusing metaphor on literal tasks,
- switching mappings too often,
- sounding artistic instead of diagnostic,
- globalizing a repo-local metaphor,
- storing one-off clever phrases as if they were durable preferences,
- letting the sensory layer replace testing, debugging, or verification.

## Output preference for consolidation

When consolidating, prefer plain, operational language.
Do not write the memory itself in lush metaphor.
The consolidator should sound like a disciplined editor, not a poet.

Good durable memory is:
- compact,
- scoped,
- reusable,
- evidence-aware,
- easy for future Codex sessions to apply.

If a candidate memory does not clearly improve future behavior, skip it.
