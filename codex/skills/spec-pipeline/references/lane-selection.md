# Lane Selection

`$spec-pipeline` must not treat an explicit `$spec-pipeline` invocation as a request for `spec_only`.

## Governing rule

For `full` mode, the default lane is:

```text
spec_to_plan
```

unless the user explicitly requests spec-only output or a material gate blocks downstream planning.

A user saying `$spec-pipeline`, `make a spec`, `write the spec`, `produce the governed spec`, or equivalent is not, by itself, a spec-only instruction. It asks the spec workflow to run. If the workflow finishes complete and plan-ready, planning authority transfers to `$plan` through the SGR-v2 and Execution Handoff.

## Legal `spec_only` reasons

Use `spec_only` only when at least one is true:

```text
user explicitly requested spec-only/no-plan/no-handoff output
mode is gate-only/challenge-only/lint-only
status is blocked, drift, audit-only, or partial
material user judgment remains unresolved
Gate Result has plan_allowed=no
lint failed, was skipped when required, or blocked handoff
fresh-eyes returned to grill or detected drift
execution_handoff.ready_for_plan=no
execution_handoff.next_owner is not $plan
do_not_execute_before is non-empty
runtime cannot load or invoke $plan, in which case emit AUTO_PLAN_HANDOFF_REQUIRED rather than silently converting to spec_only
```

## Illegal `spec_only` reasons

Do not select `spec_only` because:

```text
the user invoked `$spec-pipeline` rather than `$plan`
the user did not separately say "run `$plan`"
the assistant wants to be conservative after the spec succeeds
the final implementation should be done later by another turn
the handoff would require a same-turn tail-call
```

Those are not semantic blockers. They are routing assumptions. If the final SGR-v2 says the spec is complete and plan-ready, the correct lane is `spec_to_plan`.

## Receipt requirements

When choosing `spec_only`, record the concrete blocker in both places:

```yaml
spec_governance_receipt:
  lane: spec_only
  gate:
    reason: "..."
  execution_handoff:
    ready_for_plan: no
    next_owner: spec-pipeline | grill-me | spec-retro | none
  auto_plan_handoff:
    eligible: no
    reason: "specific blocker, not merely explicit spec-pipeline invocation"
```

When the only reason would be "the user did not ask for `$plan` separately," set:

```yaml
lane: spec_to_plan
auto_plan_handoff:
  eligible: yes
  invocation: same_turn_tail_call
```

or, if the runtime cannot load `$plan`:

```text
AUTO_PLAN_HANDOFF_REQUIRED
reason: same-turn tail-call unavailable in this runtime
next_owner: $plan
```

## Regression witness

The failure this prevents is:

```text
explicit `$spec-pipeline` invocation
-> assistant selects spec_only before final receipt
-> final receipt says auto_plan_handoff.eligible=no because user did not request same-turn planning
-> no `$plan` execution even though no spec/governance blocker existed
```

That is a routing error. Explicit `$spec-pipeline` is not an opt-out from `$plan` when the final governed spec is plan-ready.
