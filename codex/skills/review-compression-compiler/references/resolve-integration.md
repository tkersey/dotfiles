# Resolve Integration

`$resolve` should trigger `$review-compression-compiler` when:

```text
same_cluster_findings >= 2
OR same cluster reappears after selected normal form
OR selected route would add production surface
OR surface_delta_call would be larger-with-warrant or larger-without-warrant
OR review findings are accumulating as address routes
OR mutation-capable item lacks structured abstraction receipt
```

`$resolve` consumes:

```yaml
review_compression_packet.selected_normal_form
review_compression_packet.implementation_handoff
review_compression_packet.proof_matrix
review_compression_packet.closure_rule
```

`$resolve` then passes the implementation handoff to `$fixed-point-driver`.

No review finding should go directly from `address` to `apply_patch`.
