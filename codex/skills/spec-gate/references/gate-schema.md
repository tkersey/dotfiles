# Spec Gate Schema

```yaml
spec_gate:
  plan_allowed: false
  mutation_allowed: false
  strictness_profile: balanced
  missing_fields: []
  material_open_questions: []
  blocking_risks: []
  recommended_defaults: []
  clarification_receipt:
    grill_rounds: 0
    no_grill_justification: null
  next_grill_questions:
    - id:
      question:
      options:
        - label: "Recommended"
          consequence:
```

A gate pass does not mean the spec is good. It means planning is allowed. Mutation requires a later passing challenge, fresh-eyes pass, lint, and execution handoff.
