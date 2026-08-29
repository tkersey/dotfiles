---
name: tune
description: "Create, directly edit, or evidence-tune Codex skill packages. Use for new skills, explicit skill surgery, regressions, or intended-vs-observed skill behavior. Infer create, edit, or tune mode; preserve progressive disclosure and stable contracts; select the semantically weakest valid intervention before minimizing the diff; and mutate or publish only with corresponding authority."
---

# Tune

## Mission

Own the complete lifecycle of a Codex skill package:

```text
create a skill
edit a known skill surface
tune behavior from evidence
```

One skill owns diagnosis, selection, and authorized mutation. Keep those phases
distinct, but do not hand the package to another skill merely to continue the
same change.

## Public modes

Choose exactly one intent mode:

```text
create
edit
tune
```

Infer the mode unless the user names one explicitly:

```text
no suitable target skill exists
  -> create

existing target + requested change or known defect
  -> edit

existing target + question about use, behavior, effectiveness, or regression
  -> tune
```

An explicit `$tune create`, `$tune edit`, or `$tune tune` overrides inference.

`inspect`, `apply`, `regression`, evidence source, publication state, and terminal
result are not modes.

## Authority gates

### Mutation

Classify mutation authority separately:

```text
inspect
apply
```

`inspect` forbids file changes. Select it for analyze, audit, review, inspect,
"what should change?", proposal-only, or an explicit no-edit request.

`apply` authorizes local skill-package mutation. Select it for create, edit, fix,
update, apply, patch, or improve when the requested target and delta are clear.
An explicit prohibition on edits always wins.

In tune mode, diagnose and freeze the expected delta before mutation. Direct edit
mode does not require a historical tuning dossier when the requested delta is
already known.

### Publication

Local mutation does not authorize Git effects.

```text
commit  -> explicit commit, save-to-git, publish, ship, or PR intent
push    -> explicit remote publication intent
PR      -> explicit PR intent
```

Report a concrete blocker when requested publication cannot complete.

## Common kernel

1. Resolve the skill root, target, and mode.
2. Search for an existing skill before creating another one.
3. Read the relevant package:
   ```text
   SKILL.md
   agents/openai.yaml
   references/decision-contract.json
   linked references/
   linked scripts/
   linked assets/
   definitions/
   ```
4. Reconstruct only the operative contract:
   ```text
   trigger and non-trigger boundary
   consequential decisions and routes
   required authority and stopping conditions
   protected behavior
   observable success and failure
   ```
5. Acquire only the evidence the selected mode needs.
6. Before mutation, freeze:
   ```text
   expected delta: from -> to
   protected behavior
   evidence and its limits
   selected intervention
   mutation authority
   ```
7. Select one dominant valid intervention, or no change.
8. Apply only when authorized; root owns every package edit.
9. Validate package integrity and the strongest currently observable behavioral
   claim.
10. Run the fresh-eyes pass, then publish only when separately authorized.

If materially new evidence invalidates the frozen delta or selected intervention,
return to step 4. Do not silently broaden the diagnosis during editing.

## Progressive disclosure

The package must place knowledge at the cheapest sufficient layer:

```text
frontmatter description  activation cues
SKILL.md                  always-required authority, routing, safety, and stops
references/               conditional knowledge loaded at a named decision
scripts/                  substantive deterministic operations
assets/                   output resources, not hidden policy
```

Before completion, prove:

- metadata carries every activation cue without claiming neighboring skills;
- `SKILL.md` contains every always-required rule;
- each deeper resource is linked beside the condition that requires it;
- a common-path probe needs only the kernel and common resources;
- a conditional-path probe loads only resources whose condition holds;
- a near-miss prompt does not activate.

Keep `SKILL.md` under 500 lines. Move detail only when doing so improves
progressive disclosure rather than hiding governing policy.

## Create mode

