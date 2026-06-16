# Decision Impact Reporting

Reports should track decisions, not appearances.

```yaml
decision_impact:
  - decision_id:
    phase:
    trigger:
    baseline_likely_action:
    selected_action:
    companion_skill:
      name:
      expected:
      evidence:
      causal_effect: none | confirmed_route | changed_route | blocked_route | deferred | unknown
    outcome:
      code_changed:
      production_net:
      test_net:
      proof_passed:
      same_cluster_recurred_after:
```

A skill is materially useful when it changes, confirms, blocks, or defers a route in a visible way.
