#!/usr/bin/env python3
"""Tiny finite Kan-extension intuition: Lan as generated quotient, Ran as coherent observation family."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Generated:
    source: str
    path: str
    payload: str


def eta(source: str, payload: str) -> Generated:
    return Generated(source, "id", payload)


def lan_map(g: str, x: Generated) -> Generated:
    return Generated(x.source, f"{g}∘{x.path}", x.payload)


def ran_family(observations: dict[str, str]) -> dict[str, str]:
    # In a real Ran, this would validate all equations.
    return dict(observations)


def epsilon(family: dict[str, str], key: str) -> str:
    return family[key]


def main() -> None:
    old = eta("core-node", "meaning")
    assert lan_map("embed", old).payload == "meaning"
    fam = ran_family({"legacy-view": "ok", "legacy-report": "ok"})
    assert epsilon(fam, "legacy-view") == "ok"
    print("finite_kan: ok")

if __name__ == "__main__":
    main()
