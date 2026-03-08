# Language Encoding Matrix

## Table of contents
- Capability-first fallback ladder
- Family matrix
- Construction notes
- Validation defaults

## Capability-first fallback ladder
Choose the strongest honest encoding the language and repo can support.
1. Native algebraic data types, exhaustive matching, value objects, and generics.
2. Sealed hierarchies, enums with payloads, records, and closed interfaces.
3. Interfaces plus explicit tags, checked constructors, and witness structs.
4. Runtime validators, wrappers, and disciplined tests in dynamic languages.

Do not pretend a runtime validator gives compile-time guarantees. Say what remains runtime-only.

## Family matrix
| Language family | Product | Coproduct | Equalizer or refined type | Pullback | Exponential | Free construction |
| --- | --- | --- | --- | --- | --- | --- |
| Typed FP and ADT-rich languages (Haskell, OCaml, F#, Elm, Rust, Swift, Scala) | Record, tuple, unit | ADT, `Void` or `Never` style empty type | Newtype plus smart constructor | Checked witness record | Function, closure, curry, reader-like environment | AST plus fold or interpreter |
| Modern OO with sealed types (Kotlin, Java, C#, Swift) | Record, data class, value object | Sealed hierarchy, enum with payload, visitor | Factory, constructor guard, value object | Checked aggregate or witness class | Strategy, callable object, lambda | Class hierarchy or AST plus interpreter |
| Go-style structural typing | Struct, multiple return values, `struct{}` | Interface plus tag or enum-like discriminator | Constructor returning `(T, error)` | Checked struct with constructor and preserved projections | `func` value or interface method | Tagged structs plus evaluator |
| Dynamic languages (Python, Ruby, JavaScript) | Dataclass, object, dict with constructor helper | Tagged dict or object, class union by convention | Validator plus wrapper or constructor function | Validated pair object or helper constructor | Closure, callable object, higher-order function | Tagged AST objects plus interpreter |

## Construction notes
- **Product**: prefer named fields over positional tuples when the domain meaning matters.
- **Coproduct**: prefer a single discriminant field or sealed hierarchy over multiple booleans.
- **Equalizer or refined type**: centralize construction so invalid values cannot leak in casually.
- **Python note**: prefer `@dataclass(frozen=True)` value objects or small wrappers with one `parse` or constructor path; `typing.NewType` helps static tooling but does not enforce runtime validity.
- **Pullback**: preserve the two projections explicitly and keep the agreement check in one constructor.
- **Exponential**: choose closures for lightweight customization, strategy objects when the repo favors interfaces, and configuration plus callable objects when dependency injection is already established.
- **Free construction**: keep constructors dumb and interpreters explicit; do not hide execution inside the AST itself unless the repo already does that.

## Validation defaults
- Prefer the repo's built-in test runner and fixture style.
- Use property-based testing only when the repo already has support or the user approves it.
- In dynamic languages, lean harder on golden, round-trip, and differential tests because some guarantees stay runtime-only.
- In Python, annotate APIs with the refined wrapper and let mypy or pyright reinforce the boundary, but keep runtime validation in the constructor.
- In OO or Go-style code, make constructors and eliminators easy to test directly; do not rely on incidental framework behavior to prove the design.
