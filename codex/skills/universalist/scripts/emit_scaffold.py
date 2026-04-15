#!/usr/bin/env python3
"""Emit starter code for a chosen construction and language."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATES = {
    ("product", "typescript"): """type OrderContext = {
  customerId: string;
  currency: string;
  locale: string;
};

const context: OrderContext = {
  customerId: "cust_123",
  currency: "USD",
  locale: "en-US",
};
""",
    ("coproduct", "typescript"): """type DocState =
  | { tag: "Draft" }
  | { tag: "Approved"; approvedBy: string }
  | { tag: "Published"; approvedBy: string; publishedAt: string };

function renderState(state: DocState): string {
  switch (state.tag) {
    case "Draft":
      return "draft";
    case "Approved":
      return `approved by ${state.approvedBy}`;
    case "Published":
      return state.publishedAt;
  }
}
""",
    ("refined", "typescript"): """type Email = { tag: "Email"; value: string };

function parseEmail(raw: string): Email | null {
  const value = raw.trim().toLowerCase();
  return value.length === 0 ? null : { tag: "Email", value };
}
""",
    ("pullback", "typescript"): """type Customer = { accountId: string; name: string };
type Subscription = { accountId: string; plan: string };

type CustomerSubscription = {
  customer: Customer;
  subscription: Subscription;
};

function mkCustomerSubscription(
  customer: Customer,
  subscription: Subscription,
): CustomerSubscription | null {
  return customer.accountId === subscription.accountId
    ? { customer, subscription }
    : null;
}
""",
    ("exponential", "typescript"): """type PricingPolicy = (subtotal: number) => number;

const withFlatDiscount =
  (discount: number): PricingPolicy =>
  subtotal =>
    Math.max(0, subtotal - discount);
""",
    ("free", "typescript"): """type Rule =
  | { tag: "All"; rules: Rule[] }
  | { tag: "FieldEq"; field: string; value: string };

type Facts = Record<string, string>;

function evalRule(rule: Rule, facts: Facts): boolean {
  switch (rule.tag) {
    case "All":
      return rule.rules.every(child => evalRule(child, facts));
    case "FieldEq":
      return facts[rule.field] === rule.value;
  }
}

function explainRule(rule: Rule): string {
  switch (rule.tag) {
    case "All":
      return `all(${rule.rules.map(explainRule).join(", ")})`;
    case "FieldEq":
      return `${rule.field} == ${rule.value}`;
  }
}
""",
    ("product", "python"): """from dataclasses import dataclass

@dataclass(frozen=True)
class OrderContext:
    customer_id: str
    currency: str
    locale: str
""",
    ("coproduct", "python"): """from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Draft:
    tag: str = "draft"

@dataclass(frozen=True)
class Approved:
    approved_by: str
    tag: str = "approved"

DocState = Union[Draft, Approved]
""",
    ("refined", "python"): """from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        value = raw.strip().lower()
        if not value:
            raise ValueError("empty email")
        return cls(value)
""",
    ("pullback", "python"): """from dataclasses import dataclass

@dataclass(frozen=True)
class Customer:
    account_id: str
    name: str

@dataclass(frozen=True)
class Subscription:
    account_id: str
    plan: str

@dataclass(frozen=True)
class CustomerSubscription:
    customer: Customer
    subscription: Subscription

    @classmethod
    def create(cls, customer: Customer, subscription: Subscription) -> "CustomerSubscription":
        if customer.account_id != subscription.account_id:
            raise ValueError("account mismatch")
        return cls(customer=customer, subscription=subscription)
""",
    ("exponential", "python"): """from typing import Callable

PricingPolicy = Callable[[int], int]

def with_flat_discount(discount: int) -> PricingPolicy:
    return lambda subtotal: max(0, subtotal - discount)
""",
    ("free", "python"): """from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class FieldEq:
    field: str
    value: str

@dataclass(frozen=True)
class All:
    rules: tuple["Rule", ...]

Rule = Union[FieldEq, All]

def eval_rule(rule: Rule, facts: dict[str, str]) -> bool:
    if isinstance(rule, FieldEq):
        return facts.get(rule.field) == rule.value
    if isinstance(rule, All):
        return all(eval_rule(child, facts) for child in rule.rules)
    raise TypeError(rule)
