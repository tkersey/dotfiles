---
name: actuating
description: >-
  Plan-to-PR execution workflow. Turn a material plan/spec/proposal into durable
  `$st` tasks, execute every task through `$fixed-point-driver` and the repo's
  language-specific skills, keep proof-carrying completion in `$st`, run full
  build/lint/test validation, then `$ship` the branch into a PR. Trigger for
  `$actuating`, plan-to-PR, implement this plan and open a PR, turn this plan
  into tasks and ship it, use `$st` then `$fixed-point-driver` then `$ship`, or
  end-to-end plan execution. Do not use for one-off bug fixes, pure planning,
  current-branch review resolution, merge/land, or PR creation without
  implementation.
---

# Actuating

## Purpose

Drive a material plan from **plan text** to **proof-backed PR**.

This skill replaces the repeated manual prompt:

```text
Use $st to turn this plan into steps/tasks.
Use $fixed-point-driver to implement them.
Do not stop until all steps are complete.
Use $ship once all builds, lints, and tests pass.
Use language-specific skills when the repo calls for them, such as $zig.
```

## Doctrine

Operate in **ACTUATING**, **PLAN-GRAPHED**, **FIXED-POINTED**, **LANGUAGE-AWARE**, **PROOF-GATED**, **SURFACE-TAXED**, **SHIP-READY**, and **TAIL-PROOF** mode.

- **ACTUATING**: identify the lever that moves the system from plan to shipped PR, then pull it with proof.
- **PLAN-GRAPHED**: a material plan becomes durable `$st` task graph state, not transient prose or a fragile chat checklist.
- **FIXED-POINTED**: implementation work is driven through `$fixed-point-driver` until each task is complete, blocked, or explicitly removed from scope.
- **LANGUAGE-AWARE**: use repo/language skills such as `$zig`, `$lean`, or other visible language rails when files, toolchains, errors, or project conventions call for them.
- **PROOF-GATED**: each completed task needs evidence; final shipping needs current build/lint/test proof.
- **SURFACE-TAXED**: mutation-capable work must respect ablation, isomorphism, soundness, and surface-budget gates supplied by the called skills.
- **SHIP-READY**: `$ship` is allowed only after all in-scope tasks are complete or explicitly blocked/deferred and the current head has passing proof.
- **TAIL-PROOF**: the final output must end with the state, proof, PR status, and next bottleneck.

## Contract

This skill is a workflow driver. It does not replace `$st`, `$fixed-point-driver`, language skills, `verification-closure`, or `$ship`; it composes them.

Required outcomes:

1. The plan is converted into a durable `$st` graph or a clearly named fallback graph artifact.
2. Every in-scope task is implemented, validated, or explicitly blocked/deferred with reason and proof state.
3. `$fixed-point-driver` owns non-trivial implementation loops.
4. Language-specific skills own language-specific proof lanes when applicable.
5. `$ship` runs only after builds, lints, and tests pass, or after the repo proves no such command exists and the user explicitly accepts the limitation.
6. The final response ends with an **Actuation Bottom Line**.

## When to use

Use this skill when the user asks to take a plan/spec/proposal through implementation and PR publication, especially with phrases like:

- `$actuating`
- `plan to PR`
- `turn this plan into tasks and ship it`
- `use $st to turn this plan into steps/tasks`
- `use $fixed-point-driver to implement them`
- `don't stop until all steps are complete`
- `ship once builds, lints, and tests pass`
- `implement this plan and open a PR`

Do not use this skill for:

- one-shot implementation with no material plan graph;
- pure planning with no implementation intent;
- current-branch review/fix/PR-sweep loops; use `$resolve`;
- final readiness only; use `$verification-closure`;
- PR creation only after work is already complete; use `$ship`;
- merge/land; use `$land`.

## Lifecycle

```text
plan intake -> $st graph -> aperture -> fixed-point implementation -> task proof -> graph completion -> full validation -> $ship -> PR proof
```

## Workflow

### 1. Plan intake

Bind the work to a concrete plan source:

- pasted plan;
- markdown/spec/proposal file;
- issue/PR description;
- existing `.step/st-plan.jsonl`;
- active proposed plan.

Before task creation, identify:

- target outcome;
- non-goals;
- acceptance checks;
- language/toolchain clues;
- expected PR scope;
- public side effects expected by the user.

If the user has not clearly asked for PR creation/publication, stop before `$ship` and ask only if that is the real blocker. If the prompt clearly says plan-to-PR or ship once validated, PR creation is in scope.

### 2. `$st` graph creation

Use `$st` as the durable source of truth.

