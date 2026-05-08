// Defunctionalized boundary IR for Kan-shaped architecture.
// This file is a witness pattern, not a full framework.

export type PublicCase =
  | { tag: "ShowOrder"; orderId: string }
  | { tag: "PlaceOrder"; orderId: string; amount: number }
  | { tag: "RefundOrder"; orderId: string; reason: string };

export type DesiredBehavior =
  | { tag: "ReturnStatus"; status: number }
  | { tag: "EmitAuditEvent"; event: string }
  | { tag: "Reject"; reason: string };

// Lft-style defunctionalized realizer behind P.
export type ImplementationPlan =
  | { tag: "UseReadModel"; model: string }
  | { tag: "UseTransactionalWrite"; table: string }
  | { tag: "UseExternalCapability"; capability: string };

// Rft-style residual obligation behind P.
export type Obligation =
  | { tag: "NeedsField"; table: string; field: string }
  | { tag: "NeedsAuditEvent"; event: string }
  | { tag: "NeedsIdempotencyKey"; scope: string };

export function projectImplementation(
  plan: ImplementationPlan,
  useCase: PublicCase,
): DesiredBehavior {
  switch (plan.tag) {
    case "UseReadModel":
      return { tag: "ReturnStatus", status: 200 };
    case "UseTransactionalWrite":
      return { tag: "EmitAuditEvent", event: `${useCase.tag}.committed` };
    case "UseExternalCapability":
      return { tag: "ReturnStatus", status: 202 };
  }
}

export function deriveObligations(useCase: PublicCase): Obligation[] {
  switch (useCase.tag) {
    case "ShowOrder":
      return [{ tag: "NeedsField", table: "orders", field: "id" }];
    case "PlaceOrder":
      return [
        { tag: "NeedsField", table: "orders", field: "amount" },
        { tag: "NeedsAuditEvent", event: "PlaceOrder.committed" },
        { tag: "NeedsIdempotencyKey", scope: "order-write" },
      ];
    case "RefundOrder":
      return [
        { tag: "NeedsField", table: "refunds", field: "reason" },
        { tag: "NeedsAuditEvent", event: "RefundOrder.committed" },
      ];
  }
}

// Law-test idea:
// projectImplementation(leftLift(useCase), useCase) should satisfy desiredBehavior(useCase).
// satisfyAll(deriveObligations(useCase), implementation) should be sound for the public projection.
