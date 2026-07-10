# Doctrine Compiler

Doctrine mode compiles words into agent behavior.

Use this pipeline:

```text
trigger -> operator -> artifact -> receipt -> proof
```

For activation phrases, use the lighter pipeline in [doctrine_phrases.md](doctrine_phrases.md). For formal computer-science operators and distinctions, use [computer_science_doctrine.md](computer_science_doctrine.md).

## Compiler fields

For each candidate word, identify:

- `trigger`: the task pressure that should activate it.
- `operator`: the behavior it makes the agent perform.
- `artifact`: the ledger, gate, receipt, card, map, certificate, procedure, relation, or output section it produces.
- `proof`: the evidence that the operator actually changed behavior or state.
- `failure mode`: what goes wrong if the word is omitted or used decoratively.
- `formal burden`: what the term would require if interpreted literally.
- `lighter fallback`: the adjacent term to use when the full formal guarantee cannot be supported.

## Mode, persona, command, and artifact

Keep these grammatical roles separate:

- **mode**: adjective or gerund describing the operating posture, such as `ACTUATING`, `ADJUDICATIVE`, `NOMOTHETIC`, `EMULATIVE`, `CONFLUENT`, or `CONTRACTIVE`;
- **persona**: noun naming the role, such as `Arbiter` or `Nomothete`;
- **command**: imperative phrase inside the doctrine, such as `actuate the lever`, `make every pass shrink the gap`, or `issue a criteria-backed ruling`;
- **artifact**: receipt, ledger, relation, procedure, map, certificate, or gate proving the mode fired.

Do not use a persona noun as the mode when a precise adjective or gerund exists.

## Operator families

| Family | Purpose | Example words | Artifact |
|---|---|---|---|
| Action | move the system | `actuating`, `lever-seeking` | Actuation Receipt |
| Problem shaping | make the problem solvable | `tractabilizing`, `factorizing`, `orthogonalizing` | Tractability Receipt / Factorization Map |
| Reduction | remove unearned surface | `ablative`, `winnowing`, `quotienting` | Ablation Ledger / Reduction Certificate |
| Rewrite / convergence | make routes reconcile and stop | `confluent`, `terminating`, `contractive`, `critical-pair-aware` | Confluence Matrix / Contraction Measure |
| Semantics / equivalence | define what sameness means | `extensional`, `bisimulative`, `representation-independent` | Observation Contract / Bisimulation Relation |
| Generality | avoid special-case overfitting | `principal`, `parametric`, `conservative-extending` | Principal Solution / Parametricity Matrix |
| Program analysis | reason beyond sampled executions | `abstract-interpreting`, `symbolic`, `counterexample-guided` | Abstract Domain / Path Ledger / Refinement Ledger |
| Verification / oracles | test when expected output is partial or absent | `metamorphic`, `differential`, `shrinking`, `oracle-aware` | Oracle Map / Relation Suite / Minimal Counterexample |
| Concurrency | state the concurrent correctness model | `linearizable`, `serializable`, `atomic`, `commutative` | History / Serialization Graph |
| Distributed systems | state replication and partition semantics | `causally-consistent`, `eventually-consistent`, `quorum-aware`, `consensus-backed` | Consistency Contract |
| Recovery | converge from partial or dirty state | `self-stabilizing`, `transactional`, `idempotent`, `replayable` | Recovery Certificate |
| Search / optimization | search with bounds and incumbents | `anytime`, `admissible`, `branch-and-bound`, `approximation-aware` | Incumbent Receipt / Bound Ledger |
| Performance / dataflow | control recomputation and resource cost | `incremental`, `demand-driven`, `locality-aware`, `work-efficient` | Invalidation Graph / Work-Span Model |
| Security / authority | constrain influence and privilege | `least-authority`, `capability-secure`, `noninterfering`, `hygienic` | Capability Graph / Information-Flow Matrix |
| Data / schema | preserve information and constraints | `lossless`, `dependency-preserving`, `schema-evolution-aware`, `lineage-preserving` | Schema Evolution / Lineage Certificate |
| Soundness | reject invalid guarantees | `unsound`, `unwitnessed`, `totalizing` | Soundness Ledger / Totality Table |
| Reset | restart from authority | `rebaselining`, `epoching` | Baseline Receipt / Epoch Boundary |
| Knowledge | extract truth from traces | `forensic`, `cartographic`, `saturating` | Provenance Map / System Map |
| Systems | model feedback and control | `cybernetic`, `leverage-seeking` | Cybernetic Map |
| Architecture | make hidden structure explicit | `reifying`, `algebraic`, `closed-world`, `effect-explicit` | Behavior Algebra / Effect Signature |
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
    relation: isomorphic | bisimulative | observationally-equivalent | refinement-preserving | intentional-contract-change
    proof_refs: []
  gate:
    every_live_obligation_covered: pass | fail
    every_removed_factor_accounted: pass | fail
    quotient_is_congruent: pass | fail
    recomposition_proved: pass | fail
    no_orphan_surface: pass | fail
