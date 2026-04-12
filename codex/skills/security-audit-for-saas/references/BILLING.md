# Payment & Billing Security Checklist

Deep checklist for auditing SaaS payment flows. Every item comes from a real vulnerability found in production.

---

## Webhook Signature Verification

### Stripe
- [ ] `stripe.webhooks.constructEvent(rawBody, sig, secret)` used (not manual HMAC)
- [ ] Raw body preserved (not parsed JSON) for signature verification
- [ ] Missing/invalid signatures return 400/401 and log as abuse signal
- [ ] Webhook endpoint exempted from CSRF protection
- [ ] `STRIPE_WEBHOOK_SECRET` is environment-specific (test vs live)

### PayPal
- [ ] All 5 required headers validated: `paypal-transmission-id`, `paypal-transmission-time`, `paypal-transmission-sig`, `paypal-cert-url`, `paypal-auth-algo`
- [ ] Verification done via PayPal API (`/v1/notifications/verify-webhook-signature`), not locally
- [ ] PayPal API timeout set (10s) with proper error handling
- [ ] Fallback behavior on PayPal API outage: reject + rely on PayPal retries + reconciliation cron

### General
- [ ] Both providers return 200 even on processing errors (prevents retry storms)
- [ ] Event ID deduplication via `INSERT ... ON CONFLICT DO NOTHING` on `(provider, eventId)`
- [ ] Timestamp validation rejects events older than tolerance window
- [ ] Failed signature attempts tracked as abuse signals

---

## Checkout Flow Race Conditions (TOCTOU)

This is the #1 billing vulnerability category. 10 distinct patterns found across projects.

### Individual Checkout
- [ ] `SELECT ... FOR UPDATE` on user record before creating checkout session
- [ ] Pending checkout state saved with TTL (e.g., 30 min)
- [ ] Unique constraint on (userId, provider) prevents double-subscription
- [ ] Idempotency key derived from user+timestamp (not random UUID)

### Team Checkout
- [ ] Seat count read inside transaction with advisory lock
- [ ] `maxSeats` enforcement on member addition (not just at checkout)
- [ ] Org subscription state locked before creating checkout session
- [ ] THREE checks in PayPal team checkout (all must be inside transaction):
  1. Org has no existing subscription
  2. Org has no pending checkout
  3. Org is not in cancellation grace period

### Webhook Processing
- [ ] Idempotency check is INSIDE transaction scope (not outside)
- [ ] Optimistic concurrency via timestamp: `WHERE updatedAt = $previousValue`
- [ ] Subscription status updates use deterministic state machine

---

## Subscription Hijacking Prevention

### PayPal `custom_id` Attack
PayPal's `custom_id` is attacker-controlled. An attacker can set a victim's userId.

**Required validation chain (implement all):**
1. User exists in database
2. User has no PayPal `customerId` (first-time linking OK)
3. OR user's existing `customerId` matches the webhook's `payerId`
4. Mismatches: log security event + reject update

### Stripe Metadata Attack
Team checkout completion must verify that `individualSub.userId` matches the org owner (`session.client_reference_id`).

**Required validation:**
- Cross-check that the individual subscription being cancelled belongs to the authenticated user who initiated the checkout

---

## Price Integrity

- [ ] All prices come from server-side constants or Stripe/PayPal plan configuration
- [ ] No client-submitted `amount`, `price`, or `unit_amount` values accepted
- [ ] Plan IDs validated against allowed set before creating checkout sessions
- [ ] Pro-rata calculations use actual billing period length (not hardcoded 30-day month)
- [ ] Coupon/promo codes validated server-side with expiry and usage limit checks

---

## Stripe SDK Type Safety

Stripe objects can return either string IDs or expanded objects depending on `expand` parameters.

```typescript
// BAD - crashes on expanded objects
const customerId = subscription.customer as string;

// GOOD - handles both cases
const customerId = typeof subscription.customer === 'string'
  ? subscription.customer
  : subscription.customer.id;
```

**Audit all `as string` casts on Stripe objects** in webhook handlers and API routes.

---

## Subscription Status Mapping

- [ ] `mapStripeStatus()` logs errors on unknown statuses (not silent return of "none")
- [ ] `updateSubscriptionStatus()` rejects writes of "none" to prevent data corruption
- [ ] PayPal status mapping covers all lifecycle events including suspension and payment denial
- [ ] PayPal `payer_id` typed as optional (PayPal sometimes omits it)
- [ ] PayPal suspension handler has fallback when `billing_info.next_billing_time` is missing

---

## Post-Checkout State Management

- [ ] Pending checkout fields cleared on completion: `pendingCheckoutProvider`, `pendingCheckoutSessionId`, `pendingCheckoutUrl`, `pendingCheckoutExpiresAt`
- [ ] Cache invalidation is synchronous (not in `after()` callback which is unreliable in serverless)
- [ ] Cache event system includes subscription-related events: `subscription:activated`, `subscription:cancelled`, `subscription:status_changed`
- [ ] Dashboard cache TTL (e.g., 5 min) doesn't cause entitlement gaps after purchase

---

## Seat Billing

- [ ] Seat count read inside transaction with advisory lock before creating checkout
- [ ] `maxSeats` enforced when adding members to org (not just at checkout time)
- [ ] Concurrent member additions can't cause under-billing
- [ ] Seat reduction validated against active member count

---

## Dunning & Recovery

- [ ] Dunning queries use cursor-based pagination (not `LIMIT 5000` with sequential processing)
- [ ] `maxDuration` budget accounts for processing time per subscription
- [ ] DLQ has exponential backoff and max retry count
- [ ] Reconciliation cron acts as safety net for missed webhooks
- [ ] Team reactivation path exists in payment-denied handler

---

## Dual-Path Credit Systems (PayPal Orders + IPN)

For credit-based (non-subscription) payment flows:
- [ ] Transaction ID deduplication prevents double-crediting from capture endpoint + IPN
- [ ] Unique constraint on `(transactionId, source)` in credit transactions table
- [ ] `custom_id` embeds userId + credits + promoCode, validated against session on capture
- [ ] IPN validation properly echoes all fields back to `ipnpb.paypal.com`
- [ ] Atomic credit granting via database transaction
