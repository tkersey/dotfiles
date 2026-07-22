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
| Double-category arrow laws | horizontal and vertical identities/associativity hold under declared equality or normalization | either arrow family changes observations when regrouped or composed with identity |
| Double-category square boundary | every square has four matching typed boundaries and one owner-controlled constructor | a square with mismatched corners or edges is constructible |
| Double-category pasting | horizontal and vertical pasting preserve external boundaries and required internal provenance | a compatible local square cannot paste or pasting loses an observable witness |
| Double-category interchange | `normalize((a pasteH b) pasteV (c pasteH d)) == normalize((a pasteV c) pasteH (b pasteV d))` | pasting order changes effect trace, authority, failure, provenance, schema meaning, or resource cost |
| Double-functor interpretation | interpretation preserves both arrow compositions, squares, both pastings, and coherence | lowering a pasted square disagrees with pasting the lowered squares |
| Equipment base change | companions/conjoints/restrictions induced by strict maps satisfy unit/counit or triangle laws | a strict map claims generalized base change but no lawful companion, conjoint, or restriction exists |
| Day representable | `represent(a) star represent(b) ~= represent(a tensor b)` | two atomic descriptions compose differently from their indices |
| Day unit/associativity | `J star F ~= F ~= F star J`; `(F star G) star H ~= F star (G star H)` | normalization depends on grouping or the unit changes observations |
| Day decomposition | every emitted composite has a legal decomposition witness and every supported legal decomposition contributes | illegal decomposition admitted or legal decomposition omitted |
| Day quotient coherence | coherent reindexing of an intermediate representative leaves normalized observations unchanged | quotient collapses required provenance/order or equivalent presentations diverge |
| Day interpretation | `interpret(F star G) == combine(interpret(F),interpret(G))` under declared observations | description composition and semantic composition disagree |
| Promonoidal admissibility | partial/relation-valued composition contributes only through explicit `P(a,b;c)` witnesses | incompatible resources/interfaces are silently totalized |
| Convolution effectivity | decomposition, aggregation, quotient, and invalidation stay within the declared resource bound | decomposition explodes or equality/normalization is unavailable without obstruction |
| Tambara unit | `frame_I(p) ~= p` | the identity/empty context changes the capability |
| Tambara associativity | `frame_(m tensor n)(p) ~= frame_m(frame_n(p))` | nested context extension depends on grouping or wrapper order |
| Tambara endpoint naturality | `dimap(f,g,frame_m(p)) ~= frame_m(dimap(f,g,p))` | preprocessing/postprocessing and framing disagree |
| Tambara context coherence | coherent reindexing of a context leaves framed observations unchanged | equivalent residual/context presentations produce different behavior |
| Tambara interpretation | `interpret(frame_m(p)) == frameSemantics(m,interpret(p))` | framed syntax/capability and runtime semantics disagree |
| Mixed Tambara action | source action `L` and target action `R` frame one profunctor coherently | one endpoint is framed by an incompatible or implicit action |
| Optic residual | `interpretOptic(m,decompose,rebuild,p) == dimap(decompose,rebuild,frame_m(p))` | hidden residual identity leaks or reconstruction loses required context |
| Free Tambara closure | every supported legal frame of a generator is represented once modulo coherent reindexing | frame omitted, duplicated observably, or quotient collapses required provenance |
| Cofree Tambara observation | all supported frames are exposed coherently with unit/coassociativity | all-context claim omits a frame or nested observations disagree |
| Tambara representability | generalized module round-trips through a concrete context-preserving realizer | claimed implementation map exists only as a nonfunctional relation/specification |
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

For pullbacks and pushouts, do not stop at square commutativity. Require factorization through the selected artifact and an engineering approximation of uniqueness.

For double categories, do not stop at a collection of commutative squares. Require two independently meaningful arrow families, identities and composition in both directions, typed square boundaries, horizontal and vertical square pasting, interchange or coherent comparison, one double-functor interpretation, effective normalization/invalidation, and a falsifier. Interchange never grants effect commutativity by itself.

For comonadic spatiality, require center/coherence, effective halo or basis representation, restriction behavior, labelled locality, continuity, and a resource law.

For Day convolution, require a real index tensor/kernel, representable preservation, unit/associativity, sound and complete decompositions, quotient policy, interpretation law, effect-order guardrail, and effective implementation.

For Tambara modules, require a real context action on both endpoint worlds, a profunctor, unit/associativity/naturality/coherence, interpretation, effective residual/context representation, representability status, and a falsifier. Framing never grants effect commutativity or domain optic lawfulness.
