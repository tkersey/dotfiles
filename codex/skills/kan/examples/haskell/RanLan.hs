{-# LANGUAGE RankNTypes, ExistentialQuantification #-}
module RanLan where
newtype Ran k d a = Ran { runRan :: forall i. (a -> k i) -> d i }
data Lan k d a = forall i. Lan (k i -> a) (d i)
