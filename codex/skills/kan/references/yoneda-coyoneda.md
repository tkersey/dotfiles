# Yoneda and Coyoneda

## Yoneda

Use when boundary artifacts are observations.

```text
data Observation = ...
runObservation : Observation -> Subject -> Result
```

Law:

```text
runObservation(obs, repack(subject)) == runObservation(obs, subject)
```

## Coyoneda

Use when boundary artifacts are generated payloads plus deferred maps.

```text
data Generated = { payload, path }
lowerGenerated : Generated -> Target
```

Law:

```text
lowerGenerated(payload,path) == directInterpret(path,payload)
```

## With Kan lifts

Use Yoneda for public observations in `C0`; use Coyoneda for candidate realizers in `B`; defunctionalize both when they cross boundaries.