Preferred path for material plans:

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
st compile aperture --file .step/st-plan.jsonl --limit 7
```

If `st intake` / `st graph` / `st compile` are unavailable, use the fallback described by `$st`, and record graph debt explicitly. Do not pretend a durable graph exists when it does not.

Rules:

- `.step/st-plan.jsonl` is durable truth.
- Native plan tools are only the visible aperture.
- Preserve `[st-id]` prefixes in user-visible plan rows.
- Do not mark a task complete without proof.
- Do not let chat prose become the source of task state.

### 3. Aperture selection

Select the next executable aperture from `$st`.

A good aperture has:

- dependency-ready tasks;
- small enough scope for reviewable implementation;
- explicit proof signals;
- no hidden public side effects;
- no ambiguous ownership boundary.

If tasks are independent and read-heavy, use subagents or language-specific rails for evidence. Keep mutation single-rooted unless the repo's orchestration policy explicitly allows disjoint writes.

### 4. Language-skill detection

Before implementation, inspect repo signals and activate the right language rails:

- Zig: `.zig`, `build.zig`, `zig build`, `zig test`, `zig fmt`, `zls`, Zig migration/safety/performance cues -> `$zig`.
- Lean: `.lean`, `lake`, proof repair, theorem/proof/termination/mathlib cues -> `$lean`.
- Python: `pyproject.toml`, `uv`, `pytest`, `mypy`, ruff/format/test cues -> use repo Python tooling standards.
- Other language rails: use any visible repo skill whose trigger clearly owns the files/toolchain/proof lane.

Language skills should supply language-specific commands and hazards. They do not replace the plan graph, fixed-point loop, or final ship gate.

### 5. Implementation loop

For each executable `$st` item or aperture:

1. Route non-trivial code changes to `$fixed-point-driver`.
2. Let `$fixed-point-driver` select implementation, ablation, adversarial review, validation, and closure subpasses.
3. Use `$accretive-implementer` only when `$fixed-point-driver` hands off a narrow owned implementation task or when a task is small enough to avoid full fixed-point orchestration.
4. Use language-specific skills inside the loop when proof or safety is language-shaped.
5. When a task is done, complete it in `$st` with the command/check/evidence that proves it.
6. Compile the next aperture and continue.

Do not stop after the first green patch. Continue until every in-scope task is:

- `complete` with proof;
- `blocked` with a concrete blocker;
- `deferred` only when the plan or user scope explicitly permits deferral;
- removed from scope by an evidence-backed graph/update decision.

### 6. Validation gate

Before shipping, run the full repo-appropriate proof suite.

At minimum, attempt to identify and run:

- build;
- lint/static checks;
- tests;
- typecheck/proof checks;
- language-specific validation;
- any plan-specific acceptance checks;
- any PR-specific proof that `$ship` should include.

If the repo lacks a build, lint, or test command, record the search evidence and the substitute proof. Do not claim “all checks pass” when a category was not found or not run.

### 7. Ship gate

Invoke `$ship` only when all are true:

- `$st` graph has no unhandled in-scope tasks;
- current head includes the intended work;
- build/lint/test/proof gates pass or missing gates are explicitly accounted for;
- no unresolved material fixed-point, ablation, soundness, or verification gate remains;
- PR side effect is in scope;
- proof summary is ready for the PR body.

`$ship` opens or updates a PR. It does not merge. Use `$land` only for explicit merge/land intent.

## Actuation State Record

For material runs, maintain a compact state record:

```yaml
actuation_state:
  run_id: "..."
  plan_source: "..."
  target_pr_state: opened | updated | not-yet | blocked
  artifact_state:
    branch: "..."
    base: "..."
    head: "..."
  st_graph:
    file: ".step/st-plan.jsonl"
    intake_status: complete | fallback | blocked
    audit_status: pass | fail | not-run
    total_tasks: 0
    complete: 0
    blocked: 0
    deferred: 0
    open: 0
  execution:
    fixed_point_driver_used: yes | no
    language_skills_used: []
    ablation_activation: required | not-required | blocked | not-applicable
    verification_closure_used: yes | no
  validation:
    build: pass | fail | missing | not-run
    lint: pass | fail | missing | not-run
    tests: pass | fail | missing | not-run
    language_specific: pass | fail | missing | not-run
  ship:
    ship_allowed: yes | no
    pr_url: "..."
    blocker: "..."
```

## Output contract

Use tail-weighted sections:

1. Plan Source / Goal
2. `$st` Graph State
3. Execution Aperture
4. Work Completed
5. Validation
6. Ship Status
7. Actuation Bottom Line

`Actuation Bottom Line` must be the final section.

### Actuation Bottom Line

End with:

```text
Actuation Bottom Line:
- target state:
- graph state:
- tasks complete:
- validation:
- PR:
- proof:
- blocker / next bottleneck:
```

## Hard rules

- Do not bypass `$st` for material plans.
- Do not treat `update_plan` as durable state.
- Do not implement beyond the plan without updating scope or graph state.
- Do not keep going silently when the correct next step requires credentials, destructive approval, or public side-effect confirmation not already granted.
- Do not run `$ship` with failing build/lint/test gates.
- Do not call missing validation “passed.”
- Do not merge or land.
- Do not bury the final graph state or PR status above the fold.

## Resources

- [plan-to-pr-lifecycle.md](references/plan-to-pr-lifecycle.md)
- [st-handoff.md](references/st-handoff.md)
- [fixed-point-execution-loop.md](references/fixed-point-execution-loop.md)
- [language-skill-detection.md](references/language-skill-detection.md)
- [shipping-gate.md](references/shipping-gate.md)
- [example-invocations.md](references/example-invocations.md)
