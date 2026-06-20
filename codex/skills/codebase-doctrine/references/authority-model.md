# Authority and State Model

## Authority questions

For each important state/evidence object:

```text
Who creates it?
Who may mutate it?
Who validates it?
Who certifies or publishes it?
Who consumes it?
Who may transfer authority?
Who retires or invalidates it?
```

## Authority record

```yaml
authority:
  authority_id:
  owner:
  owned_state: []
  creation_paths: []
  transition_paths: []
  readers: []
  certificates_or_witnesses: []
  enforcement_boundary:
  authority_transfers: []
  shadow_owners: []
  late_validations: []
  evidence_refs: []
```

## Evidence priority

1. mutation/commit paths;
2. constructors and transition functions;
3. certificate/evidence issuance;
4. transaction and rollback boundaries;
5. validation paths;
6. read-only consumers;
7. naming/docs.

## Smells

```text
several modules can publish the same evidence
reader repairs invalid producer state
validation repeated downstream
shadow cache becomes truth owner
authority transfer has no explicit token/receipt
rollback does not restore authority state
public bypass around canonical owner
```

## Boundary rule

A boundary recommendation should name:

```text
accepted input
rejected input
authority before
authority after
state/evidence transferred
proof witness
```
