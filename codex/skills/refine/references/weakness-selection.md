# Weakness-first intervention selection

This reference adapts Michael Timothy Bennett's *The Optimal Choice of Hypothesis Is the Weakest, Not the Shortest*, arXiv:2301.12987v4 (2024), to `$refine`'s intervention-selection problem:

- https://arxiv.org/abs/2301.12987
- https://arxiv.org/pdf/2301.12987v4

The paper's operative razor is:

> Explanations should be no more specific than necessary.

`$refine` applies the same discipline to skill changes: an intervention should impose no more policy than the evidenced expected delta requires.

## Translation into skill refinement

| Paper concept | `$refine` analogue |
|---|---|
| child task | supplied decision episodes, failure evidence, and brief |
| unknown parent task | future invocation family containing those observed cases |
| hypothesis | candidate intervention and the rule it installs |
| valid model | candidate satisfying the expected delta, protected contracts, and authority boundary |
| extension | future decision episodes still compatible with the changed skill |
| weaker hypothesis | valid candidate with a larger compatible-behavior extension |
| description length | prose length, diff size, file count, clause count, or implementation cost |

The central separation is:

```text
semantic weakness != physical smallness
```

A one-line `always` rule can be semantically strong because it forbids many future behaviors. A multi-file alignment edit can be semantically weak when it expresses one narrowly conditioned rule consistently across `SKILL.md`, its decision contract, and metadata.

## Validity before weakness

Weakness never authorizes permissiveness that violates the brief.

A candidate enters comparison only when it:

1. produces the expected delta on supplied evidence;
2. preserves protected contracts and known valid near misses;
3. stays inside the authorized files and intervention budget;
4. introduces no known prohibited route, contradiction, or authority transfer;
5. leaves the claimed effect observable.

An invalid candidate is not rescued by being weak, short, elegant, or cheap.

## Semantic dominance

For candidate `c`, let `E(c)` be the future target-skill episodes still permitted by `c` after applying protected contracts and known evidence. The paper measures weakness as the cardinality `|E(c)|`. `$refine` generally cannot enumerate that set, so it must not invent a scalar weakness score. Instead it uses inclusion as a conservative dominance proof.

Candidate `a` is **provably weaker** than candidate `b` when:

```text
E(b) is a proper subset of E(a)
```

In words: every future behavior allowed by `b` is also allowed by `a`, while `a` avoids at least one restriction introduced by `b`.

When both are valid, `b` is dominated unless evidence supplies a material prior against the additional behavior preserved by `a`. If neither extension contains the other, the candidates remain incomparable; description length cannot break that semantic incomparability.

## Decision procedure

1. Generate only plausible interventions inside the brief's boundary.
2. Reject candidates that fail validity.
3. State the rule each survivor adds, removes, or narrows.
4. Ask what future cases each rule newly forbids or requires.
5. Eliminate candidates that are strictly more specific without buying required correctness.
6. Record genuinely incomparable candidates rather than forcing a false ranking.
7. When evidence shows a nonuniform future distribution, use that domain prior explicitly.
8. Only after semantic selection, minimize the physical realization or use cost to break a semantic tie.

Do not manufacture multiple candidates for ceremony. A single candidate is sufficient when the receipt states why it is valid and why no broader rule is required.

## Practical weakness probes

Use these questions when exact extensions cannot be enumerated:

- Is the change scoped to the witnessed trigger, clause, route, phase, or owner?
- What behavior outside the witnessed class does it newly forbid?
- Is each new restriction required by evidence or a protected contract?
- Could a causal condition replace a blanket downstream guard?
- Could an outcome relation replace exact wording, ordering, or artifact shape?
- Does a short sentence conceal a global `always`, `never`, or unconditional activation rule?
- Were valid near misses tested alongside the triggering episode?
- Does the target skill's vocabulary make the relevant distinction representable?

If the last answer is no, report a representation gap. Do not claim to have found the weakest candidate inside a vocabulary that cannot express the needed distinction.

## Examples

### Missed activation

Observed: one review-closeout prompt failed to activate a skill.

Semantically stronger response:

```text
Always activate for every review.
```

Weaker valid response:

```text
Activate when review-closeout cues and the required decision surface are both present; preserve explicit non-trigger cases.
```

The second rule corrects the witnessed class while preserving more legitimate review behavior.

### Incomplete apply authority

Observed: mutation occurred with an incomplete expected delta.

Semantically stronger response:

```text
Never edit unless a Tune packet exists.
```

Weaker valid response:

```text
Block when the expected delta or authorized file boundary is missing; retain the explicit current-turn-defect route when those fields are complete.
```

The second rule excludes the failure without deleting an already lawful route.

### Ceremonial activation

Observed: repeated activation produced no decision delta.

Semantically stronger response:

```text
Disable the skill outside explicit invocation.
```

Weaker valid response:

```text
Stop with no action when no consequential clause, route, proof, or lifecycle state changes.
```

The second rule removes ceremony while preserving useful implicit cases.

## Assumption guard

Bennett's formal result depends on an enactive formalism, a finite implementable language, well-defined extensions, and a uniform distribution over tasks. Real skill invocations are not known to satisfy those assumptions.

Therefore `$refine` does **not** claim that weakness maximization is formally optimal for Codex skill packages. It imports three narrower disciplines:

1. description length is not semantic generality;
2. unnecessary specificity is a generalization liability;
3. semantic dominance should precede physical-cost minimization.

When a well-supported domain prior favors a more specific candidate, select it and record the prior. When candidates are incomparable, preserve the incomparability and use the brief's evidence, protected contracts, reversibility, and outcome observation rather than pretending the theorem supplies a total order.
