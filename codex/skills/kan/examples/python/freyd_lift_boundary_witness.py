#!/usr/bin/env python3
"""Tiny Freyd/AFT-style lift-boundary witness.

This is not a theorem prover. It models the architecture heuristic:

- public requirements are observable behaviors;
- implementation templates are a bounded solution-set-like menu;
- a free-builder-like function chooses a canonical internal plan;
- projection tests check that the plan realizes or covers the requirement.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class RequiredBehavior:
    name: str
    requires_idempotency: bool = False
    requires_audit: bool = False
    requires_state_guard: bool = False


@dataclass(frozen=True)
class ImplementationTemplate:
    name: str
    supports_idempotency: bool = False
    supports_audit: bool = False
    supports_state_guard: bool = False

    def covers(self, req: RequiredBehavior) -> bool:
        return (
            (not req.requires_idempotency or self.supports_idempotency)
            and (not req.requires_audit or self.supports_audit)
            and (not req.requires_state_guard or self.supports_state_guard)
        )


@dataclass(frozen=True)
class ImplementationPlan:
    requirement: RequiredBehavior
    template: ImplementationTemplate
    exact: bool


TEMPLATES = [
    ImplementationTemplate("sync-service", supports_audit=True),
    ImplementationTemplate("idempotency-table", supports_idempotency=True, supports_audit=True),
    ImplementationTemplate("state-machine", supports_audit=True, supports_state_guard=True),
    ImplementationTemplate("event-sourced-workflow", supports_idempotency=True, supports_audit=True, supports_state_guard=True),
]


def free_builder(req: RequiredBehavior, templates: Iterable[ImplementationTemplate] = TEMPLATES) -> ImplementationPlan:
    """Choose the first bounded template covering the observable requirement."""
    for template in templates:
        if template.covers(req):
            # Exactness is a separate architecture classification.
            exact = template.name == "event-sourced-workflow" and req.requires_state_guard
            return ImplementationPlan(req, template, exact=exact)
    raise ValueError(f"no-exact-lift/no-covering-template for {req.name}")


def project(plan: ImplementationPlan) -> RequiredBehavior:
    """Projection P : B -> C, approximated by observable capabilities."""
    t = plan.template
    return RequiredBehavior(
        name=plan.requirement.name,
        requires_idempotency=t.supports_idempotency,
        requires_audit=t.supports_audit,
        requires_state_guard=t.supports_state_guard,
    )


def covers(projected: RequiredBehavior, required: RequiredBehavior) -> bool:
    return (
        (not required.requires_idempotency or projected.requires_idempotency)
        and (not required.requires_audit or projected.requires_audit)
        and (not required.requires_state_guard or projected.requires_state_guard)
    )


def main() -> None:
    requirements = [
        RequiredBehavior("authorize", requires_audit=True),
        RequiredBehavior("refund", requires_idempotency=True, requires_audit=True, requires_state_guard=True),
    ]
    for req in requirements:
        plan = free_builder(req)
        observed = project(plan)
        assert covers(observed, req), (req, plan, observed)
        print(f"{req.name}: Free -> {plan.template.name}; exact={plan.exact}; projection covers requirement")

    impossible = RequiredBehavior("manual-review", requires_idempotency=True, requires_audit=True, requires_state_guard=True)
    try:
        free_builder(impossible, templates=[TEMPLATES[0]])
    except ValueError as exc:
        print(str(exc))


if __name__ == "__main__":
    main()
