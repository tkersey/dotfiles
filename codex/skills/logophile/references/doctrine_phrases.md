# Doctrine Phrases

## Definition

In this repo, **doctrine** is a compact, reusable linguistic control surface that changes an agent's operating policy.

A doctrine unit may be a:

- **word** — a semantically dense operator such as `ablative`, `actuating`, or `forensic`;
- **phrase** — a memorable imperative, metaphor, slogan, or challenge such as `use fresh eyes`;
- **persona** — a role prior such as `Arbiter` or `Nomothete`;
- **stack** — a composition of non-overlapping doctrine units.

Doctrine is not tone, praise, or motivational decoration. It is valid only when it can be compiled into:

```text
trigger -> operator -> artifact -> receipt -> proof
```

A doctrine phrase is therefore:

> A short, memorable activation cue that uses imperative force, rhythm, metaphor, paradox, or exemplar imitation to evoke a useful operating posture, then cashes that posture out into explicit behavior and evidence.

Doctrine phrases can activate broader associative priors than technical doctrine words, but they are also more ambiguous. Every phrase must be decoded before it is trusted.

## Phrase compiler

Compile each phrase with this shape:

```yaml
doctrine_phrase:
  phrase: "..."
  class: perspective-reset | ambition-amplifier | exemplar-invocation | adversarial-challenge | action-forcing | proof-pressure | anti-locality | completion-pressure | axiom
  intended_behavior_shift: "..."
  decoded_operators: []
  trigger: "..."
  core_command: "..."
  cash_out_artifact: "..."
  proof: "..."
  guardrails: []
  common_misreadings: []
  evidence_status: observed-useful | promising | experimental | retired
```

### Evidence status

- `observed-useful`: repeated use produced route-changing artifacts or validated outcomes.
- `promising`: mechanism is clear and some use is encouraging, but evidence is limited.
- `experimental`: memorable but unvalidated, ambiguous, or likely to need tuning.
- `retired`: creates noise, overreach, imitation theater, or no procedural gain.

## Quality gates

Keep a doctrine phrase only when it passes all applicable gates:

1. **Behavioral delta** — it changes what the agent does, not merely how the answer sounds.
2. **Decodability** — the intended operators can be named precisely.
3. **Cash-out** — it creates a ledger, receipt, map, card, gate, decision row, or proof obligation.
4. **Bounded ambiguity** — plausible misreadings are named and controlled.
5. **Task fit** — the phrase activates the right pressure for the current task.
6. **Non-collision** — it does not silently conflict with scope, preservation, safety, or proof doctrine.
7. **Empirical revisability** — usage can be audited and the phrase can be promoted, narrowed, or retired.

## Usage rules

- Use one high-amplitude phrase by default; use at most two unless the user explicitly asks for a phrase stack.
- Follow the phrase with its decoded operator or concrete command when ambiguity is material.
- Do not let a phrase replace the task contract, evidence, constraints, or proof bar.
- Preserve unusual wording when its cadence or paradox appears to be part of the activation effect, but define it locally.
- Treat famous-person phrases as trait selectors, not complete specifications.
- A phrase with no artifact is an activation hypothesis, not operational doctrine.

## Core phrase registry

| Phrase | Class | Default decode | Cash-out artifact | Primary guardrail |
|---|---|---|---|---|
| `Use fresh eyes.` | perspective-reset | `DE NOVO` + `FORENSIC` + `REBASELINING` | Fresh-Eyes Receipt | Preserve verified facts; discard anchoring, not evidence. |
| `Be bolder.` | ambition-amplifier | `LEVER-SEEKING` + `DOMINANCE-TESTED` + `ACTUATING` | Bold Move Row | Bold means higher leverage, not larger unbounded scope. |
| `Perform no smallness.` | ambition-amplifier / paradoxical prohibition | full-strength framing + dominant-move search | No-Smallness Challenge | Reject timidity without rewarding grandiosity or overengineering. |
| `Be like Mike.` | exemplar-invocation | selected exemplar traits translated into task behavior | Exemplar Translation | Define `Mike` and selected traits; do not import mythology wholesale. |
| `Try to prove yourself wrong.` | adversarial-challenge | `ADVERSARIAL` + `FALSIFIABLE` | Strongest Countercase | Do not invent objections unsupported by the artifact. |
| `Solve the class, not the instance.` | anti-locality | `INVARIANT-SEEKING` + `CANONICALIZING` | Governing Invariant Row | Do not generalize beyond the witnessed counterexample family. |
| `Show me the witness.` | proof-pressure | `WITNESS-BEARING` + `TRACEABLE` | Witness Receipt | A test name or confident explanation is not automatically a witness. |
| `Actuate the lever.` | action-forcing | `ACTUATING` + `LEVER-SEEKING` | Actuation Receipt | Movement must be proved; activity is not movement. |
| `One truth, one owner.` | axiom | `CANONICALIZING` + owner-boundary discipline | Canonical Owner Map | Multiple projections may exist; only truth ownership must be singular. |
| `Delete before you add.` | anti-addition | `ABLATIVE` + `DOMINANCE-TESTED` | Ablation Receipt | Do not delete live obligations or promised compatibility. |
| `Finish the thought.` | completion-pressure | `TOTALIZING` + `CONSTRUCTIVE` | Completion / Totality Check | Do not force false certainty when the task is genuinely blocked. |
| `Rebaseline before proceeding.` | perspective-reset | `REBASELINING` + `STALE-PROOF` | Baseline Receipt | Preserve prior work that still matches current authority. |
| `What would this look like if it were easy?` | problem-shaping | `TRACTABILIZING` + representation search | Tractability Receipt | Easy must mean better-shaped, not hand-waved. |
| `Make the hidden state explicit.` | architecture | `REIFYING` + `TOTALIZING` | Behavior Algebra / State Model | Do not close a genuinely open extension surface without cause. |
| `No artifact, no doctrine.` | axiom | doctrine-compiler enforcement | named artifact or doctrine demotion | Tiny tasks may need no doctrine at all. |

