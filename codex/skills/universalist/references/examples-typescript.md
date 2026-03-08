# TypeScript Examples

## Table of contents
- Product and terminal object
- Coproduct and initial object
- Refined type
- Pullback witness
- Exponential
- Free construction
- ADD sub-lens

## Product and terminal object
```ts
type Money = { amount: number; currency: string };
type NoPayload = Record<never, never>;
```

## Coproduct and initial object
```ts
type LegacyDocument = {
  status: string;
  approvedBy?: string;
  publishedAt?: string;
  archivedReason?: string;
};

type DocState =
  | { tag: "Draft" }
  | { tag: "Approved"; approvedBy: string }
  | { tag: "Published"; approvedBy: string; publishedAt: string }
  | { tag: "Archived"; archivedReason: string };

function toState(doc: LegacyDocument): DocState | null {
  switch (doc.status) {
    case "draft":
      return doc.approvedBy == null && doc.publishedAt == null && doc.archivedReason == null
        ? { tag: "Draft" }
        : null;
    case "approved":
      return doc.approvedBy != null && doc.publishedAt == null && doc.archivedReason == null
        ? { tag: "Approved", approvedBy: doc.approvedBy }
        : null;
    case "published":
      return doc.approvedBy != null && doc.publishedAt != null && doc.archivedReason == null
        ? { tag: "Published", approvedBy: doc.approvedBy, publishedAt: doc.publishedAt }
        : null;
    case "archived":
      return doc.archivedReason != null && doc.approvedBy == null && doc.publishedAt == null
        ? { tag: "Archived", archivedReason: doc.archivedReason }
        : null;
    default:
      return null;
  }
}

function renderState(state: DocState): string {
  switch (state.tag) {
    case "Draft":
      return "draft";
    case "Approved":
      return state.approvedBy;
    case "Published":
      return state.publishedAt;
    case "Archived":
      return state.archivedReason;
  }
}
```

## Refined type
```ts
type Email = { tag: "Email"; value: string };

function mkEmail(raw: string): Email | null {
  const value = raw.trim().toLowerCase();
  return value.length === 0 ? null : { tag: "Email", value };
}
```

## Pullback witness
```ts
type Customer = { accountId: string; name: string };
type Subscription = { accountId: string; plan: string };
type CustomerSubscription = { customer: Customer; subscription: Subscription };

function mkCustomerSubscription(
  customer: Customer,
  subscription: Subscription
): CustomerSubscription | null {
  return customer.accountId === subscription.accountId
    ? { customer, subscription }
    : null;
}
```

## Exponential
```ts
type Formatter = (body: string) => string;

function withPrefix(prefix: string): Formatter {
  return body => `${prefix}${body}`;
}
```

## Free construction
```ts
type Rule =
  | { tag: "All"; rules: Rule[] }
  | { tag: "Any"; rules: Rule[] }
  | { tag: "Not"; rule: Rule }
  | { tag: "FieldEq"; field: string; value: string };

type Facts = Record<string, string>;

function evaluateRule(rule: Rule, facts: Facts): boolean {
  switch (rule.tag) {
    case "All":
      return rule.rules.every(child => evaluateRule(child, facts));
    case "Any":
      return rule.rules.some(child => evaluateRule(child, facts));
    case "Not":
      return !evaluateRule(rule.rule, facts);
    case "FieldEq":
      return facts[rule.field] === rule.value;
  }
}

function explainRule(rule: Rule): string {
  switch (rule.tag) {
    case "All":
      return `all(${rule.rules.map(explainRule).join(", ")})`;
    case "Any":
      return `any(${rule.rules.map(explainRule).join(", ")})`;
    case "Not":
      return `not(${explainRule(rule.rule)})`;
    case "FieldEq":
      return `${rule.field} == ${rule.value}`;
  }
}
```

## ADD sub-lens
```ts
type Log = { lines: string[] };
const emptyLog: Log = { lines: [] };

function combineLog(a: Log, b: Log): Log {
  return { lines: [...a.lines, ...b.lines] };
}
```
