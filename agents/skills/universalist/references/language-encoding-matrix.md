# Language encoding matrix

| Construction | Haskell / ML / Rust-ish | TypeScript / Kotlin / Java | Go / Python / dynamic |
| --- | --- | --- | --- |
| Product | record/struct | object/class | dataclass/struct/map with constructor |
| Coproduct | ADT/enum payload | sealed class/tagged union | tag + constructor + exhaustive tests |
| Refined type | newtype/smart constructor | wrapper/value class | checked constructor + runtime validator |
| Pullback | dependent pair/witness | checked aggregate | constructor enforcing agreement |
| Exponential | function/closure | strategy/interface | callable object/function |
| Free construction | AST/GADT/free monad | AST/interface hierarchy | tagged IR + interpreter |
| Observation vocabulary | enum/GADT | tagged union/sealed class | enum/dataclass + dispatcher |
| Generation path | GADT/path type | tagged union | dataclass + lowering function |
| Explicit IR | ADT | tagged union/sealed class | tags + interpreter |

When the language cannot enforce a property statically, name the trusted constructor and add tests.
