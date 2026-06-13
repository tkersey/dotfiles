# Abstraction Rent

Any new surface must pay rent.

## Surfaces that owe rent

- helper
- wrapper
- adapter
- fallback
- flag
- branch
- state variant
- public symbol
- compatibility path
- parser tolerance
- catch-and-continue path
- default/coercion behavior
- new abstraction

## Rent is paid by one or more

- retiring existing surface;
- preventing named future patches;
- making illegal state uninhabitable at the owner;
- localizing unavoidable external obligation;
- replacing multiple local repairs with one canonical owner;
- explicit user/upstream acceptance of expansion.

## Rent packet

```yaml
abstraction_rent:
  required: yes | no
  added_surface:
  owner:
  why_existing_owner_cannot_absorb:
  counterexamples_killed: []
  surfaces_retired: []
  future_patches_prevented: []
  deletion_condition:
  proof_required: []
  rent_status: paid | unpaid | not-applicable
```

Unpaid rent blocks `add-new-surface`.
