#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 {haskell|go|typescript}" >&2
  exit 1
}

lang="${1:-}"
if [[ -z "${lang}" ]]; then
  usage
fi

case "${lang}" in
  haskell)
    cat <<'HS'
-- QuickCheck law stub (illustrative)
-- Requires QuickCheck in the target project

prop_monoid_left_id :: (Eq a, Monoid a) => a -> Bool
prop_monoid_left_id x = mempty <> x == x

prop_monoid_right_id :: (Eq a, Monoid a) => a -> Bool
prop_monoid_right_id x = x <> mempty == x

prop_monoid_assoc :: (Eq a, Monoid a) => a -> a -> a -> Bool
prop_monoid_assoc a b c = a <> (b <> c) == (a <> b) <> c
HS
    ;;
  go)
    cat <<'GO'
// testing/quick law stub (illustrative)
// Requires: import "testing/quick"

func monoidLeftID[T comparable](empty T, combine func(T, T) T, x T) bool {
  return combine(empty, x) == x
}

func monoidRightID[T comparable](empty T, combine func(T, T) T, x T) bool {
  return combine(x, empty) == x
}

func monoidAssoc[T comparable](combine func(T, T) T, a, b, c T) bool {
  return combine(a, combine(b, c)) == combine(combine(a, b), c)
}
GO
    ;;
  typescript|ts)
    cat <<'TS'
// fast-check law stub (illustrative)
// Requires: import * as fc from "fast-check"

const monoidLaws = <A>(
  empty: A,
  combine: (a: A, b: A) => A,
  arb: fc.Arbitrary<A>
) => {
  fc.assert(fc.property(arb, a => combine(empty, a) === a));
  fc.assert(fc.property(arb, a => combine(a, empty) === a));
  fc.assert(fc.property(arb, fc.tuple(arb, arb, arb), ([a, b, c]) =>
    combine(a, combine(b, c)) === combine(combine(a, b), c)
  ));
};
TS
    ;;
  *)
    usage
    ;;
esac
