# Cybernetic Stop-Rule Companion

Use `$cybernetic` when the same-cluster stop rule fires or review churn becomes a system pattern.

## Trigger

Require either `cybernetic_context` or an explicit `not-required` reason when:

- same-cluster stop rule fires;
- CAS/review finds adjacent findings after local fixes;
- review feedback becomes delayed feedback that keeps resetting closure;
- local proof passes but the next review finds the same family;
- surface grows while review findings continue;
- local-vs-whole tradeoff is plausible.

## Context

```yaml
cybernetic_context:
  required: yes | no
  trigger:
    same_cluster_stop_rule: yes | no
    repeated_review_feedback: yes | no
    local_fix_loop: yes | no
    incentive_or_metric_risk: yes | no
    delayed_feedback_risk: yes | no
    local_vs_whole_tradeoff: yes | no
  system_type: clear | complicated | complex | chaotic | mixed | unknown
  pattern: "..."
  feedback_loop: "..."
  leverage_level: parameter | information_flow | rules | goal | paradigm | none
  selected_intervention:
    route: validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | use-universalist | use-reduce | use-negative-ledger | blocked
    downstream_skill: "..."
  local_patch_allowed: yes | no
  monitoring_or_probe: "..."
```

## Rule

If `local_patch_allowed: no`, `$resolve` must not route another ordinary review-driven production mutation.

If `system_type: complex`, prefer safe-to-fail probe, review distillation, or normal-form decision over deterministic point-fix.

If `system_type: chaotic`, stabilize first; do not chase normal form until safety is restored.
