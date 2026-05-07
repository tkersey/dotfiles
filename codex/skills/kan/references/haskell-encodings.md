# Haskell encodings

## Right Kan extension

```haskell
{-# LANGUAGE RankNTypes #-}
newtype Ran k d a = Ran { runRan :: forall i. (a -> k i) -> d i }
```

Reading: for every way to observe an `a` as a `k i`, produce a `d i` uniformly in `i`. Source: `[KAN-MILEWSKI-2017]`.

## Left Kan extension

```haskell
{-# LANGUAGE GADTs, ExistentialQuantification #-}
data Lan k d a where
  Lan :: (k i -> a) -> d i -> Lan k d a
```

Reading: hide an index `i`, carry a `d i`, and a way to project `k i` to `a`. Source: `[KAN-MILEWSKI-2017]`.

## Codensity

```haskell
newtype Codensity m a = Codensity
  { runCodensity :: forall b. (a -> m b) -> m b }

liftCodensity :: Monad m => m a -> Codensity m a
liftCodensity m = Codensity (m >>=)

lowerCodensity :: Monad m => Codensity m a -> m a
lowerCodensity c = runCodensity c pure
```

Use for performance only after checking semantic equivalence and measuring. Source: `[KAN-HINZE-2012]`.

## Density

A density-like encoding mirrors `Lan`:

```haskell
data Density f a where
  Density :: (f i -> a) -> f i -> Density f a
```

This often appears as a Church/existential package that delays mapping or normalization.

## Yoneda and Coyoneda adjacency

```haskell
newtype Yoneda f a = Yoneda { runYoneda :: forall b. (a -> b) -> f b }

data Coyoneda f a where
  Coyoneda :: (i -> a) -> f i -> Coyoneda f a
```

Use these as lighter tools when the problem is repeated `fmap`, functoriality recovery, or map fusion rather than a full extension along a nontrivial `K`. Source: `[KAN-HASKELL-KAN-EXTENSIONS]`.

## Typeclass-style laws

For `Codensity`:

```haskell
lowerCodensity (liftCodensity m) == m
lowerCodensity (fmap f c) == fmap f (lowerCodensity c)
lowerCodensity (c >>= k) == lowerCodensity c >>= (lowerCodensity . k)
```

These are observational equalities, not Haskell `Eq` laws for all monads.

## When Haskell encodings mislead

- `forall` gives parametricity only to the extent the language and extensions preserve it.
- `exists` packages hide indices but do not enforce categorical quotienting by themselves.
- Typeclass laws are not checked by the compiler.
- Effects, strictness, exceptions, and resource behavior can break naive equivalences.
