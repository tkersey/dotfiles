# Hylo grading, comparison, and causal progression

## What is being measured

Measure observable consequences, not resemblance to the historical answer:

```text
world outcome       repository or external state reached
trace behavior      tools, workers, ordering, permissions, budgets, side effects
answer quality      correctness, coverage, clarity, evidence, calibration
operational cost    tokens, latency, retries, and human intervention
```

The historical response is sealed diagnostic evidence. It may help identify a
failure after an authorized custody/grader reveal, but it is not a golden
answer and never supplies the replay-baseline denominator.

## Freeze evaluation before candidate execution

Freeze these contracts before the candidate runs:

```text
episode and split membership
counterfactual cut and target slots
world, runtime, tool registry, and effect policy
baseline and candidate bundle identities
trial pairs, repeats, order seed, and independence clusters
rubric dimensions and weights
hard gates and critical policy
oracle authority
absolute and pair grader authority
producer identities, binaries, keys, and roles
reveal, pass, stop, publication, and proof policy
```

Changed evaluation semantics require a new baseline, trial, or campaign. Do
not splice incomparable epochs into one trend.

## Hard gates before scores

Examples of hard gates:

```text
required output missing
forbidden side effect
path-scope violation
incorrect deterministic result
required test failure
schema invalid
critical oracle failure
hidden-reference exposure
target, world, runtime, tool, or grader drift
```

A hard-gate failure cannot be averaged away by a high scalar score.

Scored dimensions may include:

```text
task correctness
instruction fidelity
coverage
evidence quality
clarity
tool efficiency
latency
token cost
robustness
```

Use fixed-point or canonical decimal values on identity-bearing protocol
surfaces. Let native Ledger recompute aggregates and pass/fail policy; reject a
caller-supplied mismatch.

## Grader authority

Use the strongest available observation:

1. deterministic state, test, or schema assertion;
2. deterministic trace invariant;
3. model grader calibrated against human anchors;
4. human judgment.

Do not average genuine disagreement into false certainty. A model grader cannot
be the sole critical authority.

HCTP freezes grader producers by role, producer ID/version, binary
fingerprint, key ID, judge/oracle contract, and rubric fingerprint. Campaign
grades freeze judge, dimension, and oracle identities in the admitted syntax.
Ledger verifies declaration consistency and signed receipt lineage; an
uninspectable evidence reference remains a limitation.

## Blinding and commitments

Before reveal, the controller and runner must not receive:

- semantic arm identities;
- the historical response or hidden reference;
- later source-session outcomes;
- hidden oracle values;
- plaintext absolute grades;
- pair winner or pair rationale;
- grade openings;
- target-specific repair hints derived from sealed evidence.

Public pre-reveal output may contain commitments, fingerprints, producer
metadata, terminal state, and opaque acknowledgements.

For sealed assurance, use distinct role processes and anonymous descriptor
delivery. Record the truth: the current proof has role and cryptographic
separation with `os_confinement:false`, not hostile same-user isolation.

## Comparable paired evidence

A candidate is directly comparable with a baseline only when these agree:

```text
episode and source profile
counterfactual cut
world and world-availability identity
runtime and model projection
tool registry and effect policy
oracle and required observation surface
rubric and critical policy
absolute and pair grader authority
split, unit, independence cluster, and repeat contract
target common projection and target dependencies
hidden-reference visibility
```

The treatment bundle may differ. That planned difference is the intervention.

Every candidate lane requires a compatible replay-baseline lane from the
frozen pair. In the compatibility campaign fold, the replay-baseline attempt
must predate the candidate attempt for that scenario. Historical diagnostics
never satisfy this requirement.

Invalidate or label diagnostic any comparison with unexpected drift. Do not
repair drift by relabeling a target, world, runtime, grader, or oracle.

## Repeats and pairing

When deterministic seeds exist, pair them. Otherwise use frozen balanced order
and mandatory repeats for promotion claims.

Report:

```text
pair and repeat count
pass and failure count
median, minimum, maximum, and dispersion
critical violation count
position or order effects
independence-cluster coverage
latest consecutive passing cohort
null-trial or calibration result
```

The promotion cohort is the latest required complete cohort. A newer failure
reopens the frontier; older successes cannot be cherry-picked around it.

## Absolute and pair grades

An absolute lane grade answers whether one attempt satisfies the frozen rubric
and hard gates. A pair grade compares two opaque arms under the frozen pair
contract. Neither may see the semantic arm map before reveal.

Grade commitment/opening flow preserves:

```text
private grade outcome before reveal
public commitment identity
exact ordered request identity
producer signature and role
run-receipt binding
opening equality at reveal
```

Treat a missing or mismatched opening, wrong producer, wrong ordered pair,
unregistered receipt, or changed retry as invalid evidence rather than a
recoverable score.

