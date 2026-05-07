#!/usr/bin/env python3
"""Emit starter code for a chosen universalist construction and language.

Templates are intentionally small, dependency-free, and designed to be parser/typechecker friendly where possible.
They are scaffolds, not final code.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATES: dict[tuple[str, str], str] = {
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
    case "Draft": return "draft";
    case "Approved": return `approved by ${state.approvedBy}`;
    case "Published": return state.publishedAt;
  }
}
""",
    ("refined", "typescript"): """type Email = { readonly tag: "Email"; readonly value: string };

function parseEmail(raw: string): Email | null {
  const value = raw.trim().toLowerCase();
  return value.indexOf("@") >= 0 ? { tag: "Email", value } : null;
}
""",
    ("pullback", "typescript"): """type Customer = { accountId: string; name: string };
type Subscription = { accountId: string; plan: string };
type CustomerSubscription = { customer: Customer; subscription: Subscription };

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

function withFlatDiscount(discount: number): PricingPolicy {
  return (subtotal: number) => Math.max(0, subtotal - discount);
}
""",
    ("free", "typescript"): """type Rule =
  | { tag: "All"; rules: Rule[] }
  | { tag: "FieldEq"; field: string; value: string };

type Facts = Record<string, string>;

function evalRule(rule: Rule, facts: Facts): boolean {
  switch (rule.tag) {
    case "All": return rule.rules.every((child) => evalRule(child, facts));
    case "FieldEq": return facts[rule.field] === rule.value;
  }
}

function explainRule(rule: Rule): string {
  switch (rule.tag) {
    case "All": return `all(${rule.rules.map(explainRule).join(", ")})`;
    case "FieldEq": return `${rule.field} == ${rule.value}`;
  }
}
""",
    ("protocol", "typescript"): """type CheckoutState =
  | { tag: "Cart" }
  | { tag: "Shipping"; addressId: string }
  | { tag: "Payment"; addressId: string; paymentId: string }
  | { tag: "Submitted"; orderId: string };

type CheckoutEvent =
  | { tag: "SetShipping"; addressId: string }
  | { tag: "SetPayment"; paymentId: string }
  | { tag: "Submit"; orderId: string };

function transition(state: CheckoutState, event: CheckoutEvent): CheckoutState | null {
  if (state.tag === "Cart" && event.tag === "SetShipping") {
    return { tag: "Shipping", addressId: event.addressId };
  }
  if (state.tag === "Shipping" && event.tag === "SetPayment") {
    return { tag: "Payment", addressId: state.addressId, paymentId: event.paymentId };
  }
  if (state.tag === "Payment" && event.tag === "Submit") {
    return { tag: "Submitted", orderId: event.orderId };
  }
  return null;
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
    pass

@dataclass(frozen=True)
class Approved:
    approved_by: str

@dataclass(frozen=True)
class Published:
    approved_by: str
    published_at: str

DocState = Union[Draft, Approved, Published]
""",
    ("refined", "python"): """from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "Email":
        value = raw.strip().lower()
        if "@" not in value:
            raise ValueError("invalid email")
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
    ("free", "python"): """from __future__ import annotations
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class FieldEq:
    field: str
    value: str

@dataclass(frozen=True)
class All:
    rules: tuple[Rule, ...]

Rule = Union[FieldEq, All]

def eval_rule(rule: Rule, facts: dict[str, str]) -> bool:
    if isinstance(rule, FieldEq):
        return facts.get(rule.field) == rule.value
    if isinstance(rule, All):
        return all(eval_rule(child, facts) for child in rule.rules)
    raise TypeError(rule)
""",
    ("protocol", "python"): """from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Cart:
    pass

@dataclass(frozen=True)
class Shipping:
    address_id: str

@dataclass(frozen=True)
class Payment:
    address_id: str
    payment_id: str

CheckoutState = Union[Cart, Shipping, Payment]

def set_payment(state: CheckoutState, payment_id: str) -> Payment:
    if not isinstance(state, Shipping):
        raise ValueError("payment requires shipping state")
    return Payment(address_id=state.address_id, payment_id=payment_id)
""",
    ("product", "go"): """package domain

type OrderContext struct {
    CustomerID string
    Currency   string
    Locale     string
}
""",
    ("coproduct", "go"): """package domain

type DocState interface{ isDocState() }

type Draft struct{}
func (Draft) isDocState() {}

type Approved struct{ ApprovedBy string }
func (Approved) isDocState() {}
""",
    ("refined", "go"): """package domain

import (
    "fmt"
    "strings"
)

type Email string

func NewEmail(raw string) (Email, error) {
    value := strings.ToLower(strings.TrimSpace(raw))
    if !strings.Contains(value, "@") {
        return "", fmt.Errorf("invalid email")
    }
    return Email(value), nil
}
""",
    ("pullback", "go"): """package domain

import "fmt"

type Customer struct {
    AccountID string
    Name      string
}

type Subscription struct {
    AccountID string
    Plan      string
}

type CustomerSubscription struct {
    Customer     Customer
    Subscription Subscription
}

func NewCustomerSubscription(customer Customer, subscription Subscription) (CustomerSubscription, error) {
    if customer.AccountID != subscription.AccountID {
        return CustomerSubscription{}, fmt.Errorf("account mismatch")
    }
    return CustomerSubscription{Customer: customer, Subscription: subscription}, nil
}
""",
    ("exponential", "go"): """package domain

type PricingPolicy func(int) int

func WithFlatDiscount(discount int) PricingPolicy {
    return func(subtotal int) int {
        if subtotal-discount < 0 {
            return 0
        }
        return subtotal - discount
    }
}
""",
    ("free", "go"): """package domain

type Rule interface{ isRule() }

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
    ("protocol", "go"): """package domain

import "fmt"

type CheckoutState interface{ isCheckoutState() }

type Cart struct{}
func (Cart) isCheckoutState() {}

type Shipping struct{ AddressID string }
func (Shipping) isCheckoutState() {}

type Payment struct {
    AddressID string
    PaymentID string
}
func (Payment) isCheckoutState() {}

func SetPayment(state CheckoutState, paymentID string) (Payment, error) {
    shipping, ok := state.(Shipping)
    if !ok {
        return Payment{}, fmt.Errorf("payment requires shipping state")
    }
    return Payment{AddressID: shipping.AddressID, PaymentID: paymentID}, nil
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
    Published { approved_by: String, published_at: String },
}
""",
    ("refined", "rust"): """#[derive(Clone, Debug, PartialEq, Eq)]
struct Email(String);

impl Email {
    fn parse(raw: &str) -> Result<Self, String> {
        let normalized = raw.trim().to_lowercase();
        if !normalized.contains('@') {
            return Err("invalid email".to_string());
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
            return Err("account mismatch".to_string());
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
    ("free", "rust"): """use std::collections::HashMap;

enum Rule {
    FieldEq { field: String, value: String },
    All(Vec<Rule>),
}

fn eval_rule(rule: &Rule, facts: &HashMap<String, String>) -> bool {
    match rule {
        Rule::FieldEq { field, value } => facts.get(field) == Some(value),
        Rule::All(rules) => rules.iter().all(|child| eval_rule(child, facts)),
    }
}
""",
    ("protocol", "rust"): """enum CheckoutState {
    Cart,
    Shipping { address_id: String },
    Payment { address_id: String, payment_id: String },
}

fn set_payment(state: CheckoutState, payment_id: String) -> Result<CheckoutState, String> {
    match state {
        CheckoutState::Shipping { address_id } => Ok(CheckoutState::Payment { address_id, payment_id }),
        _ => Err("payment requires shipping state".to_string()),
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
