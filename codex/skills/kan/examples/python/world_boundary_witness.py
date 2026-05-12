#!/usr/bin/env python3
"""Tiny world/boundary Kan-lift witness."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PublicCase:
    name: str
    required_status: int

@dataclass(frozen=True)
class InternalRealizer:
    handler: str
    status: int
    audit: str

def required(case: PublicCase) -> int:
    return case.required_status

def realize(case: PublicCase) -> InternalRealizer:
    return InternalRealizer(handler=f"{case.name}Handler", status=case.required_status, audit=f"{case.name}.seen")

def project(realizer: InternalRealizer) -> int:
    return realizer.status

def main() -> None:
    case = PublicCase("AuthorizePayment", 200)
    assert project(realize(case)) == required(case)
    bad = InternalRealizer("AuthorizePaymentHandler", 500, "bad")
    assert project(bad) != required(case)
    print("world_boundary_witness: ok")

if __name__ == "__main__":
    main()