```

## Confluence Matrix

```yaml
confluence_matrix:
  initial_state: "..."
  rewrite_or_execution_paths:
    - path_id: "..."
      rules_or_actions: []
      result: "..."
  critical_pairs:
    - pair_id: "..."
      overlap: "..."
      left_result: "..."
      right_result: "..."
      join_state: "..."
      status: joinable | divergent | order-required | blocked
  canonical_normal_form: "..."
  termination_measure: "..."
```

## Contraction Measure

```md
Contraction Measure:
- target fixed point:
- distance metric:
- prior distance:
- current distance:
- strict decrease: yes | no
- non-contracting pass:
- reroute if non-contracting:
```

## Principal Solution

```yaml
principal_solution:
  constraints: []
  general_solution: "..."
  free_parameters: []
  instantiations:
    - case: "..."
      substitution: "..."
  rejected_special_cases: []
  proof_of_generality: "..."
```

## Behavioral Equivalence Certificate

```yaml
behavioral_equivalence:
  relation: isomorphic | bisimulative | observationally-equivalent | refinement-preserving
  state_or_value_relation: "..."
  observations: []
  forward_obligations: []
  backward_obligations: []
  unmatched_transitions: []
  proof_refs: []
  result: pass | validate-first | fail | blocked
```

## Counterexample Refinement Ledger

```yaml
counterexample_refinement:
  current_model_or_invariant: "..."
  counterexamples:
    - id: "..."
      minimal_form: "..."
      violated_claim: "..."
      abstraction_gap: "..."
      refinement: "..."
      new_distinction_witness: "..."
  wound_specific_patch_rejected: true | false
  resulting_model: "..."
```

## Oracle Map

```yaml
oracle_map:
  subject: "..."
  oracle_kind: exact | partial | relational | differential | statistical | human | absent
  direct_checks: []
  metamorphic_relations: []
  differential_peers: []
  unsupported_claims: []
  confidence_boundary: "..."
```

## Minimal Counterexample

```md
Minimal Counterexample:
- original failure:
- reduction dimensions:
- minimized input / state / trace / diff:
- failure still present:
- removed noise:
- governing mechanism:
```

## Concurrent History Contract

```yaml
concurrent_history:
  required_model: linearizable | serializable | causal | eventual | custom
  operations_or_transactions: []
  real_time_constraints: []
  candidate_order: []
  conflicts: []
  proof_or_counterexample: "..."
```

## Distributed Consistency Contract

```yaml
consistency_contract:
  model: linearizable | serializable | causal | eventual | quorum-based | consensus-backed
  authority: "..."
  partition_behavior: "..."
  stale_read_policy: "..."
  convergence_condition: "..."
  conflict_resolution: "..."
  visibility_or_lag_bound: "..."
  proof_or_test: "..."
```

## Recovery Certificate

```yaml
recovery_certificate:
  dirty_or_partial_states: []
  recovery_invariant: "..."
  retry_semantics: "..."
  idempotence_or_deduplication: "..."
  replay_source: "..."
  convergence_measure: "..."
  rollback_or_forward_repair: "..."
  proof_refs: []
```

## Anytime Incumbent Receipt

```md
Anytime Incumbent Receipt:
- current incumbent:
- validity proof:
- objective:
- current bound / quality:
- remaining gap:
- next search frontier:
- interruption-safe: yes | no
```

## Proof-Carrying Handoff

```yaml
proof_carrying_handoff:
  result: "..."
  assumptions: []
  applicability_boundary: "..."
  certificate_refs: []
  verifier: "..."
  stale_if: []
  downstream_authority: "..."
```

## Security Boundary Contract

```yaml
security_boundary:
  principals_or_components: []
  capabilities: []
  forbidden_influences: []
  mediation_points: []
  privilege_separation: []
  sandbox_limits: []
  side_channels_considered: []
  proof_or_test: "..."
```

## Schema Evolution Certificate

```yaml
schema_evolution:
  old_schema: "..."
  new_schema: "..."
  information_preserved: []
  information_retired: []
  defaults_or_unknown_fields: []
  compatibility:
    backward: pass | fail | not-required
    forward: pass | fail | not-required
  constraints_preserved: []
  migration_owner: "..."
  rollback_or_replay: "..."
