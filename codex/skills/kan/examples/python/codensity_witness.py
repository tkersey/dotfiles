#!/usr/bin/env python3
"""Small codensity/CPS-style witness using difference-list intuition."""
from typing import Callable, TypeVar, Generic

A = TypeVar("A")

class DList(Generic[A]):
    def __init__(self, run: Callable[[list[A]], list[A]]):
        self.run = run
    def append(self, xs: list[A]) -> "DList[A]":
        return DList(lambda tail: self.run(xs + tail))
    def lower(self) -> list[A]:
        return self.run([])


def main() -> None:
    d = DList[int](lambda xs: xs).append([1]).append([2, 3])
    assert d.lower() == [1, 2, 3]
    print("codensity_witness: ok")

if __name__ == "__main__":
    main()
