#!/usr/bin/env python3
"""Emit boundary adapter skeletons for staged Universalist migrations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATES = {
    ("coproduct", "typescript"): """type LegacyDocumentRow = {
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

export function decodeDocState(row: LegacyDocumentRow): DocState | null {
  switch (row.status) {
    case "draft":
      return row.approvedBy == null && row.publishedAt == null && row.archivedReason == null
        ? { tag: "Draft" }
        : null;
    case "approved":
      return row.approvedBy != null && row.publishedAt == null && row.archivedReason == null
        ? { tag: "Approved", approvedBy: row.approvedBy }
        : null;
    case "published":
      return row.approvedBy != null && row.publishedAt != null && row.archivedReason == null
        ? { tag: "Published", approvedBy: row.approvedBy, publishedAt: row.publishedAt }
        : null;
    case "archived":
      return row.archivedReason != null && row.approvedBy == null && row.publishedAt == null
        ? { tag: "Archived", archivedReason: row.archivedReason }
        : null;
    default:
      return null;
  }
}
""",
    ("refined", "typescript"): """type Email = { tag: "Email"; value: string };

export function parseEmail(raw: string): Email | null {
  const value = raw.trim().toLowerCase();
  return value.length === 0 ? null : { tag: "Email", value };
}

export function emailToWire(email: Email): string {
  return email.value;
}
""",
    ("pullback", "typescript"): """type Customer = { accountId: string; name: string };
type Subscription = { accountId: string; plan: string };

type CustomerSubscription = {
  customer: Customer;
  subscription: Subscription;
};

export function decodeCustomerSubscription(
  customer: Customer,
  subscription: Subscription,
): CustomerSubscription | null {
  return customer.accountId === subscription.accountId
    ? { customer, subscription }
    : null;
}
""",
    ("free", "typescript"): """type LegacyRule = {
  op: "all" | "field_eq";
  field?: string;
  value?: string;
  children?: LegacyRule[];
};

type Rule =
  | { tag: "All"; rules: Rule[] }
  | { tag: "FieldEq"; field: string; value: string };

export function decodeRule(input: LegacyRule): Rule | null {
  switch (input.op) {
    case "all":
      return Array.isArray(input.children)
        ? { tag: "All", rules: input.children.map(decodeRule).filter((x): x is Rule => x != null) }
        : null;
    case "field_eq":
      return typeof input.field === "string" && typeof input.value === "string"
        ? { tag: "FieldEq", field: input.field, value: input.value }
        : null;
    default:
      return null;
  }
}
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

def email_to_wire(email: Email) -> str:
    return email.value
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

def decode_doc_state(row: dict[str, object]) -> DocState:
    status = row.get("status")
    if status == "draft" and row.get("approvedBy") is None:
        return Draft()
    if status == "approved" and isinstance(row.get("approvedBy"), str):
        return Approved(approved_by=row["approvedBy"])
    raise ValueError(f"invalid legacy row: {row!r}")
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

def decode_customer_subscription(customer: Customer, subscription: Subscription) -> CustomerSubscription:
    if customer.account_id != subscription.account_id:
        raise ValueError("account mismatch")
    return CustomerSubscription(customer=customer, subscription=subscription)
""",
    ("coproduct", "go"): """type LegacyDocumentRow struct {
    Status         string
    ApprovedBy     *string
    PublishedAt    *string
    ArchivedReason *string
}

type DocState interface{ isDocState() }

type Draft struct{}
func (Draft) isDocState() {}

type Approved struct{ ApprovedBy string }
func (Approved) isDocState() {}

func DecodeDocState(row LegacyDocumentRow) (DocState, error) {
    switch row.Status {
    case "draft":
        if row.ApprovedBy == nil && row.PublishedAt == nil && row.ArchivedReason == nil {
            return Draft{}, nil
        }
    case "approved":
        if row.ApprovedBy != nil && row.PublishedAt == nil && row.ArchivedReason == nil {
            return Approved{ApprovedBy: *row.ApprovedBy}, nil
        }
    }
    return nil, fmt.Errorf("invalid legacy row")
}
""",
    ("refined", "go"): """type Email string

func NewEmail(raw string) (Email, error) {
    value := strings.ToLower(strings.TrimSpace(raw))
    if value == "" {
        return "", fmt.Errorf("empty email")
    }
    return Email(value), nil
}

func (e Email) WireValue() string {
    return string(e)
}
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

    public String toWire() {
        return value;
    }
}
""",
    ("coproduct", "java"): """public record LegacyDocumentRow(
    String status,
    String approvedBy,
    String publishedAt,
    String archivedReason
) {}

public sealed interface DocState permits Draft, Approved {}
public record Draft() implements DocState {}
public record Approved(String approvedBy) implements DocState {}

public final class DocStateAdapter {
    public static DocState decode(LegacyDocumentRow row) {
        if ("draft".equals(row.status()) && row.approvedBy() == null && row.publishedAt() == null && row.archivedReason() == null) {
            return new Draft();
        }
        if ("approved".equals(row.status()) && row.approvedBy() != null && row.publishedAt() == null && row.archivedReason() == null) {
            return new Approved(row.approvedBy());
        }
        throw new IllegalArgumentException("invalid legacy row");
    }
}
""",
    ("coproduct", "kotlin"): """data class LegacyDocumentRow(
    val status: String,
    val approvedBy: String? = null,
    val publishedAt: String? = null,
    val archivedReason: String? = null,
)

sealed interface DocState {
    data object Draft : DocState
    data class Approved(val approvedBy: String) : DocState
}

fun decodeDocState(row: LegacyDocumentRow): DocState =
    when {
        row.status == "draft" && row.approvedBy == null && row.publishedAt == null && row.archivedReason == null ->
            DocState.Draft
        row.status == "approved" && row.approvedBy != null && row.publishedAt == null && row.archivedReason == null ->
            DocState.Approved(row.approvedBy)
        else -> error("invalid legacy row")
    }
""",
}

PAIRS = sorted(TEMPLATES)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("construction", nargs="?", help="construction name")
    parser.add_argument("language", nargs="?", help="language name")
    parser.add_argument("--write", help="write output to a file")
    parser.add_argument("--list", action="store_true", help="list supported combinations")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.list:
        for construction, language in PAIRS:
            print(f"{construction}: {language}")
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
