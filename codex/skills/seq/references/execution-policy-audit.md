# Execution Policy Audit

Audit the full closed loop:

```text
EPG -> EPS -> EPD -> authority -> AFR/PAH/PAR -> ETR -> next EPS
```

Primary metrics:

```text
policy/source currentness
regime classification changes
critical unknown resolution latency
selected versus shielded actions
prediction calibration
unexpected observations
new-branch/model-failure/intent-failure rates
obligation and potential reduction
semantic-surface prediction error
proof sufficiency/staleness
commitment-horizon violations
same-state/action recurrence
rollback rate
implementation discarded
terminal proof and delivery
```

Do not treat:

```text
skill read
policy mention
context persistence
selected action without execution
```

as successful policy outcome.

Native work is specified in `SEQ_EXECUTION_POLICY_AUDIT_SPEC.md`.
