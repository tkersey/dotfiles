{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE ExistentialQuantification #-}

module RanLan where

-- Right Kan extension, Haskell/Set-shaped.
newtype Ran k d a = Ran { runRan :: forall i. (a -> k i) -> d i }

-- Left Kan extension, existential/coend-shaped.
data Lan k d a where
  Lan :: (k i -> a) -> d i -> Lan k d a

-- Codensity is Ran m m in the common Haskell encoding.
newtype Codensity m a = Codensity { runCodensity :: forall b. (a -> m b) -> m b }

liftCodensity :: Monad m => m a -> Codensity m a
liftCodensity m = Codensity (m >>=)

lowerCodensity :: Monad m => Codensity m a -> m a
lowerCodensity c = runCodensity c pure

instance Functor (Codensity m) where
  fmap f c = Codensity $ \k -> runCodensity c (k . f)

instance Applicative (Codensity m) where
  pure a = Codensity ($ a)
  mf <*> ma = Codensity $ \k -> runCodensity mf $ \f -> runCodensity ma (k . f)

instance Monad (Codensity m) where
  ma >>= f = Codensity $ \k -> runCodensity ma $ \a -> runCodensity (f a) k
