# Domain Algebra Discovery

Use at an already-live semantic decision when the operation vocabulary,
interacting equations, or observation carrier needs derivation. Reuse the
existing nomination or recognition fields; this is not another pass, report,
activation trigger, or prerequisite for an already-dispositive ordinary design.

The techniques below adapt Sandy Maguire's *Algebra-Driven Design*, especially
"What Makes a Good Algebra?", "Tiles", "Scavenger Hunt", and "Deriving
Implementations". The authority, effect, migration, and proof qualifications are
Universalist's engineering application, not additional claims made by the book.

## Grow the algebra from required uses

```text
required uses -> useful operations -> interacting equations and observations
             -> revised vocabulary or carrier -> native realization
```

Start with the human-facing purpose and representative required uses, including
an awkward composition or boundary case when one is relevant. Do not begin by
assuming the incumbent container or a preferred categorical construction. For a
first-use boundary, use attributed requirements rather than invented historical
implementations. Examples expose missing behavior; they do not define the whole
admitted domain.

Propose the smallest useful constructors, combinators, and eliminators. Relate
each proposed operation to existing operations and required observations. An
identity, distributive law, or factoring may reveal missing functionality or
remove a special case. Awkward interactions can instead expose a conflated
operation, accidental constraint, or false law. Investigate the interactions
that decide this seam, not an exhaustive operation-pair matrix.

Keep the vocabulary compositional, task-relevant, parsimonious, and orthogonal.
Generalize only where the equations and a material dividend support it. A
convenient derived operation can stay when its relation to the smaller basis is
clear and it reduces caller knowledge; parsimony does not require forcing callers
to reconstruct every useful operation. Compare complete caller contracts and
source-supported changes under the existing law-preserving dominance rule.

Attribute equations to accepted requirements, justified derivations, or candidate
regularities. Names, existing code, and generated laws do not grant requirement
authority. Resolve a contradiction against that authority: either the proposed
law, the observation, or the representation may be wrong. Do not weaken an
accepted obligation merely to obtain a familiar algebra.

## Let contradictions select the carrier

In the book's scavenger hunt, `both(a,b)` should combine rewards commutatively.
Returning a list exposes order that the intended reward observation does not
need. Replacing the list with a set removes order but also erases multiplicity:
two distinct awards of one point must still count twice.

For this observation, derive a bag (multiset) with additive counts:

```text
count(r, combine(a,b)) = count(r,a) + count(r,b)
combine(a,b) ~= combine(b,a)
combine(a,empty) ~= a
combine(combine(a,b),c) ~= combine(a,combine(b,c))
combine(singleton(r),singleton(r)) !~= singleton(r)
```

Here `~=` compares every reward count. Associativity, identity, and commutativity
follow pointwise from count addition; idempotence is a non-law. A native count map
or an equivalent representation can realize this without a public algebra
framework. A list behind an adequate observation boundary is not automatically
wrong; choose by the actual preserved observations and consumer obligations.

Ask both questions: **which distinctions does the representation introduce that
the domain does not require, and which would the simplification erase that the
domain does require?** Preserve the answer through public construction, permitted
operations, and future observations, not only current examples. An ordered audit
trace cannot be quotiented to a bag. Bounds, overflow, identity, provenance, and
failure behavior retain their actual contracts. Commutative reward accounting
neither permits reordering external effects nor proves effect-safe retries.

## Derive a unifying observation

When observations independently traverse or simulate the same structure, ask
whether a smaller observation with sufficient residual state can derive them.
The book replaces separately maintained reward and completion traversals with:

```text
step : Maybe Input -> Challenge -> (Multiset Reward, Challenge)
```

The result contains emitted rewards and the residual challenge. `Nothing` allows
immediate progress without another external event: after a gate consumes its
matching input, its reward can be emitted now, but the same input must not also
satisfy a second sequential gate. Derive reward accumulation and completion from
this semantics rather than coordinating two implementations of event dispatch.

For a pure, deterministic transition core, a native
`transition(state,event) -> (outputs,nextState)` is an analogous candidate, not
a mandated architecture. Show how each required observation is recovered and
how related residual states remain related under permitted continuations.
Today's equal status is insufficient when the next event distinguishes states.
Effectful, nondeterministic, partial, or resource-sensitive behavior needs its
actual observation and simulation argument; do not silently replace it with the
pure model. Output descriptions are not permission to execute effects.

Unify production meaning, not independent verification. Preserve an independent
oracle when it supplies distinct proof; do not consolidate it onto the very
transition being checked. Keep an adequate existing owner instead of adding a
second transition abstraction.

## Use a simple model to free the implementation

When useful for a consequential replacement, a compact initial encoding can
represent the algebra's operations as data and interpret them through the
accepted observations. It can be a reference model, not the required production
representation. Establish its connection to the accepted semantics before using
it to judge a successor; an incumbent implementation is not automatically an
oracle.

For a translation `T` between representations, the comparison is:

```text
Obs(optimized(T(program), inputs)) = Obs(reference(program, inputs))
```

Include required traces, failures, and residual behavior in `Obs`. A
structure-preserving or simulation argument may discharge more than samples;
keep its hypotheses and evidence strength explicit. The model is optional:
retain a sufficient initial implementation, direct proof, or existing oracle.
Do not require a second implementation, an IR, or an interpreter framework.
Performance claims need the actual host workload, not semantic agreement alone.

For law-adequacy countermodels, generator/observer coverage, and discovered-law
admission, use [property-test derivation](property-test-derivation.md) only when
that proof is live. Reuse the existing discriminator and required-valid control.

## Return to the existing decision

Algebra discovery supplies carriers, operations, observations, laws, non-laws,
interpreters, and falsifiers to the current nomination. It does not select a
route by itself. Keep `UNI-ORDINARY` available for a count map, local fold, or
transition function; preserve an adequate incumbent under live change pressure.
Use `UNI-CONSEQUENTIAL` only for materially different live candidates, and the
existing typed-hole/card gate only when ordinary comparison leaves a real hole.
Unknown evidence is not `UNI-OBSTRUCT`.

A lawful structure requires its laws and interpretation. A claimed universal
construction additionally requires the relevant diagram, admissible maps and
competitors, factorization, and uniqueness argument. One interpreter, opacity,
or finite tests do not establish those claims. Inside Actuating, return only the
decision-changing derivation: Universalist nominates; Actuating selects.

The tile algebra's closure does not promise infallible external operations.
Admitted compositions need defined semantics, including required failures,
authority checks, partial effects, progress, and resource limits. None may be
removed merely to make the equations simpler.
