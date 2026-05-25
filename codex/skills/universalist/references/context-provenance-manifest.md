# Context Provenance Manifest

A Context Provenance Manifest records how a published context was produced.

## Fields

```text
context_instance_id
source_snapshot_ids
schema_version
mapping_names
query_names
constraint_check_results
input_record_ids / document_ids / tool_call_ids
derivation_steps
publication_timestamp
freshness_requirements
renderer_version
semantic_consumer
rendered_packet_hash
```

## Law

Every evidence-bearing claim in published context has a provenance path to source data, assumption, missingness marker, or contradiction marker.

## Review questions

- Why did the consumer see this fact?
- Which source records produced it?
- Which mapping/query generated it?
- Which schema version was used?
- Which constraints were checked?
- Which rendering was consumed?
