# Doctrine Phrases

## Definition

In this repo, **doctrine** is compact language selected to induce a useful and repeatable change in an agent's operating policy.

Doctrine can work through two distinct mechanisms:

- **operator doctrine** specifies a bounded procedure: `ablative`, `actuating`, `adjudicative`, `forensic`;
- **activation doctrine** evokes a capability state: `Be bolder.`, `Use fresh eyes.`, `Be Optimal.`, `Be like Mike.`

Operator doctrine compresses a rubric. Activation doctrine compresses permission, ambition, identity, attention, or search posture.

The governing rule is:

> **Design expansively; invoke tersely.**

The reference may explain why a phrase works, where it fails, and what it tends to activate. The runtime invocation should normally remain in its shortest effective form.

## Optimization target

Choose activation phrases for **behavioral leverage per token**:

```text
activation value =
  behavioral shift
  × task fit
  × memorability
  ÷ token cost
```

A phrase is strong when it causes a useful behavioral shift that a longer ordinary instruction often fails to induce.

## Artifact discipline

Do not require a ledger merely to justify an activation phrase.

Require an artifact, receipt, or proof only when:

- correctness depends on it;
- the result crosses an operational handoff;
- another agent must consume the decision;
- closure, mutation, publication, or authority depends on the claim;
- the user asks for the phrase's operational unpacking.

An activation phrase may remain terse while the receiving workflow supplies its own proof discipline.

## Invocation rules

- Return the shortest effective phrase by default.
- Use one phrase by default; use at most two unless the user asks for a stack.
- Do not append an explanation to the runtime phrase unless ambiguity would materially change behavior.
- Preserve unusual cadence when it appears to be part of the activation effect.
- Do not weaken a phrase by immediately restating it as a long checklist.
- Analyze mechanism, shadow risk, and task fit in this reference or in annotated mode—not in every invocation.
- Audit phrases empirically and retire those that add confidence or verbosity without improving outcomes.

## Output modes

### `activation-fast`

Return 1-5 phrases, strongest first. No explanation.

Example:

```text
Be bolder.
Be Optimal.
```

### `activation-annotated`

For each phrase return only:

- intended shift;
- best use;
- shadow risk.

### `activation-stack`

Return the smallest non-overlapping sequence of phrases and one line describing the progression.

Example:

```text
Use fresh eyes. Be bolder. Be Optimal.
```

```text
reset the frame -> widen the search -> select the best admissible move
```

## Core phrase registry

| Phrase | Intended shift | Best for | Shadow risk |
|---|---|---|---|
| `Use fresh eyes.` | loosen anchoring to inherited framing | re-review, stale diagnosis, repeated failed routes | needless rediscovery or novelty bias |
| `Be bolder.` | admit higher-upside, more structural moves | timid option sets, merely adequate answers | scope inflation or theatrical ambition |
| `Be Optimal.` | reject merely sufficient and locally optimal answers; select the best available move under the real objective and constraints | competing routes, designs, plans, interventions | fake omniscience, hidden objective choice, overoptimization |
| `Perform no smallness.` | raise the ambition floor and search for the compounding move | local polish when a governing move may dominate | grandeur mistaken for leverage |
| `Be like Mike.` | activate elite standards, fundamentals, finishing, competitiveness, and ownership | execution quality, pressure, completion | persona theater or importing irrelevant traits |
| `Dig deeper.` | move below the first plausible explanation | shallow diagnosis, symptom patches | analysis without route change |
| `Ruminate harder.` | sustain competing frames long enough to find the stronger one | ambiguous high-judgment decisions | indecision or token burn |
| `Reject the obvious answer.` | treat the first fluent answer as a candidate | anchoring, consensus, rubber-stamping | novelty bias against a correct simple answer |
| `Be reckless.` | expand the speculative search beyond convention and feasibility | read-only divergent exploration | operational recklessness or unsupported claims |
| `Find the lever.` | identify the control point that changes system state | analysis that has not become action | activity mistaken for movement |
| `Make it inevitable.` | seek a structure where correct behavior follows naturally | invariants, canonical ownership, illegal-state prevention | rigidity or over-abstraction |
| `Finish the thought.` | close partial reasoning, handling, or execution | incomplete analysis, partial eliminators, unfinished work | false certainty when genuinely blocked |
| `Show me the witness.` | demand concrete evidence for a material claim | soundness, review, verification | proof theater or irrelevant tests |
| `Solve the class, not the instance.` | look for the governing invariant or counterexample family | recurring local failures and review comments | unjustified generalization |
| `Delete before you add.` | counter addition bias | helpers, fallbacks, wrappers, adapters, flags | deleting live obligations |
| `Rebaseline before proceeding.` | bind to current authority and invalidate stale state | changed head, stale receipts, resumed workflows | discarding still-valid prior work |
| `Actuate the lever.` | convert insight into a state-changing move | plan-to-action transitions | premature action before understanding |
| `Do not deliver the scaffolding.` | retire temporary proof, migration, review, or exploration surface | closure and cleanup | removing still-live migration or safety support |

