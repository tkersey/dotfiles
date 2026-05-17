# Synesthesia memory extension

Use this extension only during Codex memory consolidation. It interprets evidence about the user's synesthetic software-reasoning preferences and related diagnostic workflows.

It is not a runtime prompt, not a replacement for `AGENTS.md`, not a replacement for the existing source `synesthesia` skill, and not authority to turn aesthetic language into evidence.

## Source contract

This extension represents durable preferences, stable mappings, reusable heuristics, failure shields, and repo-scoped vocabulary for synesthetic software reasoning.

Its job is to help Codex remember:

- when the synesthetic lens is useful;
- when it should stay dormant;
- which sensory mappings are user-endorsed and stable;
- how sensory language must translate back into engineering language;
- which repo-specific metaphors or vocabularies should remain local;
- which failure modes to avoid when using this style;
- when to route into the source `synesthesia` skill;
- when repeated evidence justifies a memory-root synesthetic sub-skill.

`instructions.md` is classification guidance, not evidence. Do not promote a mapping merely because it appears in this file or in the source skill. Promote only from active consolidation evidence: user messages, corrections, repeated accepted outputs, learnings rows, rollout summaries, explicit resource digests, or other durable evidence.

If no durable signal is available, make no memory change.

## Optional local resource digests

If curated `resources/*.md` files are present, treat them as short-lived evidence packets, not canonical mapping tables or standing style instructions.

Prefer timestamped Markdown resource files whose names begin with `YYYY-MM-DDTHH-MM-SS`. A useful digest separates `Endorsed mappings`, `Activation boundaries`, `Rejected mappings`, `Failure shields`, and `Skill candidates`.

Each candidate should include compact fields when evidence supports them:

- `sensory_phrase`
- `engineering_translation`
- `activation_boundary`
- `non_activation_boundary`
- `scope`
- `evidence_source`
- `use_when`
- `do_not_use_when`
- `verification`
- `confidence`
- `memory_target`
- `memory_skill_candidate`
- `mcp_search_terms`

Do not promote a mapping from a template, ontology, assistant-generated phrase, visible `_templates/` directory, or example packet unless active consolidation evidence shows user endorsement, correction, repetition, or operational use.

## MCP-readability and search-shape requirements

Codex memories may be exposed through read-only memory tools that list, read, and search files under `~/.codex/memories`. Memory search is primarily exact substring/window matching, not semantic retrieval.

Shape synesthesia memories so future agents can find them without semantic guessing:

- use stable field labels such as `synesthesia_mapping`, `sensory_phrase`, `engineering_translation`, `activation_boundary`, `non_activation_boundary`, `failure_shield`, `scope`, `related_skill`, and `mcp_search_terms`;
- keep the sensory phrase and engineering translation close together, ideally within a small line window;
- preserve exact user-endorsed phrases, repo names, service/path families, task-family names, and skill names;
- include `mcp_search_terms` for high-value mappings or boundaries;
- avoid decorative headings that make the mapping hard to search.

Assume files under the memory root, including extension resources while they exist, may be discoverable by read-only memory tooling. Do not store secrets, credentials, sensitive local-only details, ambient UI colors, passive screen context, or raw chat chronology.

Resource files are short-lived consolidation inputs. Durable synesthetic knowledge must be promoted into `memory_summary.md`, `MEMORY.md`, or an appropriate memory-root `skills/*` file.

## Core contract to preserve when evidenced

These rules are load-bearing. Promote them when evidence shows the user wants them remembered; otherwise leave them in the source skill rather than duplicating them into memory.

- Synesthetic reasoning is an available diagnostic lens, not a mandatory output style.
- Metaphor is never evidence.
- Every useful metaphor must translate back into concrete engineering implications.
- Literal technical correctness outranks sensory style.
- Strong analysis pattern: literal read -> sensory render -> dissonances -> engineering translation -> recommended changes.
- For implementation work, use the lens briefly only if it improves decisions, then execute literally.
- The user prefers stable mappings over novelty when mappings are being reused.
- Synesthetic memory should be plain operational memory, not lush prose.