## Observable behavior delta

After reveal, explain score changes using observable differences:

```text
target activation
tool and worker sequence
artifact reads and writes
constraint coverage
response structure
claims and citations
hard-gate outcomes
stop condition
cost and latency
```

A behavior delta bridges “the score changed” and “this observable mechanism
may have changed.” It does not reveal or infer private chain-of-thought.

## Claim vocabulary

Use:

```text
observed_association       two observations differ; causal validity unproved
comparison_valid_delta    frozen paired comparison supports the stated delta
practice_gain             comparable practice evidence improved
supported_mechanism       predictions held and controls survived within scope
refuted_mechanism         an explicit falsifier fired
regression                comparable evidence worsened materially
incomparable              a required comparison contract changed
insufficient_evidence     repeat, sample, uncertainty, or fidelity gate unmet
invalid                   custody, replay, grader, chain, or proof integrity failed
```

State dimension and denominator. “Instruction fidelity improved on 8/10
holdout units over three blind repeats” is meaningful; “the score improved” is
not.

Do not claim causality outside the admitted episodes, worlds, runtimes,
graders, and interventions.

## Failure signatures

A failure signature must be observable and reusable. Bind:

```text
predicate or hard-gate failure
episode families and independence clusters
affected dimensions
evidence references
applicability conditions
```

Prefer repeated signatures over anecdotes. One unexplained scalar decline is
not yet a mechanism.

## Causal hypotheses

A hypothesis must state:

```text
mechanism claim
observable evidence and failure signatures
applicability context
causal cut point
predicted affected scope
protected scope
bounded candidate intervention
explicit falsifiers
```

Statuses are typed, such as:

```text
proposed
eligible
supported
refuted
inconclusive
superseded
inapplicable
```

A supported hypothesis requires its predicted observation and surviving
controls. A score change alone is insufficient.

## Experiments

A target intervention must:

- reference an eligible hypothesis;
- change content-addressed target identity;
- stay inside owner authority, allowed paths, and semantic change budget;
- predict measurable changes on admitted practice units;
- name protected controls;
- name explicit falsifiers;
- classify reversibility;
- reserve enough untouched promotion attempts.

A read-only probe must answer one discriminating question, name the hypotheses
it separates, stay bounded in cost, and leave the target unchanged.

Previously refuted routes are ineligible under equivalent applicability
conditions unless new evidence proves that those conditions changed.

## Dominance and next-step selection

Evaluate eligible experiments with ordinal dimensions:

```text
evidence          direct | triangulated | speculative
discriminability unique | partial | none
coverage          multi_failure | single_failure | anecdotal
scope             single_rule | single_section | multi_surface
reversibility     complete | partial | poor
risk              low | bounded | high
cost              low | medium | high
```

Experiment A dominates B when A is no worse on the declared decision
dimensions, strictly better on at least one, and no broader in semantic scope.

The deterministic decision is:

```text
exactly one non-dominated eligible intervention -> RUN
multiple alternatives + bounded probe           -> OBSERVE
no eligible intervention                         -> STOP
multiple alternatives + no bounded probe        -> STOP
```

`RUN` selects one experiment but grants no edit authority. `OBSERVE` selects a
read-only probe. `STOP` is the honest answer when the evidence cannot justify
one obvious next step.

The stored `next_step_recorded` body must match Ledger's recomputed decision
exactly.

## Practice, holdout, and challenge discipline

Only practice evidence may shape a repair in the active campaign.

Use holdout and challenge evidence only after candidate lock. Once eligible
holdout or challenge evidence for the candidate is exposed, the campaign must
reject further changes from that target state. A miss means rejection or a new
campaign with untouched cases.

Keep family siblings and source-dependent cases in one split. Report practice
and holdout denominators separately.

## Promotion and publication

Keep these states distinct:

```text
selected    causal frontier emitted RUN
applied     owner changed the exact bounded target surface
promoted    complete blind cohort passed the frozen gate
committed   explicit publication authority produced an exact commit
pushed      separate remote authority published it
```

Promotion requires:

- exact evaluated bundle and target snapshot;
- latest complete repeat cohort for every required frozen unit;
- all hard gates and critical policies satisfied;
- no disallowed critical violation;
- intact null/calibration evidence where required;
- no grader, oracle, runtime, world, tool, or effect drift.

Publication additionally requires exact changed paths, exact commit/tree, and
equality between committed and promoted target projections. A successful
scalar alone cannot authorize publication.

## Stop rule

Stop when the compiled answer is `STOP`, when budget is exhausted, when the
environment or grader is invalid, when promotion evidence has been exposed and
the candidate misses, or when required owner authority is absent.

Stopping is scoped to the current episodes, world, runtime, rubric, target,
and budget. A materially new observation or campaign may reopen the work; an
urge to keep editing may not.
