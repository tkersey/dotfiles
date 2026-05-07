#!/usr/bin/env python3
"""Codensity-shaped difference-list witness in Python.

Python does not enforce rank-n parametricity; this is an operational analogy for
continuation/difference-list optimization, not a formal proof.
"""
from __future__ import annotations
from time import perf_counter

class DList:
    def __init__(self, run):
        self.run = run

    @staticmethod
    def empty():
        return DList(lambda xs: xs)

    @staticmethod
    def singleton(x):
        return DList(lambda xs: [x] + xs)

    def append(self, other: "DList") -> "DList":
        return DList(lambda xs: self.run(other.run(xs)))

    def to_list(self):
        return self.run([])

def direct(n: int):
    xs = []
    for i in range(n):
        xs = xs + [i]
    return xs

def codensity_like(n: int):
    xs = DList.empty()
    for i in range(n):
        xs = xs.append(DList.singleton(i))
    return xs.to_list()

def main():
    n = 200
    t0 = perf_counter(); a = direct(n); t1 = perf_counter()
    b = codensity_like(n); t2 = perf_counter()
    assert a == b
    print(f"semantic equality: {a[:3]} ... {a[-3:]}")
    print(f"direct seconds: {t1 - t0:.6f}")
    print(f"codensity-like seconds: {t2 - t1:.6f}")
    print("Interpret benchmark cautiously; Python list/function overhead is workload-specific.")

if __name__ == "__main__":
    main()
