# Context Compilation

Context compilation is the Kan/categorical-data mechanics behind Exact Context Doctrine.

## Core formula

```text
Context(q) = core_Obs(chase(migrate_{M_q}(I_candidate)))
DecisionPacket(q) = render(Context(q))
```

Use this when a semantic consumer should receive certified context rather than raw retrieved data.

## Data

- `q`: task/question/decision/action.
- `S`: source schema/worlds.
- `I_candidate`: candidate source instance from retrieval, tools, memory, logs, documents, or databases.
- `T_q`: task-specific context schema.
- `M_q`: source-to-context mapping or dependencies.
- `Obs_q`: task-relevant observables.
- `J_q`: prepared context instance over `T_q`.

## Categorical reading

- `Delta`/restriction: drop or reindex irrelevant structure.
- `Sigma`/left pushforward: merge, coalesce, identify, quotient, summarize.
- `Pi`/right pushforward: join compatible evidence, complete support structures, gather all observations.
- Chase: enforce constraints, propagate equalities, represent missingness/contradiction.
- Core: minimize relative to observables.

## Laws

- Schema law: `J_q` satisfies `T_q` constraints.
- Observable preservation: required observables are answered, missing, contradicted, or unsupported explicitly.
- Provenance law: every evidence-bearing claim has source/assumption/missingness path.
- Freshness law: sources satisfy task validity intervals at consumption time.
- Rendering law: rendered packet preserves required observables.
