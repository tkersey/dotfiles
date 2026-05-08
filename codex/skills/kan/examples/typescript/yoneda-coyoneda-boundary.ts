// Yoneda/Coyoneda boundary witness for architecture work.
// This is intentionally small and dependency-free.

export type Observation =
  | { tag: "StatusCode" }
  | { tag: "JsonField"; path: string }
  | { tag: "AuditEvent"; name: string };

export type ObservableBehavior = {
  status: number;
  json: Record<string, unknown>;
  auditEvents: string[];
};

export function runObservation(value: ObservableBehavior, obs: Observation): unknown {
  switch (obs.tag) {
    case "StatusCode":
      return value.status;
    case "JsonField":
      return value.json[obs.path];
    case "AuditEvent":
      return value.auditEvents.includes(obs.name);
  }
}

// Yoneda-style local reading: expose sanctioned observations instead of
// leaking the internal representation.
export type PublicView = {
  observe: (obs: Observation) => unknown;
};

export function toPublicView(value: ObservableBehavior): PublicView {
  return { observe: (obs) => runObservation(value, obs) };
}

export type CandidateRealizer =
  | { tag: "ServiceMethod"; methodName: string; response: ObservableBehavior }
  | { tag: "WorkflowStep"; stepName: string; emitted: string };

export type ProjectionPath =
  | { tag: "MethodToBehavior" }
  | { tag: "StepToAuditEvent"; name: string };

// Coyoneda-style local reading: package a raw implementation payload plus a
// deferred projection path, then lower through one interpreter.
export type DeferredProjection = {
  realizer: CandidateRealizer;
  path: ProjectionPath;
};

export function projectImplementation(x: DeferredProjection): ObservableBehavior {
  switch (x.realizer.tag) {
    case "ServiceMethod":
      if (x.path.tag !== "MethodToBehavior") {
        throw new Error("service method does not support this projection path");
      }
      return x.realizer.response;
    case "WorkflowStep":
      if (x.path.tag !== "StepToAuditEvent") {
        throw new Error("workflow step does not support this projection path");
      }
      return {
        status: 202,
        json: { step: x.realizer.stepName },
        auditEvents: [x.path.name, x.realizer.emitted],
      };
  }
}

// Lift-style law witness: projected implementation satisfies public observations.
export function satisfiesObservation(
  projected: DeferredProjection,
  required: ObservableBehavior,
  obs: Observation,
): boolean {
  return Object.is(
    runObservation(projectImplementation(projected), obs),
    runObservation(required, obs),
  );
}

const required: ObservableBehavior = {
  status: 201,
  json: { id: "pmt_123" },
  auditEvents: ["payment.authorized"],
};

const candidate: DeferredProjection = {
  realizer: { tag: "ServiceMethod", methodName: "authorize", response: required },
  path: { tag: "MethodToBehavior" },
};

console.assert(satisfiesObservation(candidate, required, { tag: "StatusCode" }));
console.assert(satisfiesObservation(candidate, required, { tag: "JsonField", path: "id" }));
console.assert(satisfiesObservation(candidate, required, { tag: "AuditEvent", name: "payment.authorized" }));
