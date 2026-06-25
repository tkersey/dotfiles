# Policy Synthesis Fixed Point

`$plan` must exhaustively refine the candidate execution policy before emission.

This restores the strongest feature of the earlier `$plan`: repeated improvement
until the plan has no remaining material execution improvement.

It does **not** restore public iteration ceremony.

## Sweep lenses

A complete sweep includes:

```text
source_fidelity
semantic_authority
system_regime
belief_and_observation
action_completeness
policy_closure
safety_and_rollback
proof_and_terminal_state
simplicity_and_st_compileability
```

## Loop

```text
compile initial candidate
run lenses in order
if a lens finds material improvement:
  apply the minimal source-preserving improvement
  restart from the earliest affected lens

if a lens finds a material semantic gap:
  return_to_spec or return_to_grill

if a full sweep is clean:
  run independent fresh-eyes pass

if fresh eyes finds material issue:
  apply or route it, then restart affected lenses

otherwise:
  convergence reached
```

## No fixed cap

Do not stop because of an iteration count.

Stop only for:

```text
convergence
return_to_spec
return_to_grill
blocked
user stop
tool/safety limit
```

If forced to stop before convergence:

```text
improvements_exhausted = false
```

## Mandatory radical candidate

After the policy is apparently converged, generate the strongest non-obvious
candidate improvement.

The candidate is mandatory.

Adoption is not mandatory.

If the disposition is `adopt`, apply the candidate and restart synthesis from
the earliest affected lens before finalization. The final policy digest must
belong to the post-adoption clean sweep and fresh-eyes pass, not to the policy
state that existed before the radical candidate changed it.

Valid dispositions:

```text
adopt
reject
defer
return_to_spec
none
```

A rejected candidate should explain the governing reason:

```text
source-expanding
unsafe
surface-increasing
not execution-relevant
worse than current policy
needs evidence outside the horizon
```

## PSR-v1 receipt

```yaml
policy_synthesis_receipt:
  receipt_version: PSR-v1
  plan_id:
  revision:
  source_digest:
  initial_policy_digest:
  final_policy_digest:
  passes:
    - pass_id:
      lens:
      candidate_digest_before:
      candidate_digest_after:
      findings: []
      material_changes: []
      disposition:
        changed |
        clean |
        blocked |
        return_to_spec |
        return_to_grill
  radical_candidate:
    candidate:
    disposition:
      adopt |
      reject |
      defer |
      return_to_spec |
      none
    reason:
    affected_refs: []
  convergence:
    complete_clean_sweep:
    independent_press_pass_clean:
    unresolved_errors:
    untreated_material_risks:
    improvements_exhausted:
```

## Final output policy

The final plan may summarize PSR-v1.

It should not include:

```text
draft-by-draft logs
Iteration: N footers
rewrite-ratio self claims
fabricated no-op rows
mandatory addition just to show creativity
```

## Readiness invariant

```text
policy ready
=
complete clean sweep
+ clean fresh-eyes pass
+ radical candidate evaluated
+ no unresolved blockers
+ source-current handoff
```
