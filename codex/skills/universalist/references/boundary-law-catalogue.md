# Boundary Law Catalogue

These are practical proof signals, not formal proofs. Use one positive law and one falsifier for every Track D artifact.

| Boundary | Law shape | Falsifier |
| --- | --- | --- |
| Embedding | `new(embed(old)) == old(old)` | embedded old case changes behavior |
| Projection | `observe(project(internal)) == expectedPublicBehavior` | internal candidate cannot produce public observation |
| Forgetful | `forget(combineRich(a,b)) == combineRaw(forget(a),forget(b))` | forgetting after combination disagrees with combining forgotten values |
| Pullback agreement | `f(projectA(p)) == g(projectB(p))`; every compatible pair factors through the canonical witness | mismatched pair admitted, projections lost, or two distinct public mediators preserve the same views |
| Pushout gluing | `injectA(includeA(o)) == injectB(includeB(o))`; every compatible pair of consumers factors through the integrated artifact | false identification, silent conflict collapse, lost non-overlap data, or noncanonical duplicate integration paths |
| Double-pushout rewrite | preserved interface survives; delete/add squares commute; rewrite runs only when pushout complement exists | dangling edge, forbidden identification, deleted shared structure, or silently guessed complement |
| Interpreter | `interpret(translate(syntax)) == oldBehavior(syntax)` | translated syntax changes behavior |
| Serializer | `decode(encode(internal))` preserves public invariants | encoded form loses required evidence |
| Migration | `oldReport(old) == oldReport(restrict(migrate(old)))` | migrated data breaks old report |
| Handler | `run(handler(program))` satisfies operation observations | handler omits or misinterprets operation case |
| Freyd effect order | pure embedding preserves identity/composition; reordered effects agree observationally only when certified | accepted reordering changes state, trace, result, or failure |
| Operadic substitution | `interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))` | legal wiring changes meaning under hierarchical substitution or forbidden wiring is admitted |
| Day representable | `represent(a) star represent(b) ~= represent(a tensor b)` | two atomic descriptions compose differently from their indices |
| Day unit/associativity | `J star F ~= F ~= F star J`; `(F star G) star H ~= F star (G star H)` | normalization depends on grouping or the unit changes observations |
| Day decomposition | every emitted composite has a legal decomposition witness and every supported legal decomposition contributes | illegal decomposition admitted or legal decomposition omitted |
| Day quotient coherence | coherent reindexing of an intermediate representative leaves normalized observations unchanged | quotient collapses required provenance/order or equivalent presentations diverge |
| Day interpretation | `interpret(F star G) == combine(interpret(F),interpret(G))` under declared observations | description composition and semantic composition disagree |
| Promonoidal admissibility | partial/relation-valued composition contributes only through explicit `P(a,b;c)` witnesses | incompatible resources/interfaces are silently totalized |
| Convolution effectivity | decomposition, aggregation, quotient, and invalidation stay within the declared resource bound | decomposition explodes or equality/normalization is unavailable without obstruction |
| Behavioral coalgebra | `observe(step(state,input))` satisfies trace expectations | invalid transition admitted or equivalent states diverge observationally |
| Comonadic center | `extract(localView(x)) == x` | the supposed local view is not centered at the original value/point |
| Comonadic neighborhood coherence | `localViewOfLocalViews(x)` agrees with `expandLocalView(localView(x))` | nested contexts disagree, duplicate changes meaning, or nearby views are incoherent |
| Germ restriction | restricting to a smaller valid halo preserves local meaning at the center | a valid restriction changes the value, evidence, authority, or observation at the point |
| Basis density / reconstruction | every supported situated object decomposes into basic patches and reconstructs canonically under required observations | patch catalog covers examples but cannot reconstruct, or multiple non-normalized reconstructions disagree |
| Spatial continuity / halo preservation | point map plus context transport maps required source halos into target halos and preserves labels/restrictions | points survive but scope, dependency, owner, capability, provenance, trust, or temporal validity is lost |
| Local/global identity | local points map explicitly to global points and identifications retain provenance | distinct scoped/source-local points collapse silently into one coarse identity |
| Generation | `lowerGenerated(payload,path) == directInterpret(path,payload)` | invalid payload/path pair silently accepted |
| Observation | `runObservation(obs,repack(subject)) == runObservation(obs,subject)` | representation change leaks into public observation |
| Defunctionalization | `apply(encodedCase,x) == oldFunction(x)` | constructor payload omits captured behavior |
| Free builder | `project(free(required(case)))` satisfies required behavior | projection loses evidence required by behavior |
| Residual obligation | missing obligation fails; satisfying obligations passes | accepted implementation lacks required obligation |

For pullbacks and pushouts, do not stop at square commutativity. The distinctive universal obligation is factorization through the selected artifact, with uniqueness approximated by an opaque canonical constructor, quotient/normal form, and no competing public construction path.

For comonadic spatiality, do not stop at a type named `Context`, a dependency graph, or point preservation. Require center/coherence, effective halo or basis representation, restriction behavior, labelled locality, a continuity falsifier, and a resource law.

For Day convolution, do not stop at a nested loop or binary combination function. Require a real index tensor/kernel, representable preservation, unit/associativity, sound and complete decompositions, an explicit coend/normalization policy, interpretation law, effect-order guardrail, and effective implementation. Static/applicative structure never grants runtime commutativity by itself.
