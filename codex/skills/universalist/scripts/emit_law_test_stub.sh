#!/usr/bin/env bash
set -euo pipefail
lang="${1:-typescript}"
case "$lang" in
  haskell|hs)
    cat <<'EOF'
-- Law stub
-- prop_roundtrip x = decode (encode x) == x
EOF
    ;;
  go)
    cat <<'EOF'
// Law stub
// func TestRoundTrip(t *testing.T) { /* encode/decode */ }
EOF
    ;;
  python|py)
    cat <<'EOF'
# Law stub
def test_round_trip():
    assert encode(decode(fixture)) == fixture
EOF
    ;;
  *)
    cat <<'EOF'
// Law stub
it("round-trips through the trusted boundary", () => {
  expect(encode(decode(fixture))).toEqual(fixture);
});
EOF
    ;;
esac
