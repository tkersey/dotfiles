#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: emit_law_test_stub.sh {haskell|go|typescript}

Print illustrative algebra-law stubs. Verify the repo already supports the
chosen test style before using them directly.
EOF
  exit 1
}

lang="${1:-}"
[[ -n "$lang" ]] || usage

case "$lang" in
  haskell)
    cat <<'HS'
-- QuickCheck law stub (illustrative)
-- Requires QuickCheck in the target project.

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
// Verify the repo already uses testing/quick before adopting this directly.

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
// Verify the repo already uses fast-check before adopting this directly.

import * as fc from "fast-check";

export function assertMonoidLaws<A>(
  empty: A,
  combine: (a: A, b: A) => A,
  arb: fc.Arbitrary<A>,
): void {
  fc.assert(fc.property(arb, a => combine(empty, a) === a));
  fc.assert(fc.property(arb, a => combine(a, empty) === a));
  fc.assert(
    fc.property(fc.tuple(arb, arb, arb), ([a, b, c]) =>
      combine(a, combine(b, c)) === combine(combine(a, b), c),
    ),
  );
}
TS
    ;;
  *)
    usage
    ;;
esac
