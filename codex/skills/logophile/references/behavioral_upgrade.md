# Behavioral Upgrade Adjudication

Use this reference when `$logophile` is asked whether new wording, doctrine, a persona, a prompt, or an activation phrase is actually better than an existing version.

The governing invariant is:

> **The baseline is the incumbent. Do not replace it unless the candidate dominates behaviorally, not merely lexically.**

Semantic precision is evidence, not victory. A rarer, denser, or more elegant term may have a higher conceptual ceiling while producing a lower median outcome, higher decoding cost, narrower task coverage, or more variance.

## Scope

Use Behavioral Upgrade mode for:

- old-versus-new prompt comparison;
- doctrine-word replacement;
- activation-phrase replacement;
- skill, mode, persona, label, or heading upgrades where behavior matters;
- deciding whether a specialist term should replace a broad default;
- comparing terse exhortations with formal doctrine;
- evaluating a phrase stack as a small control program;
- planning or interpreting matched A/B trials.

Do not use it for ordinary copyediting when the user only wants cleaner prose and no behavioral policy is at stake.

## Output modes

### `upgrade-fast`

Return only:

```md
Verdict: retain | replace | specialize | pair | sequence | benchmark
Runtime Form:
[final wording]
```

### `upgrade-annotated`

Return the full Behavioral Upgrade Verdict, including role, policy delta, activation profile, stack effect, and evidence status.

### `upgrade-benchmark`

Return either:

- a matched benchmark plan; or
- an anonymized benchmark verdict when candidate outputs are supplied.

Do not claim a behavioral winner from semantics alone.

## Core workflow

```text
BASELINE
  -> ROLE MAP
  -> CANDIDATE LATTICE
  -> POLICY-DELTA CLASSIFICATION
  -> ACTIVATION PROFILE
  -> STACK TOPOLOGY
  -> CONTRASTIVE ADJUDICATION
  -> ABLATION TEST
  -> EMPIRICAL GATE
  -> VERDICT
```

## 1. Baseline: model the incumbent before editing

Treat the current wording as a functioning design, not raw material that must be improved.

Record what it already buys:

- task role;
- semantic breadth;
- activation immediacy;
- familiarity;
- decoding cost;
- cadence and memorability;
- emotional or motivational force;
- task-family coverage;
- stopping behavior;
- known success evidence;
- known failure modes.

A candidate does not win merely because its dictionary definition is more exact.

## 2. Role map

Assign each phrase or doctrine unit one or more operational roles:

```text
RESET          loosen anchoring and rebind attention
MAP            inspect the terrain and boundaries
DEEPEN         descend below the first explanation
DELIBERATE     reconsider or compare serious alternatives
HOLD-OPEN      preserve a genuine unresolved difficulty
DIVERGE        widen the candidate set
CREATE         produce a new form, representation, or possibility
SELECT         choose among serious candidates
ACTUATE        change the system state
VERIFY         demand evidence or a witness
CONVERGE       close ambiguity or iteration under a stop rule
STOP           identify the dispositive layer or completion condition
```

Hard rule:

> A replacement that changes the role is a policy change, not a wording upgrade.

Example:

```text
RUMINATE HARDER -> DELIBERATE
BE APORETIC     -> HOLD-OPEN
```

That is a specialization and role shift, not a semantics-preserving substitution.

## 3. Candidate lattice

Generate candidates at multiple levels rather than assuming the formal doctrine word is the best runtime expression:

```text
plain phrase
formal doctrine word
specialist doctrine word
persona or exemplar
phrase pair / sequence
no-change incumbent
```

Example:

```text
Formal doctrine: AUDACIOUS
Plain runtime:   Be bolder.
Specialist form: Challenge the inherited boundary.
```

The final answer may retain the plain phrase while recording the formal operator internally.

## 4. Policy-delta classification

Classify every proposed replacement as exactly one primary relation:

```text
equivalent
refinement
specialization
generalization
intensity-shift
register-shift
orthogonal-shift
polarity-shift
unknown
```

Definitions:

- **equivalent**: same role and practical task coverage, with no material policy change;
- **refinement**: same role, clearer procedure or stopping condition;
- **specialization**: narrower trigger or task family;
- **generalization**: broader trigger or task family;
- **intensity-shift**: same direction, different activation amplitude;
- **register-shift**: same intended behavior, different familiarity or decoding burden;
- **orthogonal-shift**: activates a different dimension;
- **polarity-shift**: reverses or materially redirects the posture;
- **unknown**: evidence cannot support a confident relation.

Hard rules:

