# Codensity/free-monad witness

Use this pattern when a free monad or interpreter pipeline has poor associativity/allocation behavior.

```haskell
newtype Codensity m a = Codensity { runCodensity :: forall b. (a -> m b) -> m b }

liftCodensity :: Monad m => m a -> Codensity m a
liftCodensity m = Codensity (m >>=)

lowerCodensity :: Monad m => Codensity m a -> m a
lowerCodensity c = runCodensity c pure
```

Law-test sketch:

```haskell
lowerCodensity (liftCodensity program) == program
lowerCodensity optimizedProgram == directProgram
```

Benchmark only after semantic equality passes. Operational details such as error order, laziness, logging, and resource finalization matter.

Source IDs: `[KAN-HINZE-2012]`, `[KAN-MILEWSKI-2017]`.
