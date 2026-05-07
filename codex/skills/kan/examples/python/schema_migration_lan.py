#!/usr/bin/env python3
"""Toy schema-migration-as-Lan sketch.

Two source tables merge into a target Person view by canonical key. The
quotient/canonicalization is the engineering part corresponding to colimit identification.
"""
from collections import defaultdict

customers = [
    {"customer_id": "c1", "email": "a@example.com", "name": "Ada"},
    {"customer_id": "c2", "email": "b@example.com", "name": "Bea"},
]
contacts = [
    {"contact_id": "k1", "email": "a@example.com", "phone": "111"},
    {"contact_id": "k2", "email": "c@example.com", "phone": "333"},
]

def sigma_lan_person(customers, contacts):
    by_email = defaultdict(dict)
    for row in customers:
        by_email[row["email"]].update({"email": row["email"], "name": row["name"], "source_customer": row["customer_id"]})
    for row in contacts:
        by_email[row["email"]].update({"email": row["email"], "phone": row["phone"], "source_contact": row["contact_id"]})
    return list(by_email.values())

def delta_restrict_persons(persons):
    return [{"email": p["email"], "name": p.get("name")} for p in persons if "name" in p]

if __name__ == "__main__":
    persons = sigma_lan_person(customers, contacts)
    assert {p["email"] for p in persons} == {"a@example.com", "b@example.com", "c@example.com"}
    assert {r["email"] for r in delta_restrict_persons(persons)} == {"a@example.com", "b@example.com"}
    print(persons)
