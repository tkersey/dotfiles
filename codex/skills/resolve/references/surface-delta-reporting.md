# Surface Delta Reporting

Surface movement must be measured, not inferred from confidence.

## Required summary

For any run that changes files, report:

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

## Calls

- `smaller`: production surface reduced or duplicate/shadow surface retired with proof.
- `same`: production surface roughly stable and no new public/helper/wrapper/flag/fallback surface was introduced.
- `larger-with-warrant`: production surface grew, but the growth is owned, proof-backed, and blocks future local patches or retires surface.
- `larger-without-warrant`: production surface grew without enough owner/proof/retirement warrant.
- `unknown`: counts are unavailable.

`larger-without-warrant` blocks resolved completion unless revised, warranted, or explicitly accepted by the user.
