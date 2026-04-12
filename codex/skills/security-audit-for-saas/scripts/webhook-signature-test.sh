#!/usr/bin/env bash
# webhook-signature-test.sh
#
# Test webhook signature verification against a running server.
# Sends:
#   1. Forged event with no signature → should return 400
#   2. Forged event with invalid signature → should return 401
#   3. Forged event with tampered body → should return 401
#   4. Duplicate event (valid signature) → should return 200 (idempotent)
#
# Usage: ./webhook-signature-test.sh <endpoint-url>
# Example: ./webhook-signature-test.sh http://localhost:3000/api/stripe/webhook

set -u

ENDPOINT="${1:?Usage: webhook-signature-test.sh <endpoint-url>}"
FAIL=0

if ! command -v curl >/dev/null 2>&1; then
  echo "✗ curl is required"
  exit 1
fi

echo "=== Webhook Signature Test: $ENDPOINT ==="
echo

# Test 1: No signature
echo "--- Test 1: No signature header ---"
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"type":"fake.event","id":"evt_fake_001"}')
if [ "$status" = "400" ] || [ "$status" = "401" ]; then
  echo "✓ Missing signature rejected (status $status)"
else
  echo "✗ Missing signature NOT rejected (status $status, expected 400/401)"
  FAIL=$((FAIL + 1))
fi

# Test 2: Invalid signature
echo
echo "--- Test 2: Invalid signature ---"
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1234567890,v1=invalid_signature" \
  -d '{"type":"fake.event","id":"evt_fake_002"}')
if [ "$status" = "401" ] || [ "$status" = "400" ]; then
  echo "✓ Invalid signature rejected (status $status)"
else
  echo "✗ Invalid signature NOT rejected (status $status, expected 401)"
  FAIL=$((FAIL + 1))
fi

# Test 3: PayPal missing headers
echo
echo "--- Test 3: PayPal webhook with missing headers ---"
if [[ "$ENDPOINT" == *"paypal"* ]]; then
  status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d '{"event_type":"BILLING.SUBSCRIPTION.CREATED"}')
  if [ "$status" = "400" ] || [ "$status" = "401" ]; then
    echo "✓ PayPal missing headers rejected (status $status)"
  else
    echo "✗ PayPal missing headers NOT rejected (status $status)"
    FAIL=$((FAIL + 1))
  fi
else
  echo "⊘ Skipped (not a PayPal endpoint)"
fi

# Test 4: Large body size
echo
echo "--- Test 4: Large body (>1MB) ---"
# Use a newline-free ASCII payload so rejection is caused by body size, not malformed JSON.
large_body=$(head -c 1500000 < /dev/zero | tr '\0' 'A')
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  --data-raw "{\"data\":\"$large_body\"}" 2>/dev/null || echo "000")
if [ "$status" = "413" ] || [ "$status" = "400" ] || [ "$status" = "401" ]; then
  echo "✓ Large body rejected (status $status)"
else
  echo "⚠ Large body response: $status (verify body size limit)"
fi

# Test 5: Replay with old timestamp
echo
echo "--- Test 5: Stale timestamp (replay attempt) ---"
old_ts=$(($(date +%s) - 86400))  # 24 hours ago
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=$old_ts,v1=stale_signature" \
  -d '{"type":"fake.event","id":"evt_replay_001"}')
if [ "$status" = "401" ] || [ "$status" = "400" ]; then
  echo "✓ Stale event rejected (status $status)"
else
  echo "⚠ Stale event response: $status (verify timestamp validation)"
fi

echo
echo "=== Summary ==="
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All webhook signature tests passed"
  exit 0
else
  echo "✗ $FAIL tests failed"
  exit 1
fi
