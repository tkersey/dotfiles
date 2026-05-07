{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE GADTs #-}

module YonedaCoyoneda where

newtype Yoneda f a = Yoneda { runYoneda :: forall b. (a -> b) -> f b }

toYoneda :: Functor f => f a -> Yoneda f a
toYoneda fa = Yoneda (`fmap` fa)

fromYoneda :: Yoneda f a -> f a
fromYoneda y = runYoneda y id

data Coyoneda f a where
  Coyoneda :: (i -> a) -> f i -> Coyoneda f a

instance Functor (Coyoneda f) where
  fmap g (Coyoneda h fi) = Coyoneda (g . h) fi
