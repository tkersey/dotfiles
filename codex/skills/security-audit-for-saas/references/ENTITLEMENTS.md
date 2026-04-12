# Entitlement Enforcement Checklist

Ensuring subscription status always reflects reality and paid features are properly gated.

---

## Server Action Premium Gating

Every server action that provides premium functionality must check the user's subscription tier.

### Pattern (Vulnerable)
```typescript
// packs/new/actions.ts -- NO premium check
export async function createPack(formData: FormData) {
  const user = await requireAuth();
  // Free users can create unlimited packs, bypassing paywall
  const title = formData.get("title") as string; // Also: unsafe cast
  await db.insert(packs).values({ title, userId: user.id });
}
```

### Pattern (Fixed)
```typescript
export async function createPack(formData: FormData) {
  const user = await requireAuth();
  await requireSubscription(user.id); // Premium check BEFORE operation
  const parsed = createPackSchema.safeParse(Object.fromEntries(formData)); // Zod validation
  if (!parsed.success) throw new Error('Invalid input');
  await db.insert(packs).values({ ...parsed.data, userId: user.id });
}
```

### Audit All Server Actions For
- [ ] Premium tier verification before premium operations
- [ ] Zod schema validation on all FormData (no `as string` casts)
- [ ] Max-length checks on string fields
- [ ] URL validation on URL fields
- [ ] Enum validation for visibility/status fields
- [ ] Transactional multi-step writes (e.g., delete + decrement in same transaction)
- [ ] Audit log records actual values written (not input values that may differ)

---

## Subscription Status Endpoint

The `/api/subscription/status` endpoint must handle edge cases:

- [ ] Org-only users (active via org but no personal subscription): return `subscription: null`, not misleading `{ provider: null, current_period_end: null }`
- [ ] Check `provider !== null` in addition to `status !== "none"` before building subscriptionDetails
- [ ] Grace period correctly calculated from actual `currentPeriodEnd`
- [ ] Suspended users denied even if admin flag is set

---

## Subscription Status State Machine

Valid transitions must be enforced:

```
none -> active (checkout completed)
active -> past_due (payment failed)
active -> canceled (user cancelled, still in grace period)
past_due -> active (payment retry succeeded)
past_due -> canceled (max retries exceeded)
canceled -> none (grace period expired)
none -> active (re-subscription)
```

### Status Mapping Safety
- [ ] `mapStripeStatus()` logs error on unknown status (not silent `"none"` return)
- [ ] `updateSubscriptionStatus()` refuses to write `"none"` status to subscriptions table
- [ ] PayPal status mapping handles all lifecycle events including `BILLING.SUBSCRIPTION.SUSPENDED` and `PAYMENT.SALE.DENIED`
- [ ] Unknown PayPal event types logged as warnings

---

## Cache & Entitlement Consistency

### The Cache Staleness Problem
After subscription purchase, the webhook updates DB to "active", but cached dashboard data may still show "not subscribed" for up to the cache TTL.

**Required mitigations:**
- [ ] Cache invalidation is synchronous in webhook handler (not in `after()` callback)
- [ ] Cache event types include subscription events: `subscription:activated`, `subscription:cancelled`, `subscription:status_changed`
- [ ] Entitlement checks hit DB directly (not cache) for authorization decisions
- [ ] Cache TTL is documented and acceptable for UX (e.g., 5 min max)

### Authorization Must Be Fail-Closed
```typescript
// CORRECT - fail-closed pattern
try {
  const canAccess = await canAccessPremiumContent(userId);
  if (!canAccess) return deny();
} catch {
  return deny(); // DB error = denied (safe default)
}
```

- [ ] `requireSubscription` falls back to denial on any error
- [ ] DB outage = denied access, never granted
- [ ] Suspended users denied regardless of other flags

---

## Grace Period Logic

- [ ] `currentPeriodEnd` is set from provider data, not hardcoded
- [ ] Grace period calculation uses actual period end, not stale/undefined value
- [ ] PayPal suspension handler has fallback when `billing_info.next_billing_time` is missing: use current date + grace period
- [ ] Time-sensitive values (like `now`) captured once at function entry for consistent comparisons
- [ ] Multi-subscription tie-breaking is deterministic (scoring-based, not arbitrary)

---

## Pending Checkout State

- [ ] Pending checkout saved with TTL (e.g., 30 min)
- [ ] Fields cleared after successful completion: `pendingCheckoutProvider`, `pendingCheckoutSessionId`, `pendingCheckoutUrl`, `pendingCheckoutExpiresAt`
- [ ] Stale pending state doesn't block new checkout attempts after TTL
- [ ] Same cleanup applied in both Stripe and PayPal webhook handlers
- [ ] Team checkout completion also clears pending state
