"""
Finite-poset witness for left and right Kan-lift-shaped architecture design.

This is an engineering approximation, not a general Kan-lift engine.
It models:

  A = discrete feature/spec set
  B = implementation choices ordered by capability
  C = observable guarantees ordered by strength
  P : B -> C = public projection of implementation capability
  F : A -> C = desired observable guarantee

Left lift: least implementation whose projection covers F(a).
Right lift: greatest implementation whose projection stays within F(a).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class Impl:
    name: str
    level: int


IMPLEMENTATIONS: List[Impl] = [
    Impl("stub", 0),
    Impl("cached-read-model", 1),
    Impl("transactional-db", 2),
    Impl("replicated-audit-db", 3),
]

# P : B -> C. In this simple example, B and C share a capability ordering.
def project(impl: Impl) -> int:
    return impl.level


# F : A -> C. A is discrete here: one desired guarantee per feature.
DESIRED: Dict[str, int] = {
    "list_orders": 1,
    "capture_payment": 2,
    "audit_dispute": 3,
}


def left_lift(desired_level: int, candidates: Iterable[Impl] = IMPLEMENTATIONS) -> Impl:
    """Least implementation whose projection covers the desired observable level."""
    covering = [impl for impl in candidates if desired_level <= project(impl)]
    if not covering:
        raise ValueError(f"no implementation covers desired level {desired_level}")
    return min(covering, key=project)


def right_lift(desired_level: int, candidates: Iterable[Impl] = IMPLEMENTATIONS) -> Impl:
    """Greatest implementation whose projection remains sound under desired level."""
    sound = [impl for impl in candidates if project(impl) <= desired_level]
    if not sound:
        raise ValueError(f"no implementation is sound for desired level {desired_level}")
    return max(sound, key=project)


def assert_left_lift_laws() -> None:
    for feature, desired in DESIRED.items():
        impl = left_lift(desired)
        assert desired <= project(impl), (feature, impl)
        smaller = [candidate for candidate in IMPLEMENTATIONS if project(candidate) < project(impl)]
        assert all(not (desired <= project(candidate)) for candidate in smaller), (feature, impl, smaller)


def assert_right_lift_laws() -> None:
    for feature, desired in DESIRED.items():
        impl = right_lift(desired)
        assert project(impl) <= desired, (feature, impl)
        larger = [candidate for candidate in IMPLEMENTATIONS if project(candidate) > project(impl)]
        assert all(not (project(candidate) <= desired) for candidate in larger), (feature, impl, larger)


def main() -> None:
    assert_left_lift_laws()
    assert_right_lift_laws()
    print("feature,left_lift,right_lift")
    for feature, desired in DESIRED.items():
        print(f"{feature},{left_lift(desired).name},{right_lift(desired).name}")


if __name__ == "__main__":
    main()
