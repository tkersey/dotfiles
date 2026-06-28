# Intent-Closed Review Lanes

CAS carries review transport; the caller owns review-batch authority.

Every review request should include:

```text
campaign ID
review mode
AC-v2 contract/horizon fingerprint
batch ID
RAP-v1 aperture ID
artifact base/head
accepted law/owner/transition/proof refs
known counterexample class refs
excluded scope
```

## Discovery

One broad sensing review may run before kernel acceptance.

Output is review claims requiring CEX-v1 adjudication.

## Kernel review

Review AC/CEB/MBK/RC, not implementation.

## Conformance

Prompt:

```text
Attempt to falsify only the named laws at the named owners/transitions.
Return a minimal trace or clean.
Do not conduct general feature discovery.
Do not prescribe patches.
```

Generic whole-diff conformance lanes are invalid.

## Terminal holdout

One broad final review is allowed.

Its output may:

```text
return to kernel
return to contract
capture follow-up
or remain clean
```

It never directly authorizes mutation.

CAS receipts should preserve mode, horizon, batch, aperture, and tuple metadata so downstream audit tools can validate lineage.
