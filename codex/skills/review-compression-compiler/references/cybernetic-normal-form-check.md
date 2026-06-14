# Cybernetic Normal-Form Check

Use `$cybernetic` when review counterexamples may be a system feedback pattern.

## Add to resolve_decision_record or equivalent

```yaml
cybernetic_normal_form_check:
  system_type: clear | complicated | complex | chaotic | mixed | unknown
  pattern: "..."
  feedback_loop: "..."
  selected_leverage:
    level: parameter | information_flow | rules | goal | paradigm | none
    reason: "..."
  route_effect:
    changes_parameter: yes | no
    changes_information_flow: yes | no
    changes_rule: yes | no
    changes_goal: yes | no
    only_local_patch: yes | no
```

## Rule

After same-cluster recurrence, if `only_local_patch: yes`, block or require a stronger justification. Repeated local patches are not a normal form.
