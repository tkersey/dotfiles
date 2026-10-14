# Skill coherence pilot — 2026-10-13

This is a small authoring evaluation using the existing
[workflow probes](../references/workflow-probes.md), [review economy](../references/review-economy.md), and
[Universalist contribution comparison](../../universalist/references/efficacy-evaluation.md).
It adds no production gate or review credit.

## Scope and controls

This retained report describes the original pilot, not later revisions of PR #338.
The follow-up changes to direct-assessment eligibility, catalog wording, and class
identity disclosure have not received paired model trials in this report. Moving
this record into `evals/` does not rerun or strengthen its historical evidence.

The candidate started from Dotfiles `b0fbdf72` with the skill changes in this PR.
Publication was subsequently rebased by applying only the skill patch to
`2cfb06af`. The synthetic tasks had no repository execution, network, publication,
or file-write authority. Separate agents received task facts without expected
answers or sibling results. No model override was supplied. Effective backend
model/version, reasoning configuration, token cost, and comparable latency were
not measured; these are not controlled performance trials. Each case/arm ran
once. There were no repeated trials or independent repository holdouts.

The Universalist source was unchanged at SHA-256
`82226a809228682dfe8c5cdc04ef71e40571818f793d74515d1b93733ce8766e`.
The other probes used the candidate Plan, Review Fold, Invariant Ace, and Ship
guidance. Later edits only clarified Invariant Ace's applicable report sections
and Architectonic's distinction between nomination and demonstrated success.

## Universalist artifact comparison

All arms received the same interleaved `start(components)` implementation and
requirements: an ordered finite iterable of at most 500 components, including
one-shot iterators; all registrations must succeed before any announcement;
registration failure propagates the same exception immediately with no later
registration or announcement; preserve both orders and empty behavior; no
rollback; announcement errors propagate normally. The interface stays unchanged.

| Arm | Treatment | Observed artifact |
|---|---|---|
| A | No skill or reference access | Two loops with a buffer of successfully registered components |
| B | Supplied trigger/owner/observations/law/falsifier/ordinary-candidate kernel, with grounded alternatives when relevant | Byte-identical to A |
| C | Full Universalist entrypoint, references only if their conditions apply | Byte-identical to A; loaded only the entrypoint |

All three returned:

```python
def start(components):
    registered = []
    for component in components:
        component.register()
        registered.append(component)
    for component in registered:
        component.announce()
```

Artifact SHA-256, including final newline:
`256673db5e9ecd3ea85ebb7abf0efb98be3c0852ee8ea5dbc2a5780bbf34e818`.
The agents correctly identified their code as unexecuted. The coordinator then
ran an independent trace oracle: list and one-shot inputs at lengths 0–8 and
500, successful runs, registration and announcement exceptions at every position,
exception-object identity, immediate iterator stop on registration failure, and
repeated objects. Each identical artifact passed 2,166 traces. The incumbent
interleaved implementation failed the two-component trace control. These tests
cover calls controlled by `start`, not hidden asynchronous effects inside methods.

**Disposition:** A = B = C on this one task. No incremental artifact benefit,
advanced-mechanic benefit, general routing accuracy, latency saving, or policy
change is established. The finite trace count is not a count of independent model
trials. Retain the existing construction-card limits and gather harder holdouts
before changing architecture guidance.

## Workflow decisions

The scenarios are repeatable from the matching table in
[workflow-probes.md](../references/workflow-probes.md).

| Probe | Observed decision |
|---|---|
| Bounded queue | Direct assessment, owner-level pre-mutation guard, implementation handoff allowed; unrun verification disclosed |
| Two-file/full-report queue | Same decision; no independent fanout solely for file count or presentation |
| Conflicting occurrence/descriptor witnesses | Blocked; requested owner, parity, induction, and boundary evidence |
| Unavailable restore mutator | Blocked queue-wide proof; no claim that enqueue tests cover the bypass |
| Historical H1 race at repaired H2 | Current allegation rejected; original history retained, recurrence unknown |
| Redundant serializer authentication | Placement preference rejected; required authentication preserved |
| Ordinary quiet-flag plan | Self-contained plan preserving stdout/errors/exits/defaults, verification and rollback; read five selected Plan files, without action/source/export references |
| Small CSV PR | Two sentences within managed markers, without empty headings |
| Caveated Linux watcher PR | Draft reason, missing platform tests, risk, and unfinished docs retained |

These nine decisions matched the intended distinctions. They are candidate-only
observations, not paired proof of improved quality. The Plan read count shows this
observed route, not a latency measurement or universal read reduction. No live
implementation, external PR mutation, canonical evidence write, or independent
authority clearance occurred inside these probes.

## Review repetition

Production Actuating and Ergasterion review counts remain unchanged. A retrospective
check is separate from the model probes above; only complete exact-head owner
receipts with round attribution and accepted findings could establish marginal
yield. Neither identical synthetic artifacts nor clean helper tests justify
reducing production review counts.

The bounded retrospective attempt discovered 641 local CAS receipt files and
selected the three most recently modified records. All three supported
`cas review wait --path ... --timeout-ms 1000 --json` observations failed with
`ConnectionTimedOut`; no new reviews were launched. Thus 0/3 attempted records
yielded a usable native result and zero complete same-head inventories were
established. Round attribution, material-defect yield, model configuration, and
cost remain unobserved. This is **inconclusive**, not three clean reviews or
evidence that later confirmations add no value. Resume the retrospective through
the owner interface when accessible; do not infer results from raw record counts.
