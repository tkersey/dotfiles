# Haskell Examples (ADD)

## Table of contents
- Sum and product types
- Smart constructors
- Semigroup/Monoid
- Validation algebra
- Lattice for permissions
- Semiring for scoring
- Functor laws (sketch)
- FoldMap accumulation
- State machine transitions
- Error algebra (Either)
- Normal forms
- Homomorphism

## Sum and product types
```haskell
-- Coproduct: alternatives
data PaymentStatus = Pending | Settled | Failed FailureReason

-- Product: independent fields
data Money = Money { amount :: Int, currency :: Currency }
```

## Smart constructors
```haskell
newtype NonEmpty = NonEmpty String

mkNonEmpty :: String -> Maybe NonEmpty
mkNonEmpty s = if null s then Nothing else Just (NonEmpty s)
```

## Semigroup/Monoid
```haskell
newtype Log = Log [String]

instance Semigroup Log where
  Log a <> Log b = Log (a ++ b)

instance Monoid Log where
  mempty = Log []
```

## Validation algebra
```haskell
data Validation e a = Failure e | Success a

instance Semigroup e => Semigroup (Validation e a) where
  Failure e1 <> Failure e2 = Failure (e1 <> e2)
  Failure e  <> _          = Failure e
  _          <> Failure e  = Failure e
  Success a  <> _          = Success a
```

## Lattice for permissions
```haskell
import qualified Data.Set as Set

newtype Perm = Perm (Set.Set String)

joinPerm :: Perm -> Perm -> Perm
joinPerm (Perm a) (Perm b) = Perm (Set.union a b)

meetPerm :: Perm -> Perm -> Perm
meetPerm (Perm a) (Perm b) = Perm (Set.intersection a b)
```

## Semiring for scoring
```haskell
newtype Score = Score Int

addScore :: Score -> Score -> Score
addScore (Score a) (Score b) = Score (a + b)

mulScore :: Score -> Score -> Score
mulScore (Score a) (Score b) = Score (a * b)
```

## Functor laws (sketch)
```haskell
-- For any Functor f:
-- fmap id == id
-- fmap (g . h) == fmap g . fmap h
```

## FoldMap accumulation
```haskell
-- foldMap uses a Monoid to aggregate
totalLog :: [Log] -> Log
totalLog = foldMap id
```

## State machine transitions
```haskell
data State = Draft | Review | Approved | Published

step :: State -> State
step Draft = Review
step Review = Approved
step Approved = Published
step Published = Published
```

## Error algebra (Either)
```haskell
type Result a = Either Error a

-- Sum type: Either Error a
```

## Normal forms
```haskell
data Expr = Add Expr Expr | Lit Int

normalize :: Expr -> Expr
normalize (Add (Lit 0) x) = normalize x
normalize (Add x (Lit 0)) = normalize x
normalize (Add a b) = Add (normalize a) (normalize b)
normalize (Lit n) = Lit n
```

## Homomorphism
```haskell
-- length is a homomorphism from list concatenation to integer addition
-- length (a ++ b) == length a + length b
```
