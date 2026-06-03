# Adversarial Parallelism for Fixed-Point Driver

Use adversarial parallelism to drive a branch toward Truth-Owner Normal Form
without turning the run into a slow serial review loop. Parallel adversaries are
read-only challengers. Writes remain single-threaded and warrant-scoped.

## Principle

Every material action in a fixed-point run should have an adversarial response:
validation should be challenged by no-validation and mutate-now alternatives;
mutation should be challenged by delete/reuse/refactor, owner-boundary, proof,
and surface-budget alternatives; closure should be challenged by stale-proof,
open-counterexample, duplicate-owner, and one-change alternatives.

## Safe concurrency boundary

Parallel lanes may inspect code, tests, comments, warrants, ledgers, proof
receipts, negative evidence, and architecture boundaries. They must not edit code,
resolve threads, update snapshots, or draft final PR text. The root coordinator
integrates packets and performs/delegates any mutation in one thread.

## Fixed-point action adversaries

| fixed-point action | adversarial response |
|---|---|
| warrant intake | Is the warrant stale, scoped too broadly, expired, or incompatible with the artifact state? |
| truth-unit extraction | Is this really one invariant, or are there multiple owners/contracts? Is the proposed owner canonical? |
| route selection | Is delete/reuse/refactor better than adding? Is validation-first safer than mutation? Is no-change preserved? |
| implementation | Does the patch exceed warrant scope or surface budget? Does it add duplicate truth surfaces? |
| validation | Does the proof exercise the actual claimed failure mechanism? Is it stale or indirect? |
| de novo review | Are there unlisted counterexamples, illegal inhabitants, or unretired scaffolds? |
| one-change challenge | Is there one remaining material change that should happen before closure? |
| closure handoff | Are proof receipts current? Are all vetoes cleared? Does verification have the right questions? |

## Fanout modes

- `root-equivalent`: root performs the challenge inline for narrow bounded tasks.
- `targeted-parallel`: one or two read-only lanes challenge distinct uncertainty
  classes.
- `expanded-targeted`: three or four lanes for coupled truth units or stale proof.
- `swarm`: five or more lanes for large, contentious, invariant-coupled, or
  likely-to-reopen runs.
- `not-required`: no safe action exists; the row is blocked and the missing
  evidence is named.

## Required ledgers

### Warrant Intake / Parallelism Plan

```md
| warrant id | claim id | permitted action | permitted scope | expiry check | surface budget | adversarial plan | parallelism mode | intake status |
|---|---|---|---|---|---|---|---|---|
```

### Adversarial Action Ledger

```md
| action id | phase | target | challenger lanes | parallelism mode | strongest adversarial finding | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|---|
```

### Surface Delta Receipts

```md
| receipt id | warrant id | patch/pass | production insertions | production deletions | net production loc | public symbols added | helpers added | duplicate paths added | budget status | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|
```

## Closure rule

A fixed-point candidate may not enter verification closure if any material
adversarial row has `veto status: unresolved`, `vetoed`, or `blocked`, unless the
closure packet explicitly marks the item as accepted risk or asks verification to
resolve the blocker.
