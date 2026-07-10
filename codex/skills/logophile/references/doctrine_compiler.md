# Doctrine Compiler

Doctrine mode compiles words into agent behavior.

Use this pipeline:

```text
trigger -> operator -> artifact -> receipt -> proof
```

## Compiler fields

For each candidate word, identify:

- `trigger`: the task pressure that should activate it.
- `operator`: the behavior it makes the agent perform.
- `artifact`: the ledger, gate, receipt, card, map, certificate, or output section it produces.
- `proof`: the evidence that the operator actually changed behavior or state.
- `failure mode`: what goes wrong if the word is omitted or used decoratively.

## Mode, persona, command, and artifact

Keep these grammatical roles separate:

- **mode**: adjective or gerund describing the operating posture, such as `ACTUATING`, `ADJUDICATIVE`, `NOMOTHETIC`, or `EMULATIVE`;
- **persona**: noun naming the role, such as `Arbiter` or `Nomothete`;
- **command**: imperative phrase inside the doctrine, such as `actuate the lever` or `issue a criteria-backed ruling`;
- **artifact**: receipt, ledger, map, card, certificate, or gate proving the mode fired.

Do not use a persona noun as the mode when a precise adjective or gerund exists.

## Operator families

| Family | Purpose | Example words | Artifact |
|---|---|---|---|
| Action | move the system | `actuating`, `lever-seeking` | Actuation Receipt |
| Problem shaping | make the problem solvable | `tractabilizing`, `factorizing`, `orthogonalizing` | Tractability Receipt / Factorization Map |
| Reduction | remove unearned surface | `ablative`, `winnowing`, `quotienting` | Ablation Ledger / Reduction Certificate |
| Soundness | reject invalid guarantees | `unsound`, `unwitnessed`, `totalizing` | Soundness Ledger / Totality Table |
| Reset | restart from authority | `rebaselining`, `epoching` | Baseline Receipt / Epoch Boundary |
| Knowledge | extract truth from traces | `forensic`, `cartographic`, `saturating` | Provenance Map / System Map |
| Systems | model feedback and control | `cybernetic`, `leverage-seeking` | Cybernetic Map |
| Architecture | make hidden structure explicit | `reifying`, `algebraic`, `closed-world` | Behavior Algebra |
| Review | discriminate claims | `rebuttal-first`, `anti-rubber-stamp`, `invariant-seeking` | Resolve Selection / Countercase |
| Precedent | apply or establish governing rules | `precedential`, `nomothetic`, `constitutive` | Precedent Ledger / Nomothetic Receipt |
| Simulation | build and bound an executable surrogate | `emulative`, `counterfactual`, `dynamical`, `fidelity-bounded` | Emulation Receipt / Fidelity Boundary |
| Judgment | issue criteria-backed dispositions | `adjudicative`, `criterial`, `dispositive` | Adjudication Ledger / Criteria Matrix |
| Accounting | reconcile state, obligations, and residuals | `reconciling`, `conservation-aware` | Reconciliation Ledger / Conservation Ledger |

## Actuation Receipt

```md
Actuation Receipt:
- target state:
- current blocker:
- control point:
- lever:
- action:
- why this lever dominates:
- proof of movement:
- next bottleneck:
```

## Baseline Receipt

```md
Baseline Receipt:
- authoritative baseline:
- stale assumptions discarded:
- prior artifacts still valid:
- prior artifacts invalidated:
- current proof state:
- current open obligations:
- next action from baseline:
```

## Reduction Certificate

```yaml
reduction_certificate:
  live_contract:
    required_observations: []
    permitted_contractions: []
    forbidden_changes: []
  factorization:
    whole: "..."
    factors: []
    recomposition_rule: "..."
  quotient:
    equivalence_relation: "..."
    congruence_checks: []
    merged_factors: []
    retained_distinctions: []
  ablation:
    removed_factors: []
  normal_form:
    retained_factors: []
    canonical_owners: []
    orphan_surfaces: []
  preservation:
    relation: isomorphic | observationally-equivalent | refinement-preserving | intentional-contract-change
    proof_refs: []
  gate:
    every_live_obligation_covered: pass | fail
    every_removed_factor_accounted: pass | fail
    quotient_is_congruent: pass | fail
    recomposition_proved: pass | fail
    no_orphan_surface: pass | fail
```

## Behavior Algebra

```md
Behavior Algebra:
- closed behavior space:
- constructors / variants / commands:
- payload per case:
- interpreter / eliminator:
- totality table:
- preservation proof:
- why polymorphism/callbacks are insufficient or still better:
```

## Precedent Ledger

```yaml
precedent_ledger:
  - precedent_id: "..."
    source: "..."
    prior_case: "..."
    extracted_rule: "..."
    current_analogy: "..."
    distinguishing_facts: []
    status: binding | persuasive | distinguishable | stale | superseded | rejected
    action_delta: "..."
    proof_or_followup: "..."
```

## Nomothetic Receipt

```md
Nomothetic Receipt:
- decision:
- rule established:
- governing scope:
- non-governing cases:
- authority / evidence:
- future application:
- supersession condition:
```

Use persona `Nomothete` only when the user explicitly asks for a precedent-setting persona. The operating mode remains `NOMOTHETIC`.

## Emulation Receipt

```md
Emulation Receipt:
- real system:
- simulated boundary:
- state model:
- actions / inputs:
- transition rules:
- observations:
- fidelity target:
- known simplifications:
- validation probes:
- counterfactuals supported:
- counterfactuals not supported:
```

## Adjudication Ledger

```md
Adjudication Ledger:
- item / claim:
- standard:
- evidence:
- counterevidence:
- materiality:
- disposition:
- confidence:
- dispositive factor:
- what would change the ruling:
```

Use persona `Arbiter` only when the user explicitly asks for a judge/evaluator persona. The operating mode remains `ADJUDICATIVE`.

## Reconciliation Ledger

```md
Reconciliation Ledger:
- item / obligation:
- source:
- expected state:
- observed state:
- owner:
- evidence:
- delta / residual:
- disposition:
```

## Mode collision examples

- `isomorphic` + `ablative`: OK when deletion/collapse must preserve all observable behavior; not OK when the task intentionally retires invalid or obsolete behavior.
- `saturating` + `actuating`: OK when search stops after identifying the lever; not OK if saturation prevents action after enough evidence exists.
- `accretive` + `ablative`: OK because deleting unearned surface can improve the future state; resolve by saying “subtractive work is accretive when it reduces obligations while preserving the live contract.”
- `forensic` + `synthetic`: OK when provenance is preserved; not OK if synthesis drops source quality.
- `precedential` + `nomothetic`: OK when prior precedent informs a new scoped rule; not OK if the new rule silently inherits stale precedent.
- `emulative` + `counterfactual`: OK when the surrogate’s fidelity boundary covers the intervention; not OK when unsupported scenarios are presented as predictions.
- `adjudicative` + `actuating`: OK when a ruling authorizes an action; not OK when the evaluator also invents the criteria after seeing the preferred outcome.

## Quality bar

A recommended doctrine stack is good only if:

1. each word has a distinct job;
2. the stack changes behavior;
3. the artifacts are visible enough for the receiving agent;
4. the proof/receipt is clear;
5. near-miss words were rejected for a reason;
6. mode, persona, command, and artifact are not conflated.