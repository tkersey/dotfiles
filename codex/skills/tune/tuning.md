# Tune mode

## Tune mode

Tune compares intended behavior with observed decision episodes and outcomes.

```text
activation evidence asks: was the skill present?
decision evidence asks: what changed because of it?
outcome evidence asks: was that change useful?
```

These implications are invalid:

```text
mention -> activation
activation -> decision influence
decision influence -> outcome causality
successful outcome -> skill effectiveness
```

Read [tuning-evidence.md](references/tuning-evidence.md) when historical,
provided, mixed, or attribution-sensitive evidence is needed. Use the passive Seq
definition there for bounded historical reconstruction.

For every material episode preserve the trigger, activation evidence, decision
question, selected route, rejected routes actually observed, exercised clauses,
decision effect, evidence strength, downstream signal, and counterevidence.
Do not invent unobserved alternatives.

Classify the smallest useful gap:

```text
activation | interpretation | workflow | tooling | resource
metadata | boundary | source-scope | decision-contract | observability
outcome | ceremony | overconstraint
```

Produce at most one dominant expected delta per cycle. Preserve denominators,
counterevidence, scope, and limitations. If no consequential decision,
execution, proof, lifecycle, or outcome relation should change, stop with
`no-change`.

Regression is an evidence shape, not a mode. Bind the prior failure, involved
trigger/clause/route, expected future behavior, and a reproduction query. Repair
the witnessed failure class without installing an unsupported global ban.
