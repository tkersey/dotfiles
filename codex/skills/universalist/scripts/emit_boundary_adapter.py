#!/usr/bin/env python3
"""Emit a small boundary adapter for preserving wire/storage shape while introducing an internal model."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATES: dict[tuple[str, str], str] = {
    ("coproduct", "typescript"): """// Legacy wire shape stays stable.
type LegacyDoc = {
  status: "draft" | "approved" | "published";
  approvedBy?: string;
  publishedAt?: string;
};

// Internal stronger shape.
type DocState =
  | { tag: "Draft" }
  | { tag: "Approved"; approvedBy: string }
  | { tag: "Published"; approvedBy: string; publishedAt: string };

function decodeDoc(input: LegacyDoc): DocState | null {
  switch (input.status) {
    case "draft": return { tag: "Draft" };
    case "approved": return input.approvedBy ? { tag: "Approved", approvedBy: input.approvedBy } : null;
    case "published": return input.approvedBy && input.publishedAt
      ? { tag: "Published", approvedBy: input.approvedBy, publishedAt: input.publishedAt }
      : null;
  }
}

function encodeDoc(state: DocState): LegacyDoc {
  switch (state.tag) {
    case "Draft": return { status: "draft" };
    case "Approved": return { status: "approved", approvedBy: state.approvedBy };
    case "Published": return { status: "published", approvedBy: state.approvedBy, publishedAt: state.publishedAt };
  }
}
""",
    ("refined", "typescript"): """type Email = { readonly tag: "Email"; readonly value: string };

function parseEmail(raw: string): Email | null {
  const value = raw.trim().toLowerCase();
  return value.indexOf("@") >= 0 ? { tag: "Email", value } : null;
}

function emailToWire(email: Email): string {
  return email.value;
}
""",
    ("pullback", "typescript"): """type CustomerDTO = { accountId: string; name: string };
type SubscriptionDTO = { accountId: string; plan: string };
type CustomerSubscription = { customer: CustomerDTO; subscription: SubscriptionDTO };

function decodeCustomerSubscription(
  customer: CustomerDTO,
  subscription: SubscriptionDTO,
): CustomerSubscription | null {
  return customer.accountId === subscription.accountId ? { customer, subscription } : null;
}
""",
    ("protocol", "typescript"): """type LegacyCheckout = { status: string; addressId?: string; paymentId?: string };

type CheckoutState =
  | { tag: "Cart" }
  | { tag: "Shipping"; addressId: string }
  | { tag: "Payment"; addressId: string; paymentId: string };

function decodeCheckout(input: LegacyCheckout): CheckoutState | null {
  if (input.status === "cart") return { tag: "Cart" };
  if (input.status === "shipping" && input.addressId) return { tag: "Shipping", addressId: input.addressId };
  if (input.status === "payment" && input.addressId && input.paymentId) {
    return { tag: "Payment", addressId: input.addressId, paymentId: input.paymentId };
  }
  return null;
}
""",
    ("coproduct", "python"): """from dataclasses import dataclass
from typing import Any, Union

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

def decode_doc(row: dict[str, Any]) -> DocState:
    status = row.get("status")
    if status == "draft":
        return Draft()
    if status == "approved" and row.get("approved_by"):
        return Approved(approved_by=str(row["approved_by"]))
    if status == "published" and row.get("approved_by") and row.get("published_at"):
        return Published(approved_by=str(row["approved_by"]), published_at=str(row["published_at"]))
    raise ValueError(f"invalid legacy doc row: {row!r}")

def encode_doc(state: DocState) -> dict[str, Any]:
    if isinstance(state, Draft):
        return {"status": "draft"}
    if isinstance(state, Approved):
        return {"status": "approved", "approved_by": state.approved_by}
    if isinstance(state, Published):
        return {"status": "published", "approved_by": state.approved_by, "published_at": state.published_at}
    raise TypeError(state)
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

def email_to_wire(email: Email) -> str:
    return email.value
""",
    ("pullback", "python"): """from dataclasses import dataclass

@dataclass(frozen=True)
class CustomerDTO:
    account_id: str
    name: str

@dataclass(frozen=True)
class SubscriptionDTO:
    account_id: str
    plan: str

@dataclass(frozen=True)
class CustomerSubscription:
    customer: CustomerDTO
    subscription: SubscriptionDTO

    @classmethod
    def create(cls, customer: CustomerDTO, subscription: SubscriptionDTO) -> "CustomerSubscription":
        if customer.account_id != subscription.account_id:
            raise ValueError("account mismatch")
        return cls(customer=customer, subscription=subscription)
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
        Path(args.write).write_text(template, encoding="utf-8")
    else:
        sys.stdout.write(template)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
