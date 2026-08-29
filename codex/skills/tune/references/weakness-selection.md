# Weakness-first intervention selection

Load this reference when candidate skill changes differ in semantic scope, when
a short edit would introduce a broad rule, or when a regression guard risks
overfitting one episode.

The operative distinction is:

```text
semantic weakness != physical smallness
```

A one-line `always` rule can prohibit many lawful future behaviors. A coherent
multi-file alignment can be semantically weaker when it expresses one narrowly
conditioned rule consistently across `SKILL.md`, its decision contract, and
metadata.

This discipline adapts the central insight of Michael Timothy Bennett's *The
Optimal Choice of Hypothesis Is the Weakest, Not the Shortest* to skill changes:
an intervention should impose no more policy than the evidenced expected delta
requires. It does not assume that real skill invocations satisfy the paper's
formal task-distribution assumptions.

## Validity before weakness

A candidate enters comparison only when it:

1. produces the expected delta on supplied evidence;
2. preserves protected contracts and known valid near misses;
3. stays inside the authorized package surface;
4. introduces no contradiction, prohibited route, or unowned authority;
5. leaves the claimed effect observable.

An invalid candidate is not rescued by being weak, short, elegant, or cheap.

## Conservative dominance

For valid candidate `c`, let `E(c)` be the future target-skill episodes still
permitted by `c` after applying protected contracts and current evidence.

Candidate `a` is provably weaker than candidate `b` when:

```text
E(b) is a proper subset of E(a)
```

Everything `b` permits remains permitted by `a`, while `a` avoids at least one
restriction introduced by `b`.

When both are valid, reject `b` unless evidence supplies a material prior against
the additional behavior preserved by `a`. If neither extension contains the
other, the candidates are incomparable. Diff size and prose length cannot erase
that incomparability.

Do not fabricate a scalar weakness score or claim to know unenumerated extension
cardinalities.

## Decision procedure

1. Generate only plausible interventions inside the authorized boundary.
2. Reject invalid candidates.
3. State the rule each survivor adds, removes, or narrows.
4. Ask which future cases each rule newly forbids or requires.
5. Eliminate a strictly more specific candidate that buys no required
   correctness.
6. Preserve genuine incomparability.
7. State any evidenced domain prior that favors a more specific candidate.
8. Only after semantic selection, minimize realization cost or break a semantic
   tie.

Do not manufacture alternatives for ceremony. A single candidate is sufficient
when its validity and bounded scope are clear.

## Practical probes

- Is the rule bound to the witnessed trigger, clause, route, phase, or owner?
- What behavior outside the witnessed class does it newly forbid?
- Is each restriction required by evidence or a protected contract?
- Could a causal condition at the owning decision replace a downstream ban?
- Could an outcome relation replace exact wording, order, or artifact shape?
- Does a short sentence conceal `always`, `never`, unconditional activation, or
  a global prohibition?
- Were protected near misses and counterexamples tested?
- Can the target skill's vocabulary represent the needed distinction?

When the vocabulary cannot express the distinction, report a representation gap.
Do not claim a globally weakest candidate inside an inadequate language.

## Examples

### Missed activation

Observed: one review-closeout prompt failed to activate a skill.

Semantically stronger:

```text
Always activate for every review.
```

Weaker valid intervention:

```text
Activate when review-closeout cues and the required decision surface are both
present; preserve explicit non-trigger cases.
```

### Incomplete mutation authority

Observed: mutation occurred without a complete expected delta.

Semantically stronger:

```text
Never edit without a historical tuning packet.
```

Weaker valid intervention:

```text
In tune mode, block mutation when the expected delta or authorized boundary is
missing; preserve direct edit mode when the requested delta is already known.
```

### Ceremonial activation

Observed: repeated activation produced no decision delta.

Semantically stronger:

```text
Disable the skill outside explicit invocation.
```

Weaker valid intervention:

```text
Stop with no action when no consequential trigger, route, proof, package
surface, or lifecycle state would change.
```

## Physical realization

After semantic selection, prefer:

```text
no edit
delete or consolidate
clarify an existing rule
repair an existing artifact or operation
add one conditional reference
add a substantive operation
add consequential instrumentation
```

This order is a cost heuristic, not a semantic ranking. A longer realization is
correct when it faithfully expresses the weaker valid rule.
