#!/usr/bin/env python3
"""Defunctionalized Kan-lift witness.

This is intentionally small and finite. It models a lift-shaped architecture:

    A --?--> B
    |        |
    F        P
    v        v
    C

A = public requirement cases
B = implementation plans, represented first-order
C = observable behavior level, ordered by capability
P = project an implementation plan to its observable behavior
F = desired observable behavior

Left-lift approximation: choose the least plan whose projection covers desired.
Right-lift approximation: choose the greatest plan whose projection stays within desired.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Behavior(Enum):
    NONE = 0
    READ = 1
    WRITE = 2
    AUDITED_WRITE = 3

    def covers(self, other: "Behavior") -> bool:
        return self.value >= other.value


@dataclass(frozen=True)
class PublicCase:
    tag: str
    desired: Behavior


class PlanTag(Enum):
    NOOP = "noop"
    CACHE_READ = "cache-read"
    TX_WRITE = "transactional-write"
    AUDITED_TX_WRITE = "audited-transactional-write"


@dataclass(frozen=True)
class ImplementationPlan:
    """Defunctionalized realizer behind P.

    This replaces anonymous builders like `case -> InternalService` with explicit cases.
    """

    tag: PlanTag
    resource: str = "default"


PLANS: tuple[ImplementationPlan, ...] = (
    ImplementationPlan(PlanTag.NOOP),
    ImplementationPlan(PlanTag.CACHE_READ, "read-model"),
    ImplementationPlan(PlanTag.TX_WRITE, "orders"),
    ImplementationPlan(PlanTag.AUDITED_TX_WRITE, "orders+audit"),
)


def project(plan: ImplementationPlan) -> Behavior:
    """P : B -> C. This is the only observable projection."""
    return {
        PlanTag.NOOP: Behavior.NONE,
        PlanTag.CACHE_READ: Behavior.READ,
        PlanTag.TX_WRITE: Behavior.WRITE,
        PlanTag.AUDITED_TX_WRITE: Behavior.AUDITED_WRITE,
    }[plan.tag]


def left_lift(case: PublicCase, candidates: Iterable[ImplementationPlan] = PLANS) -> ImplementationPlan:
    """Least available plan whose projection covers F(case)."""
    valid = [p for p in candidates if project(p).covers(case.desired)]
    if not valid:
        raise ValueError(f"no implementation realizes {case}")
    return min(valid, key=lambda p: project(p).value)


def right_lift(case: PublicCase, candidates: Iterable[ImplementationPlan] = PLANS) -> ImplementationPlan:
    """Greatest available plan whose projection stays within F(case)."""
    valid = [p for p in candidates if case.desired.covers(project(p))]
    if not valid:
        raise ValueError(f"no sound residual for {case}")
    return max(valid, key=lambda p: project(p).value)


def assert_left_law(case: PublicCase) -> None:
    plan = left_lift(case)
    assert project(plan).covers(case.desired), (case, plan, project(plan))
    # Minimality in this finite poset approximation.
    for candidate in PLANS:
        if project(candidate).covers(case.desired):
            assert project(plan).value <= project(candidate).value


def assert_right_law(case: PublicCase) -> None:
    plan = right_lift(case)
    assert case.desired.covers(project(plan)), (case, plan, project(plan))
    # Maximality in this finite poset approximation.
    for candidate in PLANS:
        if case.desired.covers(project(candidate)):
            assert project(candidate).value <= project(plan).value


def main() -> None:
    cases = (
        PublicCase("show-order", Behavior.READ),
        PublicCase("place-order", Behavior.WRITE),
        PublicCase("place-regulated-order", Behavior.AUDITED_WRITE),
    )
    for case in cases:
        assert_left_law(case)
        assert_right_law(case)
    print("defunctionalized_lift_witness: ok")


if __name__ == "__main__":
    main()
