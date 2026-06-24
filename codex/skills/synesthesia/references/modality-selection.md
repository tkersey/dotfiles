# Modality Selection

## Purpose

Choose representations from the shape of the evidence, not from a fixed metaphor dictionary.

A modality is useful only when it exposes an independent technical dimension or materially improves the user's mental model.

## Minimum-sufficient rule

Start with one modality. Add a second only when it answers a different technical question.

```text
one observation repeated in two vocabularies != two useful modalities
```

Use no more than three modalities, and only for genuinely multi-dimensional systems.

## Evidence-shape guide

| Evidence shape | Candidate modality | Technical dimension exposed |
|---|---|---|
| Dependencies, ownership, boundaries, topology | Spatial | adjacency, distance, bottlenecks, centrality, containment |
| Timing, sequencing, retries, concurrency | Auditory or rhythmic | cadence, phase, interruption, delay, synchronization |
| API or workflow interaction | Tactile | friction, resistance, brittleness, feedback, reversibility |
| CPU, allocation, saturation, contention | Thermal or pressure | concentration, buildup, dissipation, hot regions |
| State visibility, distribution, contrast | Visual | separation, gradients, flicker, occlusion, change over time |
| Several orthogonal dimensions | At most two initially | explicit independent axes only |

These are selection heuristics, not canonical mappings.

## Independence test

Before adding a modality, complete this sentence:

```text
This modality adds <technical dimension> that the existing model does not show.
```

Reject the modality when the answer is merely a synonym, aesthetic variation, or restatement of the same diagnosis.

## Mapping sources

Use mappings in this order:

1. Current user-defined mapping.
2. Applicable user-endorsed durable mapping for the exact scope.
3. Stable domain convention that is explicitly labeled as a convention.
4. Provisional mapping created for the current answer.

A provisional mapping must be presented as provisional and must not be admitted to memory without the normal evidence gate.

## Consistency

Within one scope:

- one phrase should retain one technical meaning;
- one technical distinction should not silently switch phrases;
- comparison axes must remain identical across alternatives;
- repo-local mappings must not be generalized globally;
- a changed mapping must be called out rather than silently substituted.

## Failure modes

Avoid:

- modality inflation;
- canned color or sound tables;
- sensory claims that imply unseen runtime facts;
- mutually inconsistent metaphors;
- using vividness to imply confidence;
- mapping every code smell to the same notion of heat, weight, or noise.
