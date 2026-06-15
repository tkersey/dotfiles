# Review Governor Memory

`$negative-ledger` is the Review Governor's memory.

It should answer:

```text
Was this route tried before?
Did it fail?
May it be repeated now?
```

## Required route gate

```yaml
negative_route_gate:
  checked: yes | no
  active_exclusion_match: yes | no
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

## Capture trigger

Create a capture candidate when:

- same cluster recurs after a selected route;
- proof matrix missed a same-family counterexample;
- public/fallback/compatibility/tolerance route was rejected;
- selected normal form failed on current artifact;
- universalist-not-needed was falsified.

## Success metric

The important report field is:

```text
route_changed_by_exclusion
```

not the number of negative-ledger mentions.
