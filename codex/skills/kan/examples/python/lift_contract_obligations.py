"""Kan-lift-shaped contract refactor witness.

A = public contract cases
B = internal implementation plans / obligations
C = observable behavior flags
P : B -> C projects internals to public behavior
F : A -> C gives required public behavior

The script computes a least covering realizer for a case when it exists and
reports missing obligations when no exact/current lift exists.
"""

from dataclasses import dataclass
from typing import FrozenSet, Iterable

Behavior = FrozenSet[str]
Capability = FrozenSet[str]


@dataclass(frozen=True)
class ContractCase:
    name: str
    required: Behavior


@dataclass(frozen=True)
class ImplementationPlan:
    name: str
    capabilities: Capability


def project(plan: ImplementationPlan) -> Behavior:
    """P : B -> C, modeled as observable behavior induced by capabilities."""
    produced = set()
    caps = plan.capabilities
    if "state-machine" in caps:
        produced.add("reject-after-settlement")
    if "audit-sink" in caps:
        produced.add("emit-audit-event")
    if "idempotency-store" in caps:
        produced.add("idempotent-retry")
    if "auth-metadata" in caps:
        produced.add("return-authorization-metadata")
    if "cancel-reason" in caps:
        produced.add("return-cancellation-reason")
    return frozenset(produced)


def covers(required: Behavior, actual: Behavior) -> bool:
    """Comparison relation in C: required behavior is a subset of projected behavior."""
    return required.issubset(actual)


def least_covering_plan(case: ContractCase, candidates: Iterable[ImplementationPlan]) -> ImplementationPlan | None:
    """Lft-like finite search: least candidate whose projection covers F(case)."""
    covering = [p for p in candidates if covers(case.required, project(p))]
    if not covering:
        return None
    return min(covering, key=lambda p: (len(p.capabilities), p.name))


def missing_obligations(case: ContractCase, current: ImplementationPlan) -> Behavior:
    """Rft-like residual report: observations F needs that P(current) lacks."""
    return frozenset(case.required - project(current))


def test_lift_witness() -> None:
    refund = ContractCase(
        "refund",
        frozenset({"reject-after-settlement", "emit-audit-event", "idempotent-retry"}),
    )
    current = ImplementationPlan("current-crud-service", frozenset({"audit-sink"}))
    candidates = [
        current,
        ImplementationPlan("workflow-only", frozenset({"state-machine"})),
        ImplementationPlan("workflow-with-audit", frozenset({"state-machine", "audit-sink"})),
        ImplementationPlan(
            "refund-workflow",
            frozenset({"state-machine", "audit-sink", "idempotency-store"}),
        ),
        ImplementationPlan(
            "overbuilt-payment-platform",
            frozenset({"state-machine", "audit-sink", "idempotency-store", "auth-metadata"}),
        ),
    ]

    missing = missing_obligations(refund, current)
    assert missing == frozenset({"reject-after-settlement", "idempotent-retry"})

    plan = least_covering_plan(refund, candidates)
    assert plan is not None
    assert plan.name == "refund-workflow"
    assert covers(refund.required, project(plan))

    smaller = [p for p in candidates if len(p.capabilities) < len(plan.capabilities)]
    assert all(not covers(refund.required, project(p)) for p in smaller)


def test_no_exact_lift_report() -> None:
    cancellation = ContractCase("cancel-order", frozenset({"return-cancellation-reason"}))
    current = ImplementationPlan("current-order-model", frozenset({"state-machine"}))
    missing = missing_obligations(cancellation, current)
    assert missing == frozenset({"return-cancellation-reason"})

    candidates = [current, ImplementationPlan("status-plus-audit", frozenset({"state-machine", "audit-sink"}))]
    assert least_covering_plan(cancellation, candidates) is None


if __name__ == "__main__":
    test_lift_witness()
    test_no_exact_lift_report()
    print("lift_contract_obligations: ok")
