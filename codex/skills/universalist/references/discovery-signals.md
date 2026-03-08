# Discovery Signals

## Table of contents
- How to use this file
- Core signals
- Advanced signals
- Overreach checks

## How to use this file
Start from the code smell or API pressure, not the theory label. Match the observed signal to the smallest construction that explains it, then translate that construction into the repo's language and framework conventions.

## Core signals
| Signal in the repo | Candidate construction | What to verify | Typical encoding | Validation cue |
| --- | --- | --- | --- | --- |
| Several fields are always carried together and consumed independently | Product plus terminal object | Are the fields truly independent, or do some combinations need validation? | Record, struct, tuple, or object; empty struct or unit for no payload | Constructor and projection consistency |
| Status strings, booleans, or nullable fields try to describe one lifecycle | Coproduct plus initial object | Is each value exactly one case? Are impossible combinations leaking through? | Tagged union, sealed interface, enum with payload, interface plus tag | Exhaustive handling and impossible-state tests |
| The same predicate is checked at many boundaries | Equalizer or refined type | What is the precise subset of legal values? Can one constructor enforce it once? | Smart constructor, value object, parser, normalized wrapper | Accept valid, reject invalid, normalization idempotence |
| Two records must agree on tenant id, account id, locale, or schema version | Pullback-shaped join | Which projections must agree? Can a checked constructor enforce the witness? | Checked composite struct, witness object, validated pair | Both projections preserved, mismatches rejected |
| Behavior is hard-coded behind branches but should be supplied by callers | Exponential | Is the real design a function or strategy from input to output? | Closure, function value, callable object, strategy interface | Application and composition examples |
| A builder, workflow, or rule engine mixes syntax with execution | Free construction or initial algebra | Can syntax be modeled separately from interpreters? Are there multiple interpretations? | AST, IR, command object tree, fold or interpreter | Interpreter consistency, fold law, differential tests |
| Combination rules dominate once the outer shape is chosen | ADD sub-lens | Is there an associative combine, identity, lattice, semiring, or normalization? | Monoid, lattice, semiring, homomorphism, normal form | Law checks or small model tests |

## Advanced signals
| Signal in the repo | Candidate construction | Default stance |
| --- | --- | --- |
| Merge two modules or schemas around a shared interface and quotient overlaps | Pushout or coequalizer | Keep in the advanced tier unless the code already talks about merge semantics formally |
| A free builder always pairs with an evaluator or forgetful projection | Adjunction | Use as explanation, not as the first code recommendation |
| Polymorphic representation theorems or optics/profunctor APIs dominate | Yoneda, ends, coends | Use only when the prompt explicitly wants that level |
| Data migration across schemas or functor-shaped indexing appears directly | Kan extension | Use only when schema or semantics transport is the real problem |
| Coeffects, handlers, or explicit effect semantics are already first-class | Monads or comonads as categorical abstractions | Follow repo conventions before introducing categorical vocabulary |

## Overreach checks
- Do not choose a larger construction just because it sounds elegant.
- Do not claim a pullback when the code only needs a pair and a runtime assertion with no stable shared projection.
- Do not claim a free construction unless separate interpreters or folds are part of the value.
- Do not claim an equalizer if the predicate is fuzzy, unstable, or context-dependent.
- When two constructions compete, choose the smaller one and mention the larger one as an alternative only if it unlocks a concrete follow-up benefit.
