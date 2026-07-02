# Example: shopping cart

## Domain

Users add items, remove items, apply coupons, view totals, and check out.

## Carriers

```text
Cart
LineItem
Coupon
CartView
PriceBreakdown
```

## Operations

```text
emptyCart   : Cart
addItem     : Cart × ItemId × Quantity -> Cart
removeItem  : Cart × ItemId × Quantity -> Cart
setQuantity : Cart × ItemId × Quantity -> Cart
applyCoupon : Cart × CouponCode -> Cart
mergeCart   : Cart × Cart -> Cart
observeCart : Cart -> CartView
priceCart   : Cart × PricingContext -> PriceBreakdown
checkout    : Cart × CheckoutCommand -> Result[OrderCreated]
```

## Observation-relative laws

- `mergeCart(emptyCart, c) = c` under item/totals observation.
- `mergeCart(a,b) = mergeCart(b,a)` only if line order and audit order are not observed.
- `addItem(addItem(c,item,q1), item, q2) = addItem(c,item,q1+q2)` only if inventory/promotion/audit intermediates are not observed.
- `checkout(commandId, cart)` repeated should produce one durable order effect when retries are possible.

## Architecture implications

- use explicit empty cart;
- normalize line quantities;
- do not claim commutativity if order/audit is observable;
- checkout needs idempotency key and durable uniqueness check.
