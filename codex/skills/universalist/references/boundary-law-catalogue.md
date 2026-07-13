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
| Coalgebra | `observe(step(state,input))` satisfies trace expectations | invalid transition admitted or equivalent states diverge observationally |
| Generation | `lowerGenerated(payload,path) == directInterpret(path,payload)` | invalid payload/path pair silently accepted |
| Observation | `runObservation(obs,repack(subject)) == runObservation(obs,subject)` | representation change leaks into public observation |
| Defunctionalization | `apply(encodedCase,x) == oldFunction(x)` | constructor payload omits captured behavior |
| Free builder | `project(free(required(case)))` satisfies required behavior | projection loses evidence required by behavior |
| Residual obligation | missing obligation fails; satisfying obligations passes | accepted implementation lacks required obligation |

For pullbacks and pushouts, do not stop at square commutativity. The distinctive universal obligation is factorization through the selected artifact, with uniqueness approximated by an opaque canonical constructor, quotient/normal form, and no competing public construction path.