## Promotion gate

Promote a candidate only when all four checks pass:

1. `evidence`: the signal comes from user endorsement/correction, repeated use, a tagged learning, an explicit durable instruction, or clear acceptance in a task outcome.
2. `stability`: it is likely to apply beyond the single sentence/session where it appeared.
3. `utility`: it improves future routing, diagnosis, communication, or failure avoidance.
4. `reversibility`: the sensory phrase can be translated into a concrete technical pattern.

After the gate passes, promote when at least one is true:

- the user explicitly marks it as durable, such as `remember this`, `from now on`, `always do this`, or `this is my preference`;
- the same mapping, activation boundary, or workflow recurs across multiple sessions or repos;
- the user corrects a mapping and the correction is clearly intended to persist;
- the pattern saves prompting, correction, retries, explanation time, or skill-routing effort;
- it prevents a recurring failure mode;
- it materially improves when/how the source `synesthesia` skill should trigger;
- it proves a reusable sub-workflow that may justify a memory-root skill.

Do not promote a metaphor just because it sounded good once. Assistant-generated metaphors are not durable memory unless the user accepts, repeats, corrects, or operationalizes them.

## Good candidates for durable memory

Promote information like this:

- stable activation boundaries;
- stable non-activation boundaries;
- user-endorsed sensory mappings;
- stable output-format preferences;
- repo-specific metaphor vocabularies that recur;
- reusable diagnostic cues;
- failure shields that prevent decorative or vague metaphor;
- routing cues that say when to use the source `synesthesia` skill;
- repeated sub-workflows that go beyond the existing source skill.

Examples of durable memories:

- Use synesthetic reasoning for architecture review, weird bugs, cohesion/readability critique, performance feel, or compare-by-feel analysis.
- Avoid synesthetic framing for exact syntax questions, narrow command execution, security sign-off, legal/compliance interpretation, or literal-only requests.
- The user wants sensory language tied to evidence.
- The user wants direct engineering translation every time the sensory layer is used.

## Mapping confidence and scope

Store mappings with the narrowest correct scope:

- `global_default`: repeated or explicitly endorsed across contexts.
- `repo_scoped`: applies to one repo, service, path family, or domain vocabulary.
- `task_family_scoped`: applies to architecture review, debugging, performance triage, onboarding, comparison, etc.
- `tentative`: not enough for durable memory; normally skip unless the open question itself is useful as a route/stop rule.

If a mapping is repo-specific, keep it repo-specific. Do not globalize local vocabulary unless later evidence makes it a cross-repo default.

When candidates conflict, prefer:

1. the latest explicit user instruction;
2. repo-scoped guidance over global guidance for that repo;
3. repeated user-endorsed evidence over single-session impressions;
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

## Artifact targeting

Follow the base memory schema and update existing task groups when possible.

### `memory_summary.md`

Put only compact, always-useful defaults here:

- activation boundaries;
- non-activation boundaries;
- `metaphor is never evidence`, when evidenced as durable user preference;
- the requirement to translate sensory observations back into engineering language;
- the default routing rule toward the source `synesthesia` skill;
- a short pointer to any memory-root synesthetic sub-skill if one exists.

Recommended shape:

```text
- synesthesia_boundary: <when to use / not use>; engineering_translation_required: true; related_skill: synesthesia.
```

Do not paste the mapping ontology into `memory_summary.md`.

### `MEMORY.md`

Put richer operational guidance here:

- stable mapping tables that are evidence-backed;
- repo-specific vocabularies;
- reusable diagnostic cues;
- failure shields;
- nuanced routing notes;
- scoped exceptions;
- source skill or memory-root skill pointers.

Recommended line-window shape:

```text
synesthesia_mapping: <short title>
scope: <global_default|repo_scoped|task_family_scoped>; scope_anchor: <repo/path/task>
sensory_phrase: <phrase>
engineering_translation: <concrete technical pattern>
activation_boundary: <when to use>
non_activation_boundary: <when to avoid>
failure_shield: <mistake avoided>
related_skill: synesthesia
mcp_search_terms: synesthesia, <phrase>, <repo>, <task>, <technical pattern>
```

