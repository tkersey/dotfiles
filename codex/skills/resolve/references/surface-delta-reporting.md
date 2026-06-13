# Surface Delta Reporting

For any run that changes files, record measured surface movement.

```yaml
surface_delta_summary:
  production_insertions:
  production_deletions:
  production_net:
  test_insertions:
  test_deletions:
  test_net:
  generated_insertions:
  generated_deletions:
  generated_net:
  helpers_wrappers_adapters_added:
  public_symbols_added:
  flags_fallbacks_compat_paths_added:
  duplicate_or_shadow_surfaces_retired:
  surface_delta_call: smaller | same | larger-with-warrant | larger-without-warrant | unknown
```

`larger-without-warrant` blocks resolved completion unless revised, warranted, or explicitly accepted by the user.
