# Skill Candidacy v2

Portfolio shape:

```text
zero or one root repository skill
zero to five focused skills
```

No skill is mandatory.

Each criterion is evidence-bearing:

```yaml
recurring_trigger:
  verdict: yes | no | unknown
  evidence_refs: []
  counterevidence_refs: []
  rationale:
```

Positive criteria:

```text
recurring_trigger
consequential_decision
stable_governing_law
independent_activation
standalone_workflow
observable_success_and_failure
```

Negative criteria:

```text
better_as_code
better_as_test
better_as_tooling
better_as_docs
```

A trial recommendation requires all positive criteria `yes` and all negative
criteria `no`.

Status:

```text
rejected
recommended_for_trial
accepted
```

`accepted` additionally requires empirical use evidence. Initial doctrine should
normally use `recommended_for_trial`.

A candidate records governing law IDs, source claims, triggers, non-triggers,
consequential decisions, canonical prohibited route IDs, required artifacts,
success/failure signals, standalone use cases, and empirical evidence.

Reject directory-shaped, one-off, unstable-law, mechanically enforceable, or
root-duplicating candidates.
