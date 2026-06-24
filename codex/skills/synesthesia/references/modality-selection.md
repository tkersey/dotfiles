# Synesthesia Modality Selection

## Purpose

Choose a representation because its structure matches the available evidence, not because a phrase sounds vivid.

## Minimum-sufficient rule

```text
one modality if one independent dimension is enough
second modality only when it exposes a different technical dimension
more than two only with an explicit reason
```

A modality is redundant when removing it leaves the same technical translation, uncertainty, falsifier, and next move.

## Evidence-shape guide

| Evidence shape | Primary representation | Technical dimensions it may expose |
|---|---|---|
| dependencies, ownership, boundaries, layering | spatial | topology, direction, bottlenecks, boundary leakage, centrality |
| timing, retries, sequencing, concurrency | rhythmic or auditory | cadence, jitter, phase conflict, serialization, feedback |
| API or workflow interaction | tactile | friction, brittleness, hidden state, rollback cost, affordance |
| CPU, allocation, contention, saturation | thermal or pressure | concentration, accumulation, pressure transfer, cooling paths |
| state visibility, contrast, distribution, change | visual | hidden state, unstable contrast, spread, clustering, transitions |

This table maps evidence shapes to representational affordances. It is not a fixed metaphor ontology.

## Selection procedure

1. Name the literal evidence and unresolved question.
2. Choose the representation whose structure is most nearly isomorphic to that evidence.
3. State the engineering translation before elaborating the sensory language.
4. Add a second modality only when it answers a different question.
5. Remove any modality that does not change the diagnosis, explanation, comparison, or next move.

## Common mistakes

- **Synonym stacking:** several modalities restate “complex” without exposing independent dimensions.
- **Ontology substitution:** a canned phrase is treated as if it were an observed system property.
- **Unfalsifiable texture:** a description cannot be contradicted by code, traces, tests, or user behavior.
- **Aesthetic ranking:** one alternative is made to sound better without a stable comparison axis.
- **Narrative overrun:** implementation is narrated metaphorically after the route is already selected.

## Verification

For each material modality, answer:

```text
What literal evidence selected it?
What independent technical dimension does it expose?
What would falsify the translation?
What decision or explanation changes because of it?
```

If any answer is missing, omit or compress the modality.
