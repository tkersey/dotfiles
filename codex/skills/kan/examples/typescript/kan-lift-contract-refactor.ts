// Kan-lift-shaped contract-first refactor sketch.
// A = public contract cases
// B = internal implementation candidates
// C = observable behavior
// P : B -> C = projectImplementation
// F : A -> C = requiredBehavior

export type ContractCase =
  | { tag: "Refund"; idempotencyKey: string }
  | { tag: "CancelOrder"; orderId: string };

export type PublicObservation =
  | { tag: "StatusCode" }
  | { tag: "ResponseField"; path: string }
  | { tag: "AuditEvent"; event: string }
  | { tag: "IdempotentRetry"; key: string };

export type ObservableBehavior = {
  statusCode: number;
  fields: Record<string, unknown>;
  auditEvents: string[];
  idempotencyKeys: string[];
};

export type CandidateRealizer =
  | { tag: "WorkflowStep"; workflow: "refund" | "cancel"; capabilities: string[] }
  | { tag: "RepositoryChange"; table: string; fields: string[] }
  | { tag: "ExternalCapability"; capability: string };

export type ProjectionPath =
  | { tag: "ControllerResponse" }
  | { tag: "AuditTrace" }
  | { tag: "PersistenceView" };

export type ImplementationObligation =
  | { tag: "NeedsData"; field: string; reason: string }
  | { tag: "NeedsTransition"; transition: string; reason: string }
  | { tag: "NeedsCapability"; capability: string; reason: string }
  | { tag: "NeedsProjectionPath"; path: string; reason: string };

export function requiredBehavior(c: ContractCase): ObservableBehavior {
  switch (c.tag) {
    case "Refund":
      return {
        statusCode: 200,
        fields: { result: "refunded" },
        auditEvents: ["Refunded"],
        idempotencyKeys: [c.idempotencyKey],
      };
    case "CancelOrder":
      return {
        statusCode: 200,
        fields: { result: "cancelled", reason: "required" },
        auditEvents: ["OrderCancelled"],
        idempotencyKeys: [],
      };
  }
}

export function projectImplementation(r: CandidateRealizer, path: ProjectionPath): ObservableBehavior {
  if (r.tag === "WorkflowStep" && r.workflow === "refund") {
    return {
      statusCode: 200,
      fields: { result: "refunded" },
      auditEvents: r.capabilities.includes("audit-sink") ? ["Refunded"] : [],
      idempotencyKeys: r.capabilities.includes("idempotency-store") ? ["refund-key"] : [],
    };
  }
  if (r.tag === "WorkflowStep" && r.workflow === "cancel") {
    return {
      statusCode: 200,
      fields: r.capabilities.includes("cancel-reason")
        ? { result: "cancelled", reason: "required" }
        : { result: "cancelled" },
      auditEvents: r.capabilities.includes("audit-sink") ? ["OrderCancelled"] : [],
      idempotencyKeys: [],
    };
  }
  return { statusCode: 500, fields: {}, auditEvents: [], idempotencyKeys: [] };
}

export function observe(b: ObservableBehavior, obs: PublicObservation): unknown {
  switch (obs.tag) {
    case "StatusCode":
      return b.statusCode;
    case "ResponseField":
      return b.fields[obs.path];
    case "AuditEvent":
      return b.auditEvents.includes(obs.event);
    case "IdempotentRetry":
      return b.idempotencyKeys.includes(obs.key);
  }
}

export function deriveObligations(c: ContractCase, candidate: CandidateRealizer): ImplementationObligation[] {
  const required = requiredBehavior(c);
  const actual = projectImplementation(candidate, { tag: "ControllerResponse" });
  const obligations: ImplementationObligation[] = [];

  for (const event of required.auditEvents) {
    if (!actual.auditEvents.includes(event)) {
      obligations.push({ tag: "NeedsCapability", capability: "audit-sink", reason: `must emit ${event}` });
    }
  }
  for (const key of required.idempotencyKeys) {
    if (!actual.idempotencyKeys.includes(key)) {
      obligations.push({ tag: "NeedsCapability", capability: "idempotency-store", reason: `must preserve ${key}` });
    }
  }
  if ("reason" in required.fields && !("reason" in actual.fields)) {
    obligations.push({ tag: "NeedsData", field: "cancellation.reason", reason: "public view requires reason" });
  }

  return obligations;
}

export function checkLift(c: ContractCase, candidate: CandidateRealizer, observations: PublicObservation[]): boolean {
  const required = requiredBehavior(c);
  const actual = projectImplementation(candidate, { tag: "ControllerResponse" });
  return observations.every((obs) => observe(required, obs) === observe(actual, obs));
}