Use the required `# Task Group` structure from the base consolidation prompt. Keep mapping bullets compact and scoped.

### `skills/*`

Codex memory consolidation may create or update memory-root `skills/*`. Use this capability sparingly.

Do not recreate the existing source `synesthesia` skill in memory. The source skill owns the full runtime procedure.

Create or update a memory-root skill only if repeated evidence shows a new reusable sub-workflow beyond the current source skill, for example:

- a repeatable log-to-rhythm triage workflow;
- a repo-specific architecture color-mapping workflow;
- a stable compare-by-feel review procedure with a proven verification checklist;
- a performance-feel diagnostic preflight tied to concrete metrics/profiling;
- a memory/MCP search preflight for repo-specific synesthetic vocabulary.

Prefer specific names such as `skills/synesthesia-log-rhythm-triage/`, `skills/<repo>-architecture-color-map/`, or `skills/synesthesia-memory-preflight/` rather than colliding with the source `synesthesia` skill.

A memory-root synesthesia skill should be short and evidence-bound:

```text
# <skill name>
trigger: ...
use_when: ...
first_memory_searches: ...
procedure: literal read -> sensory render -> dissonances -> engineering translation -> recommended changes
translation_required: true
verification: ...
non_goals: ...
mcp_search_terms: ...
```

If the pattern is useful but not yet strong enough for a skill, keep it as a concise `MEMORY.md` note. If it is only a global activation boundary, keep it in `memory_summary.md`.

## Chronicle-derived context guard

Chronicle-derived sensory, visual, or interface context must not become a synesthetic preference unless the user explicitly endorsed the mapping, corrected it as durable, repeated it across contexts, or used it as a stable diagnostic aid.

Use Chronicle-derived context to recover task continuity or locate source material, not to infer taste. Reject passive screen context, incidental UI colors, one-off metaphors, generated descriptions, and ambient chronology unless they translate to a concrete engineering pattern and pass the normal promotion gate.

## Cross-extension handling

- If a `learnings` row reinforces a synesthetic preference or mapping, consolidate the durable signal here and avoid duplicating it in learnings memory.
- If a `learnings` row is a general workflow failure shield with no sensory preference, let `learnings` own it.
- If the signal is a general behavior guardrail about when to use or avoid metaphor, `synesthesia` owns the sensory boundary and `harness` may own the broader agent-behavior rule only if separate.
- If the signal is a failed-hypothesis route constraint, let `negative-ledger` own it; preserve only any endorsed sensory vocabulary here.
- If multiple extensions point to the same durable rule, keep one memory entry and include the most useful retrieval anchor.

## Failure modes to guard against

Promote concise shields against recurring mistakes:

- using sensory language without concrete technical translation;
- overusing metaphor on literal tasks;
- switching mappings too often;
- sounding artistic instead of diagnostic;
- globalizing a repo-local metaphor;
- storing one-off clever phrases as durable preferences;
- letting the sensory layer replace testing, debugging, profiling, or verification;
- treating assistant-generated metaphors as user preference without user evidence.

## What not to preserve

Do not preserve:

- one-off poetic phrases;
- vivid but non-reusable metaphors;
- transient bugs or current incident details;
- branch names, issue ids, temporary task state, or sprint context;
- raw chat chronology;
- speculative assumptions about the user's taste;
- security-sensitive material;
- secrets, credentials, tokens, or private keys;
- repo-local metaphors that have not proven durable;
- the full source `synesthesia` skill procedure.

A sentence like `this payment service felt like wet cardboard today` is not durable memory. A rule like `for payment-service latency chains in this repo, the user likes long corridor to mean serialized waits` can be durable memory if repeated or explicitly endorsed.

## Output preference for consolidation

When consolidating, write plain operational memory. Good durable synesthesia memory is compact, scoped, reusable, evidence-aware, searchable, and easy for future Codex sessions to apply.

If a candidate memory does not clearly improve future behavior, skip it.