## Phrase cards

### Be Optimal

**Runtime form:**

```text
Be Optimal.
```

**Intended shift:**

Search beyond the first acceptable answer and select the best available move under the actual objective, constraints, evidence, uncertainty, and future-state effects.

**Internal decode:**

```text
CRITERIAL + DOMINANCE-TESTED + CYBERNETIC + CALIBRATED + ACTUATING
```

**Important distinction:**

`Be Optimal.` does not mean maximize one visible metric. It means identify the real objective, account for constraints and second-order effects, compare serious alternatives, and choose the move that dominates on the governing criteria.

**Shadow risks:**

- pretending the objective is known when it is not;
- claiming global optimality from incomplete search;
- optimizing a proxy instead of the real outcome;
- analysis paralysis from searching indefinitely;
- sacrificing robustness for a brittle theoretical maximum.

**When unpacking is required:**

Only when the objective or criteria are contested. Then ask:

```text
Optimal for what, under which constraints, over what horizon, and with what proof?
```

### Be like Mike

**Runtime form:**

```text
Be like Mike.
```

**Repo convention:**

Unless local context clearly identifies another Mike, `Mike` means **Michael Jordan** as a compact exemplar of:

- relentless fundamentals;
- an elite performance standard;
- competitive intensity;
- decisive finishing under pressure;
- ownership of the outcome.

The phrase selects those traits only. It does not import biography, celebrity mythology, interpersonal style, or unrelated behavior.

**Intended shift:**

Raise execution quality and competitive standard while keeping attention on fundamentals and completion.

**Shadow risks:**

- persona cosplay instead of better work;
- aggression replacing judgment;
- confidence replacing proof;
- competition against the wrong objective.

### Be bolder

**Runtime form:**

```text
Be bolder.
```

**Intended shift:**

Permit higher-upside, more structural, less deferential possibilities to enter consideration.

**Shadow risk:**

Do not interpret boldness as a larger patch. The boldest move may be deletion, rejection, simplification, or a single governing correction.

### Use fresh eyes

**Runtime form:**

```text
Use fresh eyes.
```

**Intended shift:**

Suspend inherited conclusions as authority and reconstruct the problem from current evidence.

**Shadow risk:**

Discard anchoring, not verified facts.

### Perform no smallness

**Runtime form:**

```text
Perform no smallness.
```

**Local meaning:**

Do not shrink the objective, frame, explanation, or intervention beneath the governing stakes merely to remain comfortable, conventional, or easy to approve.

**Shadow risk:**

No smallness in ambition does not authorize excess semantic surface.

### Be reckless

**Runtime form:**

```text
Be reckless.
```

**Intended shift:**

During a read-only speculative pass, admit possibilities that ordinary feasibility, convention, and politeness filters would suppress.

**Boundary:**

Recklessness applies to search, not to facts, mutation, authority, publication, or proof.

## Recommended stacks

### Escape a local optimum

```text
Use fresh eyes. Be bolder.
```

### Find and select the strongest move

```text
Be bolder. Be Optimal.
```

### Raise execution quality

```text
Be like Mike. Finish the thought.
```

### High-temperature search followed by selection

```text
Be reckless. Be Optimal.
```

The first phrase expands the candidate space. The second selects under the real objective and constraints.

### Full ambition without sloppy execution

```text
Perform no smallness. Be Optimal.
```

## Selection heuristics

Use **Be bolder** when the candidate set is timid.

Use **Be Optimal** when the candidate set exists but the model may settle for a merely sufficient or locally attractive answer.

Use **Be like Mike** when the gap is execution standard, fundamentals, competitive intensity, or finishing.

Use **Use fresh eyes** when prior framing may be suppressing the correct route.

Use **Perform no smallness** when the problem has been framed below its true stakes.

Use **Be reckless** only for speculative search that remains separated from action.

## Anti-patterns

Reject or repair:

- `Be smart.` — generic praise with weak activation specificity;
- `Be Optimal.` used without a knowable objective when the ambiguity is material;
- `Be like Mike.` when local context clearly points to a different Mike and no convention resolves it;
- phrase stacks made entirely of synonyms;
- a long explanation appended to a phrase whose value is brevity;
- runtime ledgers produced only to prove that an activation phrase was used;
- treating a phrase as evidence, authority, permission, or proof.

## Audit discipline

Activation phrases are empirical hypotheses. Track, when useful:

- phrase used;
- task family;
- behavioral or route delta;
- outcome evidence;
- token and verbosity cost;
- shadow failure;
- user correction;
- status: `observed-useful`, `promising`, `experimental`, or `retired`.

Promote phrases because they improve decisions or execution per token—not because they sound memorable.
