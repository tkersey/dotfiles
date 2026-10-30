# Claim-appropriate proof

Use the applicable section when a decision-critical premise needs investigation,
a model result needs implementation correspondence, or a representation-independence,
universal-construction, lawful-transformation, or bounded-approximation claim is
live. Inquiry needs no finished proof. Reuse the existing argument; this module
adds neither a packet nor a route. Ordinary boundary contracts already carry
their construction and preservation laws.

Use [universal witnesses](#universal-witness-contract) for universal claims,
[transport](#transport-across-interpretations) when moving an argument between
worlds, [determination](#determination-before-cancellation) before inferring a
stronger equality, and [endpoint correspondence](#endpoint-specific-correspondence)
only for lifting or distinguishability claims. Keep each check inside the
existing argument.

Keep claim kind separate from realization strength. A lawful categorical model
(`structure`) is not automatically a universal construction (`universal`).
Use the existing proof-profile surface; do not add a workflow or route.

For a **structure** claim, establish the carrier and operations, their applicable
laws, preservation by interpretation and permitted operations, effectivity, and a
discriminating counterexample. A coalgebra needs transition/observation laws,
not finality. An observation vocabulary needs preservation and, before quotienting,
adequacy under required future continuations, not a fabricated Yoneda argument.
A lawful transformation needs its hypotheses and observation-preserving equation;
performance or resource improvements need their own evidence.

Information hiding can realize an abstract interface of operations, laws, and
sanctioned observations without exposing its representation. To claim representation
independence, establish a relation preserved by public construction and every
permitted operation, with agreement on required observations and future continuations;
account for aliasing, lifetime, effects, and bypasses where relevant. For a functional
abstraction `alpha: R -> A` and matched unary operations, the commuting obligation is
`alpha o op_R = op_A o alpha`; observations must agree through `alpha` as well.
Use the appropriate simulation or relational argument when a functional abstraction
is not justified. Do not force this model onto every interface or infer the claim
from opacity. If distinctions are quotiented, the equivalence must respect permitted
operations and required future observations, not merely today's examples.

Lower caller burden is a context-relative design benefit, not an initiality,
finality, parametricity, equivalence, or uniqueness proof. Preserve the selected
claim's existing proof profile; an ordinary encapsulation needs no invented
universal construction, and a genuine universal claim still needs its witness.

## Premise-guided investigation

When resolving uncertainty can change the construction or deciding proof, ask:
**which premise supports the conclusion, and what available evidence would
separate it from a plausible alternative?** Inspect source when it can decide the
question; use an already-authorized safe experiment only when needed. Reuse a
sufficient argument without manufacturing doubt, a dependency graph, a competing
model, or a probe quota. The argument may still be developing.

Follow dependencies, but also inspect the relevant source-permitted behavior that
the model omits: ingress, recovery, aliases, effects, or observations may cross its
boundary without appearing in its proof. Reuse the receiving workflow's independent
coverage evidence; a candidate-authored list of transitions cannot certify its own
completeness. Focus on behavior material to the claim, not a speculative whole-system
inventory. Missing access stays evidence debt, not proof of impossibility.

For example, `check receipt; perform external effect; persist receipt` cannot get
an at-most-once guarantee merely from a two-state model that combines the effect
and receipt into one transition. The deciding premise is atomicity across their
actual owners. Inspect that boundary or, when authorized, interrupt after effect
commit but before durable receipt and then recover. Observe the external effect
count, not just the final receipt. Two distinct logical operations with identical
payloads remain a required-valid control when the contract distinguishes them.

A transaction covering both operations or evidenced durable external idempotency
may support a construction; their mere names do not. Otherwise keep the affected
guarantee unresolved or expose its residual failure behavior. A local enum cannot
supply missing external atomicity. A contradiction may require changing the model's
states, operations, observation, or interpretation rather than patching the code to
conform to a false model. Accepted requirements remain binding.

In Actuating, return the deciding discriminator through its existing argument;
Actuating owns experiments, mutation, and review epochs. In read-only analysis,
propose rather than execute an experiment. A new premise does not authorize a
production fault injection, nested workflow, or separate evidence store.

## Claim-directed correspondence

Keep structural lawfulness, a theorem about a model, and its application to the
implementation separate. Select the weakest adequate connection for the actual
claim, not a complete simulator or equivalence proof by default. For a function
`alpha` from relevant real traces to model traces, one sufficient safety transfer is:

```text
alpha(T_real) subseteq T_model
Bad_real(t) => Bad_model(alpha(t))
no trace in T_model is Bad_model
therefore no trace in T_real is Bad_real
```

The abstraction must cover the claimed real initial states and transitions and
preserve the violation being excluded. A model may overapproximate behavior; it
must not silently omit a real counterexample. Successful recorded traces alone
establish neither that coverage nor impossibility. Use a relation/simulation or
direct argument when a functional abstraction is inappropriate; this equation is
one sufficient form, not a new required representation.

A successful model plan needs realization of that particular witness, including
its preconditions, observations, authority, effects, failures, and resources. An
overapproximation can contain spurious successes. A behavioral replacement needs
the promised equivalence or refinement under required continuations; do not infer
it from one-way safety transfer. Eventual completion needs its own progress and,
when relevant, scheduling/fairness assumptions, not just an invariant.

Often the actual implementation admits a smaller direct certificate:

```text
Init(s) => I(s)
I(s) and R(s,a,s_next) => I(s_next)
I(s) => P(s)
```

For all admitted initial states and relevant implementation transitions `R`,
induction establishes `P` on reachable states. Cover ingress, recovery, and external
behavior relevant to the claim at their actual owners; do not call a restricted
surrogate `R` complete. Reuse an adequate native proof or existing model rather than
requiring a second implementation. A property-specific proof view need not replace
production state or preserve observations outside that property; its limitations
must not be inherited by the production contract.

When a machine-checked proof supplies evidence, bind the actual theorem statement,
definitions, assumptions, admitted initial states, goal, source version, and
implementation interpretation. Check trusted assumptions and unfinished proof
placeholders using the proof system's facilities. Kernel acceptance validates the
formal statement, not its intended meaning or its parser/implementation connection.
A short definitional proof can be exactly the benefit of a sound construction;
proof length is not evidence strength. Keep runtime-cost claims separately grounded.

## Universal witness contract

Only a nomination that claims a **universal construction** additionally requires
an explicit diagram, admissible competitors and maps, factorization equations,
and a uniqueness argument. The full profile is:

```text
Existence:
  the repository-native artifact or bounded approximation can be built.

Preservation:
  required observations, invariants, compatibility, and effects commute.

Mediation:
  every admissible competitor has the required comparison path.

Canonicality:
  the structure-respecting comparison is unique under the declared equivalence;
  any normalization used to decide it has a justified correspondence to that equality.

Effectivity:
  construction, comparison, validation, interpretation, and invalidation fit
  the budget.

Falsifier:
  a nearby weaker or illegal construction fails observably.
```

Opacity, a single public interpreter, canonical IDs, and removal of bypasses
may enforce a representation. They do not by themselves prove mediation or
uniqueness. Show why every admissible competitor factors and why two mediators
with the required equations are equal under the declared equivalence. Tests can
falsify a claim or exhaust a finite universe; sampled success is not a universal
proof. Any restriction of the competitor universe must come from requirements
or an explicitly bounded claim, not from excluding an inconvenient alternative.

The universal object includes its legs, projections, injections, or other named
structure. Uniqueness compares mediators that respect that entire structure; an
isomorphism of the underlying carrier alone does not establish it. Multiple
factories may realize the same universal construction, while a single factory
may expose a non-universal one.

When a universal claim fails, locate the missing obligation before choosing the
next discriminator: no admissible artifact has been constructed; an admissible
competitor has no mediator satisfying the equations; or two inequivalent mediators
satisfy them. The first needs a construction or a scoped impossibility argument,
the second a factorization witness or counterexample, and the third a uniqueness
argument or a distinguishing observation. A failed candidate or unavailable proof
does not establish that every construction is obstructed.

A missing universal proof is evidence debt about that stronger claim, not an
obstruction to an adequate structure-only implementation. Nominate the weaker
honest artifact when it suffices, without silently retaining universal wording.

## Transport across interpretations

Before moving a result through an interpreter, name the source and target maps
and distinguish **preservation** (source evidence implies target evidence) from
**reflection** (target evidence implies source evidence). Carry an explicit
witness when its equations supply the needed transport and eliminate repeated
construction or search.

For example, let `p: E -> B` and `s: B -> E` satisfy `p o s = id_B`. The map `s`
is a section of `p`: it builds a representative of every admitted `B`. A covariant
functor `F` carries that witness because it preserves composition and identities:

```text
F(p) o F(s) = F(p o s) = F(id_B) = id_F(B)
```

An ordinary builder plus projection and this round-trip law may therefore remove
repeated realization logic across interpreters. The opposite round trip is not
required. Check that the builder is an actual admissible map and the interpreter
satisfies the relevant functor laws; partial, effectful, or context-dependent code
needs its corresponding model and preservation argument. A bare epic or another
property quantified over all maps in the ambient category is not automatically
preserved by an arbitrary functor. Do not transport an unproved universal claim
merely because an artifact has been translated, or reflect equality through a
lossy interpretation without a determination argument. Resource savings still
need the existing workload evidence.

## Determination before cancellation

From `h o a = h o b`, infer `a = b` only if the evidence determines those maps.
A monic `h` permits this cancellation for every admissible pair; separation on
the relevant range or a direct argument may suffice for the particular pair.
Dually, from `a o e = b o e`, an epic `e` permits cancellation uniformly; a
generating input family can suffice for the actual claim. Do not demand global
monicity or epicity when the narrower determination argument already closes it.

For example, equal absolute values do not determine signed values. A status
normalizer can hide duplicate effects. Agreement on generated inputs can miss
required imported or legacy states. Before a test or interpreter's equality is
used to prove a stronger internal law, establish adequate observers or generators
for that inference. If the requirement is intentionally only the sanctioned,
lossy observation, preserve that observation and its required continuations;
there is no obligation to expose the representation or prove literal equality.

## Endpoint-specific correspondence

Use this discriminator only when a transformation claims to lift target
operations or distinguish source operations. A functor preserves identities and
composition of already composable source maps. For each relevant endpoint pair,
the correspondence is `C(x,y) -> D(Fx,Fy)`: **faithful** means injective on this
hom-set, and **full** means surjective. The required property may be proved for a
relevant family of pairs without a manual exhaustive matrix. A global mapping
of operation names does not establish either property.

Include empty source hom-sets when lifting is claimed. If distinct endpoints
`x,y` collapse to one target object, its identity lies in `D(Fx,Fy)` even when
`C(x,y)` is empty. An adapter that erases a tenant, owner, capability, or state
index can consequently admit a transition with no permitted source realization.
Retain the relevant index or provide an explicit admissible adapter when the
requirement demands it.

Do not impose full faithfulness on an intentionally forgetting interpretation
or on composition preservation alone. Even a fully faithful functor can identify
isomorphic objects: strict endpoint identity, authority, and literal source
composability need their own argument when required. Full faithfulness by itself
does not supply those stronger guarantees.

## Realization strength

State claim strength:

```text
literal
effective realization
bounded approximation
```

These strengths apply independently to structure and universal claims. A bounded
approximation states its domain, included and excluded behaviors or competitors,
possible losses, evidence strength, and refinement condition. It must not erase
required distinctions or reject required-valid behavior without declaring the
remaining requirement residual or obstructed. Neither disposition discharges it.

## Source and application boundary

Eugenia Cheng, [*The Joy of Abstraction*](https://doi.org/10.1017/9781108769389):
§§16.4, 16.6 and 18.3–18.4 (pp. 211–217, 243–244) for structure-respecting
uniqueness; §§15.5–15.6 and 20.5 (pp. 201–204, 302–305) for split witnesses and
functorial transport; §§15.3–15.4 and 22.6 (pp. 194–200, 336–337) for cancellation
and determination; §21.5 (pp. 322–327) for full and faithful functors. Page numbers
are printed pages. The builder, adapter, observer, and failure-diagnosis guidance
above is an engineering application under the stated hypotheses.

*Algebraic World Model: From Exploration to Proofs*,
[sections 4.3–4.4 and appendix C.6](https://arxiv.org/html/2610.40503v1), motivates
premise-directed investigation and the distinction between model proofs and
implementation transfer. The trace conditions, direct certificate, and receipt
example above are engineering applications, not a mandatory reproduction of its
pipeline or evidence of Universalist efficacy.
