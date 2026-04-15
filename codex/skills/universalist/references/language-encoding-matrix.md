# Language Encoding Matrix

## Capability-first fallback ladder

Choose the strongest honest encoding the language and repo can support.

1. Native algebraic data types, exhaustive matching, value objects, and generics
2. Sealed hierarchies, enums with payloads, records, and closed interfaces
3. Interfaces plus explicit tags, checked constructors, witness structs, and strategy objects
4. Runtime validators, wrappers, and disciplined tests in dynamic languages

Do not pretend a runtime validator gives compile-time guarantees.

## Family matrix

| Language family | Product | Coproduct | Equalizer / refined type | Pullback | Exponential | Free construction |
| --- | --- | --- | --- | --- | --- | --- |
| ADT-rich languages (Haskell, OCaml, F#, Rust, Swift, Scala) | record, struct, tuple | enum / ADT | newtype + smart constructor | checked witness struct | function / closure | enum AST + interpreter / fold |
| Modern OO with sealed types (Kotlin, Java, C#) | record, data class, value object | sealed hierarchy, enum with payload, visitor | private constructor + factory / value object | checked aggregate / witness class | lambda, strategy interface, callable object | class or enum AST + interpreter |
| Go-style structural typing | struct, multiple return values, `struct{}` | interface + tag or discriminator | constructor returning `(T, error)` | checked struct with unexported fields | `func` value or interface | tagged structs + evaluator |
| Dynamic languages (Python, Ruby, JavaScript) | dataclass / object / dict helper | tagged dict or class union by convention | validator + wrapper + one constructor path | validated pair object | closure, callable object | tagged AST objects + interpreter |

## Construction notes

### Product
Prefer named fields over positional tuples when domain meaning matters.

### Coproduct
Prefer one discriminant or one sealed hierarchy over several booleans.

### Refined type
Centralize construction so invalid values cannot leak in casually. If the repo is dynamic, keep the validator and wrapper next to each other.

### Pullback
Preserve both projections explicitly and keep the agreement check in one constructor.

### Exponential
Use closures when the repo already passes functions. Use strategy objects when the repo favors interfaces, dependency injection, or object seams.

### Free construction
Keep constructors dumb and interpreters explicit. Do not hide execution in the syntax tree unless the repo already does that.

## Boundary prompts by ecosystem

### TypeScript / JavaScript
Ask:
- where JSON becomes domain data
- whether a runtime decoder already exists
- whether the internal union can stay richer than the wire shape
- whether one discriminant field can be introduced internally before any API change

### Python
Ask:
- where parsing happens today
- whether a small frozen wrapper can replace repeated raw-string use
- whether serializers can unwrap explicitly at the edge
- what remains runtime-only after introducing the wrapper

### Java / Kotlin
Ask:
- whether DTOs can stay at the controller boundary
- whether value objects can avoid bleeding into persistence immediately
- whether a factory or static constructor can centralize refinement
- whether a sealed hierarchy can stay internal while Jackson or persistence models remain stable

### Go
Ask:
- whether fields can be unexported so the constructor is the only way in
- whether JSON or DB mapping should stay in a separate package
- whether the witness should expose preserved projections instead of public fields
- whether the error path is obvious and testable

### Rust / Swift
Ask:
- whether newtypes can hold the invariant cheaply
- whether `serde` / `Codable` adapters should stay at the edge
- whether enum exhaustiveness can replace stringly-typed branching directly

## Validation defaults

- Prefer the repo's built-in test runner and assertion style.
- Prefer compile, typecheck, and deterministic fixtures before introducing property testing.
- In dynamic languages, lean harder on boundary tests, round-trips, and differential tests.
- In OO or Go-style code, make constructors and eliminators easy to test directly.
