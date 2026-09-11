---
name: tune
description: "Create, edit, or diagnose Codex skill packages, including activation failures, regressions, and intended-versus-observed behavior. Use for skill-package work, not ordinary application code changes."
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
push    -> explicit remote publication intent after the intended commit succeeds
PR      -> explicit PR intent
```

Report a concrete blocker when requested publication cannot complete.

## Selected guidance

After selecting intent and authority, read only [create.md](create.md),
[edit.md](edit.md), or [tuning.md](tuning.md) for that mode. Read
[authoring.md](authoring.md) before selecting or realizing a package intervention,
including proposal-only surgery; it owns disclosure, intervention selection,
package integrity, and the fresh-eyes pass. A tune diagnosis ending in `no-change`
need not load authoring procedure merely to report that result.

Follow the selected guide through its authorized validation and publication.
An available implementation or another skill is not a reason to stop short of
the requested package change. Continue independent authorized work when one
claim or effect is blocked.

<a id="progressive-disclosure"></a>
Progressive disclosure: [authoring.md](authoring.md#progressive-disclosure).
<a id="cognitive-compilation"></a>
Cognitive compilation: [authoring.md](authoring.md#cognitive-compilation).
<a id="intervention-selection"></a>
Intervention selection: [authoring.md](authoring.md#intervention-selection).
<a id="decision-instrumentation"></a>
Decision instrumentation: [authoring.md](authoring.md#decision-instrumentation).
<a id="package-rules"></a>
Package rules: [authoring.md](authoring.md#package-rules).
<a id="fresh-eyes-pass"></a>
Fresh-eyes pass: [authoring.md](authoring.md#fresh-eyes-pass).
<a id="create-mode"></a>
Create mode: [create.md](create.md#create-mode).
<a id="edit-mode"></a>
Edit mode: [edit.md](edit.md#edit-mode).
<a id="tune-mode"></a>
Tune mode: [tuning.md](tuning.md#tune-mode).

## Common kernel

1. Resolve the skill root, target, and mode.
2. Search for an existing skill before creating another one.
3. Read `SKILL.md`, `agents/openai.yaml`, and an existing decision contract first.
   Load linked references, scripts, assets, and definitions only when the selected
   mode or proposed change depends on them; inspect affected integrations before
   editing.
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

For an explicitly requested portfolio pass, apply selection independently to each
target and finish the authorized set. A supported defect in current package text
can justify a direct edit; historical reconstruction is needed for claims about
observed activation, recurrence, influence, or outcomes.

If materially new evidence invalidates the frozen delta or selected intervention,
return to step 4. Do not silently broaden the diagnosis during editing.

## Outcome observation

Run a current behavioral observation when the evidence can exist now. Otherwise
retain the exact future query and state what remains unproved.

A text edit proves only that the package changed. It does not prove improved
activation, decision quality, execution fidelity, or outcomes.

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
- Doctrine vocabulary without an observable behavioral delta does not justify an
  edit.
- Preserve stable contract IDs and unrelated work.
- No package creation before checking for an existing owner.
- No commit, push, or PR without explicit publication intent.
