"""Small Yoneda/Coyoneda witness for a Kan-lift architecture slice.

Yoneda side: public behavior is represented by sanctioned observations.
Coyoneda side: candidate internal realizers carry deferred projection paths.
The law test checks that projection of the realizer satisfies required observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence


@dataclass(frozen=True)
class Behavior:
    status: int
    json: Mapping[str, Any]
    audit_events: tuple[str, ...]


@dataclass(frozen=True)
class Observation:
    tag: Literal["status", "json_field", "audit_event"]
    key: str | None = None


def observe(behavior: Behavior, obs: Observation) -> Any:
    if obs.tag == "status":
        return behavior.status
    if obs.tag == "json_field":
        assert obs.key is not None
        return behavior.json.get(obs.key)
    if obs.tag == "audit_event":
        assert obs.key is not None
        return obs.key in behavior.audit_events
    raise ValueError(obs)


@dataclass(frozen=True)
class ServiceMethod:
    method_name: str
    response: Behavior


@dataclass(frozen=True)
class WorkflowStep:
    step_name: str
    emitted_event: str


Realizer = ServiceMethod | WorkflowStep


@dataclass(frozen=True)
class ProjectionPath:
    tag: Literal["method_to_behavior", "step_to_audit"]
    event_name: str | None = None


@dataclass(frozen=True)
class DeferredProjection:
    realizer: Realizer
    path: ProjectionPath


def project(x: DeferredProjection) -> Behavior:
    if isinstance(x.realizer, ServiceMethod):
        if x.path.tag != "method_to_behavior":
            raise ValueError("service method cannot use projection path")
        return x.realizer.response
    if isinstance(x.realizer, WorkflowStep):
        if x.path.tag != "step_to_audit":
            raise ValueError("workflow step cannot use projection path")
        event = x.path.event_name or x.realizer.emitted_event
        return Behavior(
            status=202,
            json={"step": x.realizer.step_name},
            audit_events=(event, x.realizer.emitted_event),
        )
    raise TypeError(x.realizer)


def satisfies(candidate: DeferredProjection, required: Behavior, observations: Sequence[Observation]) -> bool:
    actual = project(candidate)
    return all(observe(actual, obs) == observe(required, obs) for obs in observations)


def main() -> None:
    required = Behavior(status=201, json={"id": "pmt_123"}, audit_events=("payment.authorized",))
    candidate = DeferredProjection(
        realizer=ServiceMethod("authorize", required),
        path=ProjectionPath("method_to_behavior"),
    )
    observations = [
        Observation("status"),
        Observation("json_field", "id"),
        Observation("audit_event", "payment.authorized"),
    ]
    assert satisfies(candidate, required, observations)

    bad = DeferredProjection(
        realizer=WorkflowStep("authorize", "payment.started"),
        path=ProjectionPath("step_to_audit", "payment.authorized"),
    )
    assert not satisfies(bad, required, observations)
    print("yoneda_coyoneda_witness: ok")


if __name__ == "__main__":
    main()