- A specialization must not silently displace a general-purpose default.
- A register shift must justify its decoding cost.
- An intensity shift must name its overreach risk.
- An unknown relation defaults to `benchmark`, not `replace`.

## 5. Activation profile

Use this comparison when behavior, not just prose, matters:

```yaml
activation_profile:
  baseline: "..."
  candidate: "..."
  intended_role: "..."
  policy_relation: equivalent | refinement | specialization | generalization | intensity-shift | register-shift | orthogonal-shift | polarity-shift | unknown

  semantic_specificity: lower | equal | higher | unknown
  activation_immediacy: lower | equal | higher | unknown
  lexical_familiarity: lower | equal | higher | unknown
  decoding_cost: lower | equal | higher | unknown
  task_coverage: narrower | equal | broader | unknown
  cadence_fit: worse | equal | better | unknown
  token_cost: lower | equal | higher | unknown

  predicted_median: lower | equal | higher | unknown
  behavioral_ceiling: lower | equal | higher | unknown
  output_variance: lower | equal | higher | unknown
  shadow_risk: lower | equal | higher | unknown

  formal_doctrine: "..."
  runtime_form: "..."
  evidence_status: theoretical | promising | observed-useful | validated | task-specific | retired
  verdict: retain | replace | specialize | pair | sequence | benchmark
```

Never fabricate precision in these fields. `unknown` is valid.

## 6. Stack topology

A doctrine or activation stack is a small control program. Evaluate order and missing roles, not only word overlap.

Common topology:

```text
RESET
  -> MAP / DEEPEN
  -> DELIBERATE / HOLD-OPEN
  -> DIVERGE
  -> CREATE
  -> SELECT
  -> ACTUATE
  -> VERIFY
  -> STOP
```

Not every stack needs every role. Flag:

- expansion without selection;
- deliberation without a stopping operator;
- action before sufficient understanding;
- verification before a claim exists;
- `APORETIC` without an eventual `DISPOSITIVE`, `ADJUDICATIVE`, or experiment boundary;
- `EXCAVATORY` after the dispositive layer is already known;
- `AUDACIOUS + POIETIC` without a criterion that rejects useless novelty;
- multiple synonyms that amplify confidence but not intelligence;
- a formal term that weakens the original cadence or immediacy.

## 7. Contrastive adjudication

Evaluate the baseline and candidate against the same task distribution.

Ask:

- What does the candidate add?
- What does it remove?
- What does it narrow?
- What does it make slower to decode?
- What new failure mode does it introduce?
- What known baseline strength is at risk?
- Does the candidate change median reliability, ceiling, or variance?
- Would a pair or sequence preserve both advantages?

Do not describe the candidate in isolation.

## 8. Ablation test

For each new word in a phrase stack, remove it and ask whether a distinct behavioral function disappears.

```text
full stack
minus candidate A
minus candidate B
baseline plus A
baseline plus B
baseline plus A plus B
```

If removing a word does not change the predicted role map, the word is redundant.

When several replacements are proposed, change one variable at a time before judging the package.

## 9. Verdicts

### `retain`

The incumbent remains the best default.

Use when the candidate is only more sophisticated, narrower, slower to decode, or unsupported.

### `replace`

The candidate preserves the intended role and is predicted or demonstrated to dominate the baseline across the intended task distribution.

### `specialize`

Keep the incumbent as the broad default and add the candidate for a narrower trigger.

Example:

```text
Default:     Ruminate harder.
Specialist:  Be aporetic.  # genuine contradiction or underdetermination
```

### `pair`

Use both when they activate distinct simultaneous roles without destructive interference.

### `sequence`

Use both in order when one prepares the state for the next.

Example:

```text
Be bolder. Be Optimal.
```

### `benchmark`

Semantics cannot establish the winner. Run matched trials.

## 10. Formal doctrine versus runtime activation

Never assume the formal operator should replace the plain activation phrase.

```text
formal doctrine != automatically best runtime wording
```

Examples:

```text
Formal Doctrine: AUDACIOUS
Runtime Form:    Be bolder.
```

```text
Formal Doctrine: POIETIC
Runtime Form:    Operate poietically.
Alternative:     Create a new form.
```

```text
Formal Doctrine: APORETIC
Broad Runtime:   Ruminate harder.
Specialist Form: Remain with the contradiction.
```

Optimize runtime activation for behavioral leverage per token, not terminological prestige.

## 11. Empirical gate

Activation phrases are empirical hypotheses. For consequential replacements, prefer a matched evaluation.

Minimum benchmark design:

1. Select representative tasks from the intended distribution.
2. Hold model, settings, tools, context, and evaluation budget constant.
3. Run baseline and candidate independently.
4. Change one phrase at a time when possible.
5. Randomize and anonymize output order.
6. Evaluate correctness before novelty.
7. Record token and verbosity cost.
8. Repeat enough tasks to expose variance.
9. Retain the incumbent unless the candidate shows a meaningful advantage.

Suggested evaluation dimensions:

```text
correctness
material frame novelty
route quality
proof quality
completion
calibration
overreach
verbosity
token cost
user preference
```

A blind evaluator must not reward the candidate for rarer vocabulary, apparent sophistication, or knowledge of which version is newer.

## 12. Activation arbiter handoff

Use `activation_upgrade_arbiter` when anonymized baseline/candidate outputs are available or when a high-value replacement needs independent adjudication.

The generator should not be the sole judge of its own language.

The arbiter must:

- receive candidate IDs without baseline/new labels;
- score against declared criteria;
- name decisive differences and failure modes;
- return `tie` or `insufficient` when dominance is not established;
- never infer that more novel wording is better;
- preserve the incumbent when evidence is weak.

## 13. Evidence status

Track phrase and doctrine candidates internally as:

```text
theoretical     semantic mechanism only
promising       plausible mechanism plus limited encouraging use
observed-useful repeated use with route or outcome improvement
validated       matched evaluation supports the claim
task-specific   useful only for a named task family
retired         noise, overreach, regression, or no net gain
```

A newly coined term starts as `theoretical` or `promising`, never `validated`.

## Behavioral Upgrade Verdict

Use this shape in `upgrade-annotated`:

```md
Behavioral Upgrade Verdict:
- baseline:
- intended role:
- candidate:
- policy relation:
- semantic gain:
- activation gain:
- activation loss:
- task coverage:
- predicted median / ceiling / variance:
- decoding and token cost:
- stack effect:
- formal doctrine:
- recommended runtime form:
- evidence status:
- verdict: retain | replace | specialize | pair | sequence | benchmark
- confidence:
- next empirical test:
```

Put the final runtime wording at the tail.

## Worked example: `$glaze`

Baseline roles:

```text
DIG DEEPER       -> DEEPEN
RUMINATE HARDER  -> DELIBERATE
BE BOLDER        -> DIVERGE / AMPLIFY
MORE CREATIVE    -> CREATE
USE FRESH EYES   -> RESET
```

Candidate roles:

```text
BE EXCAVATORY       -> DEEPEN
BE APORETIC          -> HOLD-OPEN
BE AUDACIOUS         -> DIVERGE / AMPLIFY
OPERATE POIETICALLY  -> CREATE
USE FRESH EYES       -> RESET
```

Likely initial verdicts without benchmark evidence:

| Baseline | Candidate | Relation | Initial verdict |
|---|---|---|---|
| `DIG DEEPER` | `BE EXCAVATORY` | refinement + register shift | replace or benchmark |
| `RUMINATE HARDER` | `BE APORETIC` | specialization + role shift | specialize |
| `BE BOLDER` | `BE AUDACIOUS` | near-equivalent + register shift | benchmark |
| `MORE CREATIVE` | `OPERATE POIETICALLY` | specialization toward form-creation | specialize or benchmark |
| `USE FRESH EYES` | unchanged | retained | retain |

This table is more trustworthy than declaring every denser term an upgrade.

## Anti-patterns

Reject:

- lexical novelty presented as behavioral superiority;
- replacing a broad phrase with a specialist term without changing the trigger;
- changing several phrases at once and attributing the result to each one;
- evaluating the candidate but not the baseline;
- ignoring familiarity, cadence, or decoding cost;
- claiming global optimality from a small task sample;
- letting the generator grade its own unblinded outputs;
- rewarding verbosity, confidence, or rare vocabulary;
- forcing a replacement when `retain` or `specialize` is more accurate;
- treating user preference as proof of correctness, or correctness as proof of preferred style.

## Quality gate

A behavioral-upgrade recommendation is ready only when:

1. the incumbent's strengths are named;
2. baseline and candidate roles are explicit;
3. the policy relation is classified;
4. specialization and register shifts are not hidden;
5. median, ceiling, variance, coverage, and decoding cost are considered;
6. the stack remains topologically coherent;
7. `retain`, `specialize`, and `benchmark` are treated as successful outcomes;
8. empirical claims match the evidence;
9. the final runtime wording is short and copy-pasteable;
10. the recommendation explains what evidence would overturn it.
