# Claim Binding Playbook

Use for fingerprints, receipts, certificates, proof records, refs, cursors, manifests, checkpoints, replay records, attestations, and pass/fail APIs.

## Objective

A proof-like value is valid only when it binds the complete transitive set of facts downstream code trusts.

```text
claim
-> authoritative source
-> canonical encoding
-> digest/signature/identity
-> validation predicate
-> downstream authority
```

## Contract

```yaml
claim_binding:
  claim_id:
  claim:
  authoritative_owner:
  authoritative_sources: []
  canonical_encoding:
  bound_fields: []
  trusted_but_unbound_fields: []
  caller_controlled_fields: []
  derivation_steps: []
  public_predicate:
  strongest_internal_predicate:
  predicate_parity: pass | fail
  downstream_authorities: []
  forgery_tests: []
  evidence_refs: []
```

## Required questions

- Which exact bytes or facts are authoritative?
- Which fields are reconstructed versus caller supplied?
- Can a claimed field change without changing the fingerprint?
- Can an empty/minimal/zero evidence list still pass?
- Can the caller supply both object and alleged fingerprint?
- Does order, duplication, omission, or defaulting change meaning?
- Does public `passed()`/`verify()` call the strongest predicate?
- Does the proof bind version, domain, owner, epoch, and target object?
- Does a ref bind object identity or merely a length/shape?

## Canonical encoding

State:

```text
field order
length encoding
endianness
domain separator
version
optional/absent encoding
collection ordering
duplicate policy
normalization
```

Avoid ad hoc concatenation with ambiguous boundaries.

## Forgery matrix

At minimum:

1. change each claimed field independently;
2. omit each optional-looking field;
3. replace evidence with zero/minimal values;
4. reorder collections;
5. duplicate one entry;
6. replace one ref with an equal-length foreign ref;
7. use a caller-supplied digest unrelated to the source;
8. change authority/domain/version/epoch metadata;
9. change the underlying object after proof creation;
10. compare public predicate with strongest internal predicate.

## Ownership

The component that owns the authoritative bytes should generally derive the proof.

A consumer should not “validate” a caller-authored proof by comparing it against caller-authored metadata.

## Ref and evidence closure

For semantic refs, prove that each ref resolves to an owned object and that the proof binds the resolved object facts actually trusted.

A count or non-empty list is not object closure.

## Failure routing

A failed claim-binding test usually means:

```text
wrong owner
incomplete canonical encoding
weak public predicate
caller-controlled authority
stale proof epoch
```

Do not add a downstream tolerance check before resolving the owner/binding defect.
