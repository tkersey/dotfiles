# Codensity and free syntax

`Codensity m a = forall b. (a -> m b) -> m b` is the continuation/right-Kan-shaped encoding used for CPS-style optimization. Free syntax should be interpreted with law tests before performance claims.
