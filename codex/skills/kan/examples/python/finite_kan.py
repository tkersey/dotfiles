#!/usr/bin/env python3
"""Tiny finite Set-valued Kan extension playground.

It computes pointwise Lan/Ran for finite categories represented by objects,
arrows, composition, and functors. This is for witnesses, tests, and intuition.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Tuple

@dataclass(frozen=True)
class Arrow:
    name: str
    src: str
    dst: str

class FiniteCategory:
    def __init__(self, objects: Iterable[str], arrows: Iterable[Arrow], identities: Dict[str, str], compose: Dict[Tuple[str, str], str]):
        self.objects = list(objects)
        self.arrows = {a.name: a for a in arrows}
        self.identities = identities
        self.compose_table = compose

    def hom(self, src: str, dst: str) -> List[str]:
        return [n for n, a in self.arrows.items() if a.src == src and a.dst == dst]

    def compose(self, g: str, f: str) -> str:
        """g ∘ f."""
        return self.compose_table[(g, f)]

class Functor:
    def __init__(self, obj: Dict[str, Any], arr: Dict[str, Any]):
        self.obj = obj
        self.arr = arr

class UnionFind:
    def __init__(self):
        self.parent = {}

    def add(self, x):
        self.parent.setdefault(x, x)

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.add(a); self.add(b)
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra

    def classes(self):
        out = {}
        for x in list(self.parent):
            out.setdefault(self.find(x), []).append(x)
        return list(out.values())

def pointwise_lan(C: FiniteCategory, D: FiniteCategory, K: Functor, F: Functor, d: str):
    """Return equivalence classes representing (Lan_K F)(d)."""
    comma_objects = []
    for c in C.objects:
        for u in D.hom(K.obj[c], d):
            comma_objects.append((c, u))

    uf = UnionFind()
    for c, u in comma_objects:
        for x in F.obj[c]:
            uf.add((c, u, x))

    for c, u in comma_objects:
        for cp, up in comma_objects:
            for f in C.hom(c, cp):
                # morphism exists if up ∘ Kf = u
                if D.compose(up, K.arr[f]) == u:
                    fn: Callable[[Any], Any] = F.arr[f]
                    for x in F.obj[c]:
                        uf.union((c, u, x), (cp, up, fn(x)))
    return uf.classes()

def pointwise_ran(C: FiniteCategory, D: FiniteCategory, K: Functor, F: Functor, d: str):
    """Return coherent families representing (Ran_K F)(d)."""
    comma_objects = []
    for c in C.objects:
        for u in D.hom(d, K.obj[c]):
            comma_objects.append((c, u))

    if not comma_objects:
        return [dict()]

    candidates = []
    set_lists = [list(F.obj[c]) for c, _ in comma_objects]
    for values in product(*set_lists):
        fam = dict(zip(comma_objects, values))
        ok = True
        for c, u in comma_objects:
            for cp, up in comma_objects:
                for f in C.hom(c, cp):
                    # morphism exists if Kf ∘ u = up
                    if D.compose(K.arr[f], u) == up:
                        fn: Callable[[Any], Any] = F.arr[f]
                        if fn(fam[(c, u)]) != fam[(cp, up)]:
                            ok = False
        if ok:
            candidates.append(fam)
    return candidates

def demo():
    C = FiniteCategory(
        objects=["A", "B"],
        arrows=[Arrow("idA", "A", "A"), Arrow("idB", "B", "B"), Arrow("f", "A", "B")],
        identities={"A": "idA", "B": "idB"},
        compose={("idA", "idA"): "idA", ("idB", "idB"): "idB", ("f", "idA"): "f", ("idB", "f"): "f"},
    )
    D = FiniteCategory(
        objects=["A", "B", "X"],
        arrows=[Arrow("idA", "A", "A"), Arrow("idB", "B", "B"), Arrow("idX", "X", "X"), Arrow("f", "A", "B"), Arrow("g", "B", "X"), Arrow("gf", "A", "X")],
        identities={"A": "idA", "B": "idB", "X": "idX"},
        compose={
            ("idA", "idA"): "idA", ("idB", "idB"): "idB", ("idX", "idX"): "idX",
            ("f", "idA"): "f", ("idB", "f"): "f", ("g", "idB"): "g", ("idX", "g"): "g",
            ("gf", "idA"): "gf", ("idX", "gf"): "gf", ("g", "f"): "gf",
        },
    )
    K = Functor(obj={"A": "A", "B": "B"}, arr={"idA": "idA", "idB": "idB", "f": "f"})
    F = Functor(obj={"A": {"a1", "a2"}, "B": {"b1", "b2"}}, arr={"idA": lambda x: x, "idB": lambda x: x, "f": lambda x: {"a1": "b1", "a2": "b2"}[x]})
    print("Lan at X:")
    for cls in pointwise_lan(C, D, K, F, "X"):
        print(" ", cls)
    print("Ran at A:")
    for fam in pointwise_ran(C, D, K, F, "A"):
        print(" ", fam)

if __name__ == "__main__":
    demo()