## Detailed phrase cards

### Use fresh eyes

**Meaning**

Suspend prior proposed solutions, summaries, review conclusions, and inherited frames as authority. Reconstruct the narrowest current model from present artifacts.

**Decode**

```text
DE NOVO + FORENSIC + REBASELINING + ADVERSARIAL
```

**Cash-out**

```md
Fresh-Eyes Receipt:
- current authoritative state:
- prior frame suspended:
- verified facts preserved:
- new candidate frames:
- strongest countercase:
- conclusion changed: yes | no
- proof / next check:
```

**Guardrails**

- Do not erase verified facts, explicit requirements, or current proof.
- Do not restart bounded work merely to perform novelty.
- A fresh-eyes pass is valuable only when anchoring could change the route.

### Be bolder

**Meaning**

Raise the ambition of the candidate set. Search for the higher-leverage, more constitutive, or more system-improving move instead of settling for the first competent local answer.

**Decode**

```text
LEVER-SEEKING + DOMINANCE-TESTED + ACTUATING + CONSTITUTIVE
```

**Cash-out**

```md
Bold Move Row:
- competent local move:
- bolder candidate:
- leverage gained:
- future-state improvement:
- risk / scope bound:
- strongest countercase:
- proof signal:
```

**Guardrails**

- Boldness is not verbosity, certainty inflation, architecture theater, or scope expansion for its own sake.
- Prefer a larger conceptual move only when it dominates the local move and remains evidence-backed.

### Perform no smallness

**Local definition**

Treat this as a deliberately unusual, locally defined phrase:

> Do not shrink the objective, frame, explanation, or intervention beneath the governing stakes merely to remain comfortable, conventional, or easy to approve.

Its strangeness may be part of its activation effect. Preserve the wording, but never leave the meaning implicit.

**Decode**

```text
FULL-STRENGTH FRAMING + DOMINANCE-TESTED + LEVER-SEEKING + ACTUATING
```

**Cash-out**

```md
No-Smallness Challenge:
- governing stakes:
- artificially small framing:
- full-strength objective:
- largest credible move:
- bounds / non-goals:
- why this is not grandiosity:
- proof path:
```

**Guardrails**

- No smallness does not mean no bounds.
- Reject timid underreach and theatrical overreach equally.
- The selected move must remain tractable, owned, and proof-bearing.

### Be like Mike

**Meaning**

Invoke an exemplar to activate selected traits. The phrase is incomplete until `Mike` and the intended traits are resolved.

When the local intent is Michael Jordan, a reasonable default trait selection is:

- relentless fundamentals;
- competitive intensity;
- decisive finishing under pressure;
- ownership of the outcome.

Do not assume that decode when the context points to another Mike.

**Cash-out**

```md
Exemplar Translation:
- exemplar:
- selected traits:
- rejected / irrelevant traits:
- task translation:
- concrete behavior:
- artifact / proof:
```

**Guardrails**

- Imitate selected traits, not biography, mythology, celebrity, or irrelevant behavior.
- Do not use a famous name as a substitute for criteria.
- Prefer a direct doctrine phrase when the exemplar adds ambiguity without behavioral value.

## Phrase families

### Perspective reset

- `Use fresh eyes.`
- `Rebaseline before proceeding.`
- `Forget the patch; reconstruct the problem.`
- `Read the artifacts, not the story.`

### Ambition and amplitude

- `Be bolder.`
- `Perform no smallness.`
- `Reject the merely competent answer.`
- `Find the move that changes the future state.`

### Adversarial and proof pressure

- `Try to prove yourself wrong.`
- `Show me the witness.`
- `What would falsify this?`
- `Make the claim earn its confidence.`

### Anti-locality and canonicalization

- `Solve the class, not the instance.`
- `One truth, one owner.`
- `Fix the producer, not the tolerance path.`
- `Name the governing invariant.`

### Action and completion

- `Actuate the lever.`
- `Finish the thought.`
- `Do not stop at diagnosis.`
- `Prove the system moved.`

### Reduction and surface discipline

- `Delete before you add.`
- `Make every abstraction earn its keep.`
- `Collapse the shadow owner.`
- `Retain only live obligations.`

## Phrase stacking

A phrase stack should have distinct roles. Good:

```text
Use fresh eyes. Be bolder. Show me the witness.
```

Decode:

```text
reset the frame -> widen the candidate set -> demand proof
```

Bad:

```text
Be bold. Be fearless. Think big. Be ambitious.
```

The phrases overlap, provide no cash-out, and amplify confidence more than intelligence.

Recommended pattern:

```md
[one activation phrase]
Operate in [decoded doctrine mode(s)].
[exact task contract]
Produce [artifact / receipt / proof].
```

Example:

```md
Use fresh eyes.
Operate in DE NOVO, FORENSIC, and ADVERSARIAL mode.
Reconstruct the current changeset from current artifacts rather than prior review prose.
Produce a candidate inventory, strongest countercase, and current-state proof receipt.
```

## Audit discipline

Doctrine phrases are hypotheses about model activation. Audit them.

For each phrase, track:

- session/task;
- phrase used;
- decoded operator;
- artifact emitted;
- whether the route changed;
- evidence of better outcome;
- verbosity or overreach cost;
- user corrections;
- status promotion, narrowing, or retirement.

Promote phrases because they produce better decisions and artifacts, not because they sound memorable.
