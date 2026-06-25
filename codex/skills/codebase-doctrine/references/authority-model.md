# Authority and State Model

For important state and evidence, ask who may:

```text
create
mutate
validate
certify or publish
consume
transfer authority
roll back
retire or invalidate
```

```yaml
authority:
  authority_id:
  doctrine_status:
  normative_authority:
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
  current_evidence_refs: []
  target_authority_refs: []
  gap_statement:
  evidence_refs: []
```

Evidence priority:

```text
mutation and publication
constructors and canonical transitions
certificate issuance
transaction and rollback
validation
read-only consumption
names and docs
```

A boundary record must name accepted and rejected input, authority before and
after, transferred state/evidence, and proof.
