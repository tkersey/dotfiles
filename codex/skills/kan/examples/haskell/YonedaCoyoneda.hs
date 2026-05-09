{-# LANGUAGE RankNTypes, ExistentialQuantification #-}
module YonedaCoyoneda where
newtype Yoneda f a = Yoneda { runYoneda :: forall b. (a -> b) -> f b }
data Coyoneda f a = forall b. Coyoneda (b -> a) (f b)
