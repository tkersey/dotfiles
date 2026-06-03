# Adversarial Parallelism for Review Adjudication

Use adversarial parallelism to challenge every downstream action while preserving
time-to-action. The goal is not to make review adjudication slower; the goal is
to spend adversarial effort only where it can change route, scope, proof, owner,
or permission.

## Core principle

Every `Resolve Selection` row needs an adversarial response. The response must
attempt to defeat, downgrade, reroute, narrow, or block the selected action.

Adversarial responses are read-only. They may inspect current artifacts, proofs,
comments, rationale, ownership boundaries, or surface budgets. They must not edit
code, mutate fixtures, resolve threads, or draft final replies.

## Action-to-adversary map

| selected action | required adversarial challenge |
|---|---|
| `address` | Is no code change safer? Should validation happen first? Is the proposed fix wrong or overbroad? Does this violate scope/ownership? Does the surface budget permit the fix? Is fixed-point routing overkill? |
| `validate-only` | Is there enough current proof to mutate now? Is validation valuable, or is no action better? Is the probe likely to mutate production behavior accidentally? |
| `resolve-thread-only` | Is the comment still material on latest HEAD? Is proof strong enough to resolve without code? Is hidden implementation still needed? |
| `do-not-address` | Is the no-change case actually preserved? Is there review-closure value in a proof-only reply? Is this really out of scope or preference-only? |
| `blocked` | Can a narrower validation, proof-only reply, or user question safely unblock the claim? |

## Parallelism modes

Use one mode per row:

- `root-equivalent`: root performs the adversarial response inline. Use for narrow,
  obvious, proof-only, already-fixed, or no-change rows.
- `targeted-parallel`: one or two independent read-only lanes challenge distinct
  uncertainty classes.
- `full-fanout`: evidence, scope/ownership, criticality, no-change,
  validation-value, and fix-shape lanes run in parallel.
- `swarm`: five or more lanes for large, contentious, P2+, invariant-coupled, or
  likely-to-reopen sets.
- `not-required`: only for `blocked` rows where no safe downstream action exists;
  name the missing evidence.

## Calibration rule

Parallelize when it reduces elapsed time or prevents expensive wrong action.
Avoid parallelism when the row is narrow, local, already proof-bearing, or when
parallel lanes would all inspect the same small fact.

Escalate to `full-fanout` or `swarm` when any of these are true:

- a P2+ row may be selected as `address`
- all substantive comments would otherwise be accepted or selected
- current CAS/Codex findings are invariant-framed and would mutate code
- the no-change case is weak, generic, or reviewer-authority-shaped
- validation-only is rejected for a plausible unproven finding
- implementation would route to `$fixed-point-driver`
- comments are coupled through one governing invariant

## Adversarial Action Matrix

Emit this table after `Resolve Countercases`:

```md
| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
```

Allowed `veto status` values:

- `cleared`
- `preserved-no-change`
- `unresolved`
- `vetoed`
- `blocked`
- `not-required`

Allowed `clearance` values:

- `cleared`
- `preserved`
- `rerouted`
- `downgraded`
- `blocked`

## Clearance contract

- `address` requires `cleared` / `cleared`.
- `validate-only` requires `cleared` / `cleared` or `cleared` / `downgraded`.
- `resolve-thread-only` requires `cleared` or `preserved-no-change`, with
  `clearance: preserved`.
- `do-not-address` requires preserved no-change or explicit clearance for no
  action, with `clearance: preserved`.
- `blocked` requires unresolved/blocked status with `clearance: blocked`.

A vetoed or unresolved row blocks implementation unless it is explicitly rerouted
to a stricter non-mutating action and the new action receives its own warrant.