""",
    ("product", "go"): """type OrderContext struct {
    CustomerID string
    Currency   string
    Locale     string
}
""",
    ("coproduct", "go"): """type DocState interface{ isDocState() }

type Draft struct{}
func (Draft) isDocState() {}

type Approved struct{ ApprovedBy string }
func (Approved) isDocState() {}
""",
    ("refined", "go"): """type Email string

func NewEmail(raw string) (Email, error) {
    value := strings.ToLower(strings.TrimSpace(raw))
    if value == "" {
        return "", fmt.Errorf("empty email")
    }
    return Email(value), nil
}
""",
    ("pullback", "go"): """type Customer struct {
    AccountID string
    Name      string
}

type Subscription struct {
    AccountID string
    Plan      string
}

type CustomerSubscription struct {
    customer     Customer
    subscription Subscription
}

func NewCustomerSubscription(customer Customer, subscription Subscription) (CustomerSubscription, error) {
    if customer.AccountID != subscription.AccountID {
        return CustomerSubscription{}, fmt.Errorf("account mismatch")
    }
    return CustomerSubscription{customer: customer, subscription: subscription}, nil
}
""",
    ("exponential", "go"): """type PricingPolicy func(int) int

func WithFlatDiscount(discount int) PricingPolicy {
    return func(subtotal int) int {
        if subtotal-discount < 0 {
            return 0
        }
        return subtotal - discount
    }
}
""",
    ("free", "go"): """type Rule interface{ isRule() }

type FieldEq struct {
    Field string
    Value string
}
func (FieldEq) isRule() {}

type All struct{ Rules []Rule }
func (All) isRule() {}

func EvalRule(rule Rule, facts map[string]string) bool {
    switch v := rule.(type) {
    case FieldEq:
        return facts[v.Field] == v.Value
    case All:
        for _, child := range v.Rules {
            if !EvalRule(child, facts) {
                return false
            }
        }
        return true
    default:
        return false
    }
}
""",
    ("product", "java"): """public record OrderContext(String customerId, String currency, String locale) {}
""",
    ("coproduct", "java"): """public sealed interface DocState permits Draft, Approved {}

public record Draft() implements DocState {}
public record Approved(String approvedBy) implements DocState {}
""",
    ("refined", "java"): """public final class Email {
    private final String value;

    private Email(String value) {
        this.value = value;
    }

    public static Email parse(String raw) {
        String normalized = raw.trim().toLowerCase();
        if (normalized.isEmpty()) {
            throw new IllegalArgumentException("empty email");
        }
        return new Email(normalized);
    }

    public String value() {
        return value;
    }
}
""",
    ("pullback", "java"): """public record Customer(String accountId, String name) {}
public record Subscription(String accountId, String plan) {}

public final class CustomerSubscription {
    private final Customer customer;
    private final Subscription subscription;

    private CustomerSubscription(Customer customer, Subscription subscription) {
        this.customer = customer;
        this.subscription = subscription;
    }

    public static CustomerSubscription create(Customer customer, Subscription subscription) {
        if (!customer.accountId().equals(subscription.accountId())) {
            throw new IllegalArgumentException("account mismatch");
        }
        return new CustomerSubscription(customer, subscription);
    }
}
""",
    ("exponential", "java"): """import java.util.function.Function;

Function<Integer, Integer> withFlatDiscount(int discount) {
    return subtotal -> Math.max(0, subtotal - discount);
}
""",
    ("free", "java"): """public sealed interface Rule permits FieldEq, All {}

public record FieldEq(String field, String value) implements Rule {}
public record All(java.util.List<Rule> rules) implements Rule {}

public final class EvalRule {
    public static boolean eval(Rule rule, java.util.Map<String, String> facts) {
        if (rule instanceof FieldEq fieldEq) {
            return java.util.Objects.equals(facts.get(fieldEq.field()), fieldEq.value());
        }
        if (rule instanceof All all) {
            for (Rule child : all.rules()) {
                if (!eval(child, facts)) {
                    return false;
                }
            }
            return true;
        }
        throw new IllegalArgumentException("unknown rule");
    }
}
""",
    ("product", "kotlin"): """data class OrderContext(
    val customerId: String,
    val currency: String,
    val locale: String,
)
""",
    ("coproduct", "kotlin"): """sealed interface DocState {
    data object Draft : DocState
    data class Approved(val approvedBy: String) : DocState
}
""",
    ("refined", "kotlin"): """@JvmInline