```

## Behavior Algebra

```md
Behavior Algebra:
- closed behavior space:
- constructors / variants / commands:
- payload per case:
- interpreter / eliminator:
- totality table:
- effect signature:
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

## Formal-distinction checks

### Deterministic vs confluent

- `deterministic`: one prescribed next step or output for the same state/input.
- `confluent`: multiple valid paths may exist, but every divergence is joinable.
- Do not use `deterministic` when the system intentionally allows concurrent or reordered paths.

### Fixed-point vs contractive vs terminating

- `fixed-point`: describes a stable endpoint.
- `contractive`: each pass reduces a distance to that endpoint.
- `terminating`: the process cannot continue forever.
- A terminating process need not reach the desired fixed point; a fixed-point iteration need not be visibly contractive without a metric.

### Principal vs optimal

- `principal`: most general solution satisfying the constraints.
- `optimal`: best solution under a declared objective.
- Do not call a solution optimal when the objective, horizon, or search bound is missing.

### Isomorphic vs bisimulative vs extensional

- `isomorphic`: invertible structural correspondence.
- `bisimulative`: mutually matching observable transitions.
- `extensional` / `observationally-equivalent`: equal under selected observations.
- `refinement-preserving`: preserves required behavior while allowing forbidden or obsolete behavior to disappear.

### Sound vs complete vs total vs decidable

- `sound`: no invalid conclusions.
- `complete`: every valid conclusion is reachable.
- `total`: defined for every valid input.
- `decidable`: terminates with a judgment for every valid input.

### Traceable vs proof-carrying vs replayable

- `traceable`: evidence can be followed.
- `proof-carrying`: evidence travels with the artifact.
- `replayable`: captured state can reproduce behavior.

### Hermetic vs hygienic vs noninterfering

- `hermetic`: isolated from ambient dependencies.
- `hygienic`: transformations avoid unintended capture.
- `noninterfering`: forbidden influences cannot affect protected observations.

### Serializable vs linearizable

- `serializable`: concurrent transactions equal some serial transaction order.
- `linearizable`: individual operations also respect real-time order.

### Anytime vs exhaustive

- `anytime`: a valid best-so-far result exists at every interruption point.
- `exhaustive`: all material cases or branches are covered.
- An anytime process may be incomplete; an exhaustive process may offer no useful intermediate result.

## Mode collision examples

- `isomorphic` + `ablative`: OK when deletion/collapse must preserve all observable behavior; not OK when the task intentionally retires invalid or obsolete behavior.
- `saturating` + `actuating`: OK when search stops after identifying the lever; not OK if saturation prevents action after enough evidence exists.
- `accretive` + `ablative`: OK because deleting unearned surface can improve the future state.
- `forensic` + `synthetic`: OK when provenance is preserved; not OK if synthesis drops source quality.
- `precedential` + `nomothetic`: OK when prior precedent informs a new scoped rule; not OK if the new rule silently inherits stale precedent.
- `emulative` + `counterfactual`: OK when the fidelity boundary covers the intervention.
- `adjudicative` + `actuating`: OK when a ruling authorizes action; not OK when the evaluator invents criteria after seeing the preferred outcome.
- `deterministic` + `confluent`: often redundant or conceptually wrong; choose based on whether multiple valid paths are allowed.
- `principal` + `optimal`: compatible only when the principal solution is also evaluated under an explicit objective.
- `monotone` + `ablative`: compatible only when the order includes explicit supersession/tombstones or the deletion occurs outside the monotone accumulation layer.
- `eventually-consistent` + `linearizable`: contradictory for the same operation surface unless separate boundaries or modes are named.
- `anytime` + `fixed-point`: useful when every interrupted state is valid and the final state still has a fixed-point gate.
- `hygienic` + `hermetic`: complementary; one prevents capture, the other ambient dependency.

## Quality bar

A recommended doctrine stack is good only if:

1. each word has a distinct job;
2. the stack changes behavior;
3. the artifacts are visible enough for the receiving agent;
4. the proof/receipt is clear;
5. near-miss words were rejected for a reason;
6. mode, persona, command, and artifact are not conflated;
7. formal computer-science terms retain their actual distinction;
8. the requested proof burden is proportionate to the strength of the word;
9. a lighter fallback is used when the formal guarantee cannot be established;
10. the stack remains small enough to steer rather than enumerate the whole glossary.
