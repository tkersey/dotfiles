# Boundary Kind to Kan Mapping

| Boundary kind | Software shape | Categorical mechanics | First law |
| --- | --- | --- | --- |
| Embedding | old/core included in new/target | `Lan`, `Ran`, `Delta` | `new(embed(old)) == old(old)` |
| Projection | internals observed as public behavior | Kan lift, `P_*`, Freyd diagnostic | `observe(P(internal)) == required` |
| Forgetful map | rich structure erased to raw view | adjunction/free builder | `forget(free(raw))` satisfies raw behavior |
| Interpreter | syntax/effect/program -> behavior | algebra, fold, handler | interpreter agrees on fixtures |
| Compiler/lowering | source syntax/IR -> target IR/code | transported semantics, Coyoneda | lowering preserves semantics |
| Serializer/codec | internal model -> wire/storage | projection/restriction/lift obstruction | round-trip/invariant preservation |
| View/query | model -> report/client view | `Ran`, Yoneda | overlapping observations commute |
| Handler | effect syntax -> runtime behavior | free effects, handlers, defunctionalized ops | handler satisfies observations |
| Observer | subject -> observation result | Yoneda / `Ran` / `Rft` | representation change preserves observation |
| Migration | old schema -> new schema | `Delta`, `Lan`/Sigma, `Ran`/Pi | old reports pass through migration |
