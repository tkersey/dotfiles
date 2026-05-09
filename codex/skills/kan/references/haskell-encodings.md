# Haskell encodings

```haskell
newtype Ran k d a = Ran { runRan :: forall i. (a -> k i) -> d i }
data Lan k d a = forall i. Lan (k i -> a) (d i)
newtype Codensity m a = Codensity { runCodensity :: forall b. (a -> m b) -> m b }
newtype Yoneda f a = Yoneda { runYoneda :: forall b. (a -> b) -> f b }
data Coyoneda f a = forall b. Coyoneda (b -> a) (f b)
```

Treat these as programming representations of end/coend/right-Kan/left-Kan shapes. Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`, `[KAN-HASKELL-YONEDA]`, `[KAN-HASKELL-COYONEDA]`.
