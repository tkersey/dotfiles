# Structures and Laws Catalog

## Table of contents
- Products and coproducts
- Semigroup and monoid
- Groups
- Lattices and posets
- Semirings
- Functor / Applicative / Monad
- Homomorphisms
- Normal forms

## Products and coproducts
**Product (record/struct)**
- Shape: A x B
- Laws: projection consistency (fst (a,b) = a, snd (a,b) = b)
- Use: independent fields, cross-product of constraints

**Coproduct (sum/tagged union)**
- Shape: A + B
- Laws: exhaustiveness and disjointness (each value is exactly one variant)
- Use: alternatives, state machines, error typing

## Semigroup and monoid
**Semigroup**
- op(a,b) associative: op(a, op(b,c)) == op(op(a,b), c)
- Use: combine logs, configs, validations

**Monoid**
- Semigroup + identity element `empty`
- Laws:
  - assoc: a <> (b <> c) == (a <> b) <> c
  - identity: empty <> a == a; a <> empty == a
- Use: aggregation, folding, accumulation

## Groups
**Group**
- Monoid + inverse
- Laws: a <> inv(a) == empty
- Use: undo/redo, reversible ops

## Lattices and posets
**Join-semilattice**
- op is associative, commutative, idempotent
- Laws:
  - assoc: a v (b v c) == (a v b) v c
  - comm: a v b == b v a
  - idem: a v a == a
- Use: permissions, feature flags, conflict resolution

**Meet-semilattice**
- Dual of join with ^
- Same laws as above

## Semirings
Two operations: add and multiply
- Add: associative, commutative, identity (zero)
- Multiply: associative, identity (one)
- Distributivity: a*(b+c) == a*b + a*c
- Zero annihilates: a*0 == 0 == 0*a
- Use: costs, path weights, policy composition

## Functor / Applicative / Monad
**Functor**
- map id == id
- map (f . g) == map f . map g

**Applicative**
- identity, homomorphism, interchange, composition (see law list per library)

**Monad**
- left identity: return a >>= f == f a
- right identity: m >>= return == m
- associativity: (m >>= f) >>= g == m >>= (\x -> f x >>= g)

## Homomorphisms
A function `h` between algebras that preserves operations:
- h(op(a,b)) == op'(h(a), h(b))
Use as a refactor criterion and test property.

## Normal forms
Define a canonical representation and a `normalize` function.
- Law: normalize(normalize(x)) == normalize(x)
- Law: normalize(x) == x for already-canonical inputs

