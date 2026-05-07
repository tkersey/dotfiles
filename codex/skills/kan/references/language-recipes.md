# Language recipes

## TypeScript

TypeScript cannot express true rank-n polymorphism or higher-kinded types directly. Use interface-level approximations.

```ts
export type Ran<K, D, A> = {
  run<I>(observe: (a: A) => K): D;
};

export type Lan<KI, DI, A> = {
  project: (ki: KI) => A;
  payload: DI;
  tag?: string;
};
```

Architecture use: keep `Lan` constructors opaque; centralize normalization/quotienting; use property tests for compatibility; do not rely on structural typing alone for laws.

## Rust

Rust can encode existential packages through trait objects/enums and right-Kan-like callbacks through higher-ranked trait bounds in limited cases.

```rust
pub struct Lan<KI, DI, A> {
    pub project: Box<dyn Fn(KI) -> A>,
    pub payload: DI,
}

pub trait Ran<A> {
    type Out<I>;
    fn run<I, Observe>(&self, observe: Observe) -> Self::Out<I>
    where
        Observe: Fn(&A) -> I;
}
```

Use explicit witness structs and law tests; avoid over-abstracting with trait gymnastics if an adapter is enough.

## Python

Python works well for finite-category experiments and architecture sketches. Use dataclasses for objects/arrows, dictionaries for functor maps, union-find for finite `Lan` quotients, products/filtering for finite `Ran` coherent families, and Hypothesis or table-driven tests for laws.

Python is poor at enforcing parametricity. Treat rank-n/codensity encodings as conventions.

## Scala / OCaml

Use GADTs, modules/functors, existential wrappers, and typeclasses/implicit evidence where available. Start with a concrete witness module, add higher-kinded abstractions only when multiple implementations share laws, and keep law tests near the abstraction.

## Cross-language rule

The core implementation asset is not the name `Lan` or `Ran`; it is the compatibility bridge:

```text
η : old -> restrict(new)
ε : restrict(new) -> old
```

Encode that bridge directly and test it.
