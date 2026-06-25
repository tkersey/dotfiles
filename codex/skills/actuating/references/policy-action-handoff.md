# Policy Action Handoff Through Existing ASL/FPS

No separate policy-action realization protocol is required.

Reuse:

```text
ASL-v1  mutation capability and semantic frontier
FPS-v1  bounded realization input
FPSR-v1 bounded realization result
```

Add the same `policy_control` block to ASL and FPS:

```yaml
policy_control:
  mode: epg
  policy_id:
  policy_revision:
  policy_digest:
  state_id:
  state_digest:
  decision_id:
  action_id:
  action_kind:
  policy_current: yes
  decision_selected: yes
  commitment_horizon_sequence:
  expected_effects:
  expected_observation_refs: []
  failure_observation_refs: []
```

FPSR returns matching policy identity plus observed effects/observations.

Root compiles those facts into ETR-v1; the fixed-point driver never advances EPS itself.