1. Search for a skill already covering the intent.
2. Collect two or three realistic trigger prompts and at least one near miss.
3. State the problem, success criterion, and non-trigger boundary.
4. Classify the skill as `decision`, `execution`, `evidence`, `orchestration`, or
   `mixed` only when the classification affects design or observability.
5. Map activation metadata, the always-required kernel, common resources, and
   each conditional resource.
6. Scaffold when useful:
   ```bash
   uv run --with pyyaml -- python3 \
     codex/skills/.system/skill-creator/scripts/init_skill.py \
     <skill-name> --path codex/skills
   ```
7. Author the smallest operative package.
8. Evaluate decision instrumentation; do not add it by default.
9. Align `agents/openai.yaml`.
10. Remove redundant doctrine, examples, and generated ceremony.

If an existing skill already owns the intent, prefer extending it or report
`no-change`; do not create a synonym package.

## Edit mode

Use for direct user-authorized surgery when the desired change is already known.

- Preserve unrelated behavior and files.
- Preserve stable decision-contract IDs.
- Update only affected clauses and linked surfaces.
- Keep frontmatter, package paths, links, and `agents/openai.yaml` aligned.
- Do not manufacture historical evidence, tuning packets, or receipts.
- Escalate to tune mode only when deciding *whether* or *how* the skill should
  change requires behavioral evidence.

## Tune mode

Tune compares intended behavior with observed decision episodes and outcomes.

```text
activation evidence asks: was the skill present?
decision evidence asks: what changed because of it?
outcome evidence asks: was that change useful?
```

These implications are invalid:

```text
mention -> activation
activation -> decision influence
decision influence -> outcome causality
successful outcome -> skill effectiveness
```

Read [tuning-evidence.md](references/tuning-evidence.md) when historical,
provided, mixed, or attribution-sensitive evidence is needed. Use the passive Seq
definition there for bounded historical reconstruction.

For every material episode preserve the trigger, activation evidence, decision
question, selected route, rejected routes actually observed, exercised clauses,
decision effect, evidence strength, downstream signal, and counterevidence.
Do not invent unobserved alternatives.

Classify the smallest useful gap:

```text
activation | interpretation | workflow | tooling | resource
metadata | boundary | source-scope | decision-contract | observability
outcome | ceremony | overconstraint
```

Produce at most one dominant expected delta per cycle. Preserve denominators,
counterevidence, scope, and limitations. If no consequential decision,
execution, proof, lifecycle, or outcome relation should change, stop with
`no-change`.

Regression is an evidence shape, not a mode. Bind the prior failure, involved
trigger/clause/route, expected future behavior, and a reproduction query. Repair
the witnessed failure class without installing an unsupported global ban.

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

## Outcome observation

Run a current behavioral observation when the evidence can exist now. Otherwise
retain the exact future query and state what remains unproved.

A text edit proves only that the package changed. It does not prove improved
activation, decision quality, execution fidelity, or outcomes.

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

Fix a material finding before completion. Otherwise retain
`fresh_eyes_delta: none` internally.

## Report

```text
Tuned:
- Target:
- Mode: create | edit | tune
- Mutation: inspect | apply
- Expected delta:
- Evidence and limits:
- Selected intervention:
- Files changed:
- Validation:
- Outcome observation:
- Publication:
- Remaining uncertainty:
```

Omit empty or inapplicable fields.

## Hard rules

- `$tune` is the sole owner of skill creation, direct editing, and
  evidence-backed tuning.
- Mode expresses intent; authority, evidence shape, rigor, and result do not.
- Diagnosis precedes mutation in tune mode.
- Direct edit does not require ceremonial diagnosis.
- No expected delta, no tune-mode mutation.
- One dominant intervention per cycle.
- Semantic weakness precedes physical minimality.
- Behavioral claims require behavioral evidence.
- Preserve stable contract IDs and unrelated work.
- No package creation before checking for an existing owner.
- No commit, push, or PR without explicit publication intent.
