# Language encoding matrix

Choose the strongest encoding the repository language can support without fighting the ecosystem.

| Need | Haskell/OCaml/F# | TypeScript | Python | Java/Kotlin | Go | Rust/Swift |
| --- | --- | --- | --- | --- | --- | --- |
| Product | record | interface/type | dataclass | record/data class | struct | struct |
| Coproduct | ADT | tagged union | tagged dataclass | sealed class | tagged struct/interface | enum with payload |
| Refined type | smart constructor/newtype | branded type + constructor | wrapper + validator | value class/factory | wrapper + constructor | newtype/struct |
| Pullback witness | dependent pair-ish record | checked pair object | checked dataclass | checked record | checked struct | struct with constructor |
| Exponential | function/closure | function/strategy | callable/protocol | interface/lambda | interface func | closure/trait |
| Free syntax | ADT + fold | AST union + interpreter | class/union + visitor | sealed AST + visitor | interface tags | enum AST |
| Observation vocabulary | ADT | enum/union + runner | enum/class + runner | sealed observation | tagged observation | enum + match |
| Defunctionalized IR | ADT + apply | union + switch | dataclass variants + match | sealed class + visitor | tagged union | enum + match |
| Free builder behind projection | algebra/constructor | factory/build plan | builder dataclass | builder/service | builder funcs | builder/trait |

Say what remains runtime-only in dynamic or weakly typed environments.
