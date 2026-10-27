# Skill authoring

## Progressive disclosure

The package must place knowledge at the cheapest sufficient layer:

```text
frontmatter description  activation cues
SKILL.md                  always-required authority, routing, safety, and stops
workflow guides/references  conditional knowledge loaded at a named decision
scripts/                  substantive deterministic operations
assets/                   output resources, not hidden policy
```

Before completion, prove:

- metadata carries every activation cue without claiming neighboring skills;
- `SKILL.md` contains every always-required rule;
- each deeper resource is linked beside the condition that requires it;
- a common-path probe reaches its outcome with the kernel and common resources,
  without requiring the consumer to reconstruct internal routing or choreography;
- a conditional-path probe loads only resources whose condition holds, without
  hiding an always-required obligation in an optional reference;
- a near-miss prompt does not activate.

Treat the 500-line body and 1024-character description limits as ceilings, not
quality targets. Front-load the task that distinguishes the skill from its
nearest neighbors. Descriptions are routing metadata, not miniature workflows:
keep necessary activation and near-miss cues there; put authority inventories,
procedures, internal modes, and output details in the selected body.

For multiple workflows, select the route before reading its procedures. Keep
shared obligations in the entry and link each required module at the decision
or effect it governs. Moving the whole manual behind an unconditional link is
not progressive disclosure; nor is hiding a mandatory rule in an optional read.
A common route must finish without reading unselected workflows.

During an authorized catalog-level change, inspect the actual rendered catalog,
including installed/system skills when accessible. Test neighboring descriptions
together for collisions and missed activation; do not infer truncation from
this repository alone. Record unavailable runtime/catalog evidence as a limit,
not a fabricated pass. This is change validation, not a new startup ritual.

Move detail only when doing so improves
progressive disclosure rather than hiding governing policy. In those same probes,
name what the consumer can stop knowing or coordinating and test a relevant change
for locality. Merely moving text to references or exposing it through configuration
does not deepen the skill. Retain specialized vocabulary only when it compresses a
stable distinction the consumer can recover; private terminology is not capability.

Separate content-preserving relocation from behavioral ablation. Preserve
required reviews, authority, stopping rules, canonical writers, and claim strength
unless their change is itself authorized and evidence-backed. Check positive,
near-miss, and shadow-failure cases on the selected read path. Distinguish static
reachability and byte preservation from observed model behavior; fewer loaded
bytes or a passing structural check alone does not prove efficacy.

## Cognitive compilation

When creating or changing how a target agent frames, searches, explains,
constructs, selects, reduces, or turns a selected route into action, read
[cognitive-compilation.md](references/cognitive-compilation.md) before selecting
the intervention. Skip this reference for mechanical routing, authority,
tooling, transport, or formatting edits that do not change cognition.

Translate the requested or evidenced weakness into the target's native trigger,
operation, shadow-risk guard, stopping condition, observable route delta, and
positive, near-miss, and shadow-failure probes. Reuse an equivalent native rule;
prefer `no-change` when no material delta is justified.

This is conditional authoring knowledge, not another public mode, runtime
dispatcher, handoff, or receipt. Tune's selection and authority gates still
govern. Do not redefine canonical verbatim skills or gate their independent
entry points through the operator taxonomy.

## Intervention selection

Select by semantic weakness, then realize by physical minimality.

Read [weakness-selection.md](references/weakness-selection.md) when candidates
differ in semantic scope, a short edit would introduce a broad rule, or a
regression guard risks overfitting.

A candidate is valid only when it:

- produces the expected delta;
- preserves protected contracts and valid near misses;
- stays inside the authorized package surface;
- introduces no contradiction, prohibited route, or unowned authority;
- leaves its claimed effect observable.

Among valid candidates, reject a semantically stronger candidate when a provably
weaker valid candidate permits every behavior the stronger candidate permits
while avoiding at least one unnecessary restriction. Preserve genuine
incomparability; never invent a numeric weakness score.

Select one dominant intervention route:

```text
no-change
trigger-or-boundary
decision-or-routing
workflow-or-tooling
artifact-or-resource
metadata-or-observability
consolidate-or-delete
blocked
```

One intervention may touch several files when they jointly realize one rule,
such as `SKILL.md` plus the matching decision-contract clause and agent prompt.

After semantic selection, minimize physical realization:

```text
1. no edit
2. delete or consolidate
3. clarify an existing trigger, rule, route, or stop
4. repair an existing artifact or operation
5. add one conditional reference
6. add a substantive operation
7. add a consequential contract clause or receipt
```

## Decision instrumentation

Read
[decision-instrumentation.md](references/decision-instrumentation.md)
before adding or materially changing a decision contract or receipt.

Create `references/decision-contract.json` only when stable consequential
decision rules need future clause-level evidence. Add an SDR-v1 receipt only when
the decision cannot otherwise be recovered proportionately.

When a contract exists:

- preserve stable trigger, route, and clause IDs;
- never renumber for formatting;
- synchronize changed routes with `SKILL.md`;
- preserve superseded IDs when historical evidence depends on them;
- update the source fingerprint after the final package state is known.

Structural validation proves shape, not correctness, usefulness, or authority.

## Package rules

- Make the smallest sufficient package, not merely the fewest changed lines.
- Default frontmatter to `name` and `description`.
- Use a hyphen-case name of at most 64 characters matching the folder.
- Keep the description under 1024 characters.
- Do not add README, INSTALL, or CHANGELOG files inside a skill package.
- Do not add scripts that merely grade prose.
- Do not add network dependencies, secrets, hidden global state, or
  nondeterminism.
- Preserve concurrent and unrelated work.
- Do not delegate edits to a system-managed optimizer.
- Root owns all skill-package mutation.

## Fresh-eyes pass

Before completing a non-trivial creation or edit, reread the result as both user
and router:

- Did the description become too broad, narrow, or duplicative?
- Does body workflow conflict with frontmatter or another skill's ownership?
- Did evidence, authority, privacy, publication, or stopping rules weaken?
- Did paths, names, links, contract IDs, or `agents/openai.yaml` drift?
- Would the result cause false, missed, ceremonial, or partial activation?
- Did the change add protocol where direct capability would suffice?
- For cognitive edits, did the native decision procedure change rather than just
  its register, without duplicating a handler or widening authority?

Fix a material finding before completion. Otherwise retain
`fresh_eyes_delta: none` internally.
