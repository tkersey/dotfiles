# Context Compilation

Context compilation is the Kan/categorical-data mechanics behind Exact Context Doctrine.

## Core formula

```text
Context(q) = core_Obs(chase(migrate_{M_q}(I_candidate)))
DecisionPacket(q) = render(Context(q))
```

Use this when a semantic consumer should receive certified context rather than raw source data.

## Data

- `q`: task/question/decision/action.
- `S`: source schema/worlds.
- `I_candidate`: candidate source instance from retrieval, tools, operational stores, logs, documents, APIs, event streams, or databases.
- `T_q`: task-specific context schema.
- `M_q`: source-to-context mapping or dependencies.
- `Obs_q`: task-relevant observables.
- `J_q`: prepared context instance over `T_q`.

## Categorical reading

- `Delta`/restriction: drop or reindex irrelevant structure.
- `Sigma`/left pushforward: merge, coalesce, identify, quotient, summarize.
- `Pi`/right pushforward: join compatible evidence, complete support structures, gather all observations. Use with caution operationally.
- Chase/closure: enforce constraints, propagate equalities, represent missingness/contradiction.
- Core: minimize relative to observables.

## Verified Context Plane

```text
Operational Source Plane -> Candidate Plane -> Verified Context Plane -> Publication Plane -> Rendering Plane -> Semantic Consumption Plane
```

Placement rule:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

CQL/categorical databases are a reference implementation style when schemas, mappings, constraints, integration, and provenance dominate. They should normally surround operational stores rather than replace live mutable stores.

## Laws

- Schema law: `J_q` satisfies `T_q` constraints.
- Mapping law: source-to-context mapping preserves declared relationships and attributes.
- Constraint law: context violates no declared integrity constraints, or violations are explicit.
- Observable preservation: required observables are answered, missing, contradicted, or unsupported explicitly.
- Provenance law: every evidence-bearing claim has source/assumption/missingness path.
- Freshness law: sources satisfy task validity intervals at consumption time.
- Publication law: published context derives from stable source snapshot.
- Rendering law: rendered packet preserves required observables.
- Operational boundary law: semantic consumers read published context, not raw live stores, unless marked primitive exception.