value class Email private constructor(val value: String) {
    companion object {
        fun parse(raw: String): Email {
            val normalized = raw.trim().lowercase()
            require(normalized.isNotEmpty()) { "empty email" }
            return Email(normalized)
        }
    }
}
""",
    ("pullback", "kotlin"): """data class Customer(val accountId: String, val name: String)
data class Subscription(val accountId: String, val plan: String)

data class CustomerSubscription private constructor(
    val customer: Customer,
    val subscription: Subscription,
) {
    companion object {
        fun create(customer: Customer, subscription: Subscription): CustomerSubscription {
            require(customer.accountId == subscription.accountId) { "account mismatch" }
            return CustomerSubscription(customer, subscription)
        }
    }
}
""",
    ("exponential", "kotlin"): """typealias PricingPolicy = (Int) -> Int

fun withFlatDiscount(discount: Int): PricingPolicy = { subtotal ->
    maxOf(0, subtotal - discount)
}
""",
    ("free", "kotlin"): """sealed interface Rule {
    data class FieldEq(val field: String, val value: String) : Rule
    data class All(val rules: List<Rule>) : Rule
}

fun evalRule(rule: Rule, facts: Map<String, String>): Boolean =
    when (rule) {
        is Rule.FieldEq -> facts[rule.field] == rule.value
        is Rule.All -> rule.rules.all { child -> evalRule(child, facts) }
    }
""",
    ("product", "rust"): """struct OrderContext {
    customer_id: String,
    currency: String,
    locale: String,
}
""",
    ("coproduct", "rust"): """enum DocState {
    Draft,
    Approved { approved_by: String },
}
""",
    ("refined", "rust"): """#[derive(Clone, Debug, PartialEq, Eq)]
struct Email(String);

impl Email {
    fn parse(raw: &str) -> Result<Self, String> {
        let normalized = raw.trim().to_lowercase();
        if normalized.is_empty() {
            return Err("empty email".into());
        }
        Ok(Self(normalized))
    }
}
""",
    ("pullback", "rust"): """struct Customer {
    account_id: String,
    name: String,
}

struct Subscription {
    account_id: String,
    plan: String,
}

struct CustomerSubscription {
    customer: Customer,
    subscription: Subscription,
}

impl CustomerSubscription {
    fn create(customer: Customer, subscription: Subscription) -> Result<Self, String> {
        if customer.account_id != subscription.account_id {
            return Err("account mismatch".into());
        }
        Ok(Self { customer, subscription })
    }
}
""",
    ("exponential", "rust"): """type PricingPolicy = Box<dyn Fn(i64) -> i64>;

fn with_flat_discount(discount: i64) -> PricingPolicy {
    Box::new(move |subtotal| (subtotal - discount).max(0))
}
""",
    ("free", "rust"): """enum Rule {
    FieldEq { field: String, value: String },
    All(Vec<Rule>),
}

fn eval_rule(rule: &Rule, facts: &std::collections::HashMap<String, String>) -> bool {
    match rule {
        Rule::FieldEq { field, value } => facts.get(field) == Some(value),
        Rule::All(rules) => rules.iter().all(|child| eval_rule(child, facts)),
    }
}
""",
}

CONSTRUCTIONS = sorted({construction for construction, _ in TEMPLATES})
LANGUAGES = sorted({language for _, language in TEMPLATES})


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("construction", nargs="?", help=f"one of: {', '.join(CONSTRUCTIONS)}")
    parser.add_argument("language", nargs="?", help=f"one of: {', '.join(LANGUAGES)}")
    parser.add_argument("--write", help="write output to this file instead of stdout")
    parser.add_argument("--list", action="store_true", help="list supported combinations")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.list:
        for construction in CONSTRUCTIONS:
            supported = [lang for (cons, lang) in TEMPLATES if cons == construction]
            print(f"{construction}: {', '.join(sorted(supported))}")
        return 0

    if not args.construction or not args.language:
        print("construction and language are required unless --list is used", file=sys.stderr)
        return 2

    key = (args.construction.lower(), args.language.lower())
    template = TEMPLATES.get(key)
    if template is None:
        print(f"Unsupported combination: {args.construction} / {args.language}", file=sys.stderr)
        return 2

    if args.write:
        path = Path(args.write)
        path.write_text(template, encoding="utf-8")
    else:
        sys.stdout.write(template)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
