# Law tests

| Construction | Minimal law |
|---|---|
| `Lan` | `lan_map(Kf, eta(c,x)) == eta(c', Ff(x))` |
| `Ran` | `Ff(epsilon(c,fam)) == epsilon(c', ran_map(Kf,fam))` |
| `Δ` | old view of new model equals old fixture |
| `Lft` | `F(a) -> P(L(a))` or `desired <= projected` |
| `Rft` | `P(R(a)) -> F(a)` or `projected <= desired` |
| Freyd/free builder | `P(Free(c)) ~= c` |
| Defunctionalization | `apply(case,args) == originalFunction(args)` |
| Yoneda | sanctioned observations are representation-independent |
| Coyoneda | deferred path lowering fuses with composition |

For architecture work, use golden fixtures, property tests, and centralization checks to approximate universal laws.
