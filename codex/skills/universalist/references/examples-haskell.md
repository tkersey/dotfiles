# Haskell Examples

## Product and terminal object

```haskell
data Money = Money
  { amount :: Int
  , currency :: String
  }

type NoPayload = ()
```

## Coproduct and initial object

```haskell
data DocState
  = Draft
  | InReview [String]
  | Published String

renderState :: DocState -> String
renderState Draft = "draft"
renderState (InReview reviewers) = "review:" ++ show reviewers
renderState (Published url) = url
```

## Refined type

```haskell
newtype NonEmpty = NonEmpty String deriving (Eq, Show)

mkNonEmpty :: String -> Maybe NonEmpty
mkNonEmpty s
  | null s = Nothing
  | otherwise = Just (NonEmpty s)
```

## Pullback witness

```haskell
newtype AccountId = AccountId String deriving (Eq, Show)

data Customer = Customer
  { customerAccountId :: AccountId
  , customerName :: String
  }

data Subscription = Subscription
  { subscriptionAccountId :: AccountId
  , planName :: String
  }

data CustomerSubscription = CustomerSubscription
  { joinedCustomer :: Customer
  , joinedSubscription :: Subscription
  }

mkCustomerSubscription :: Customer -> Subscription -> Maybe CustomerSubscription
mkCustomerSubscription customer subscription
  | customerAccountId customer == subscriptionAccountId subscription =
      Just (CustomerSubscription customer subscription)
  | otherwise = Nothing
```

## Exponential

```haskell
type Formatter = String -> String

withPrefix :: String -> Formatter
withPrefix prefix = \body -> prefix ++ body
```

## Free construction

```haskell
data Expr
  = Lit Int
  | Add Expr Expr

eval :: Expr -> Int
eval (Lit n) = n
eval (Add a b) = eval a + eval b

pretty :: Expr -> String
pretty (Lit n) = show n
pretty (Add a b) = "(" ++ pretty a ++ " + " ++ pretty b ++ ")"
```

## ADD sub-lens

```haskell
newtype Log = Log [String] deriving (Eq, Show)

instance Semigroup Log where
  Log a <> Log b = Log (a ++ b)

instance Monoid Log where
  mempty = Log []

totalLog :: [Log] -> Log
totalLog = foldMap id
```
