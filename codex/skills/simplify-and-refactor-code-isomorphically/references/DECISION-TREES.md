# Decision trees — flowcharts for the ambiguous calls

> When you hit an ambiguous decision mid-pass, print the relevant tree and
> walk it in order. Do not skip nodes. Record the path you took in the
> isomorphism card / rejection log so reviewers can replay your logic.

## Contents

1. [Tree 1 — collapse or leave?](#tree-1--collapse-or-leave)
2. [Tree 2 — rescue mission or main loop?](#tree-2--rescue-mission-or-main-loop)
3. [Tree 3 — delete, stage, or keep?](#tree-3--delete-stage-or-keep)
4. [Tree 4 — extract-fn, dispatch, or leave alone?](#tree-4--extract-fn-dispatch-or-leave-alone)
5. [Tree 5 — accept or reject a candidate by score + risk?](#tree-5--accept-or-reject-a-candidate-by-score--risk)

---

## Tree 1 — collapse or leave?

```
                            [ duplication detected ]
                                       │
                  ┌────────────────────┴────────────────────┐
                  │                                         │
             2 sites only                              3+ sites
                  │                                         │
                  ▼                                         ▼
         ┌──────────────┐                    ┌──────────────────────┐
         │ Rule of 3:   │                    │ Can you state the    │
         │ NOT YET      │                    │ observable contract  │
         │              │                    │ each site satisfies? │
         │ rung 0 keeps │                    └──────────────────────┘
         │ copy-paste   │                            │         │
         │ Revisit when │                          yes         no
         │ 3rd appears. │                            │         │
         └──────────────┘                            ▼         │
                                   ┌─────────────────────┐     │
                                   │ Do all sites' contracts │ ◄─── STOP:
                                   │ match byte-for-byte on  │      read each site in
                                   │ return / errors /       │      full; if you can't
                                   │ side effects / timing / │      state contract you
                                   │ logs / metrics?         │      cannot collapse.
                                   └─────────────────────────┘
                                           │        │
                                         yes        no
                                           │        │
                                           │        ▼
                                           │   ┌───────────────────────┐
                                           │   │ Is the divergence     │
                                           │   │ intentional and       │
                                           │   │ permanent?            │
                                           │   └───────────────────────┘
                                           │          │        │
                                           │        yes        no
                                           │          │        │
                                           │          ▼        │
                                           │  ┌─────────────┐  │
                                           │  │ Type V      │  │
                                           │  │ accidental  │  │
                                           │  │ rhyme:      │  │
                                           │  │ REJECT.     │  │
                                           │  │ Log in      │  │
                                           │  │ rejection_  │  │
                                           │  │ log.md.     │  │
                                           │  └─────────────┘  │
                                           │                   ▼
                                           │        ┌────────────────────┐
                                           │        │ Type III gapped:   │
                                           │        │ parameterize the   │
                                           │        │ gap; keep side-    │
                                           │        │ effect boundaries  │
                                           │        │ OUTSIDE the helper │
                                           │        └────────────────────┘
                                           ▼
                        ┌──────────────────────────────────────┐
                        │ Type I or II. Score the candidate.   │
                        │ If score ≥ 2.0: fill isomorphism     │
                        │ card, pick lever, proceed to Phase E │
                        └──────────────────────────────────────┘
```

Reference: [DUPLICATION-TAXONOMY.md](DUPLICATION-TAXONOMY.md) for clone types;
[ABSTRACTION-LADDER.md](ABSTRACTION-LADDER.md) for Rule of 3.

---

## Tree 2 — rescue mission or main loop?

```
                         [ start of pass ]
                               │
                               ▼
              ┌──────────────────────────────────┐
              │ ./scripts/rescue_phase_check.sh  │
              │ (reads tests + warnings + orphans)│
              └──────────────────────────────────┘
                         │            │
                    green/ready    red/triage
                         │            │
                         ▼            ▼
                 ┌──────────────┐   ┌────────────────────────────┐
                 │ MAIN LOOP    │   │ RESCUE MODE.               │
                 │ Phase A →    │   │ Do NOT start the main loop.│
                 │ Phase G.     │   │                            │
                 └──────────────┘   │ Triage in this order:      │
                                    │ 1. Quarantine flaky tests  │
                                    │ 2. Pin unpinned deps (P37) │
                                    │ 3. Delete orphans          │
                                    │    (via gauntlet!)         │
                                    │ 4. Snapshot warning        │
                                    │    ceiling                 │
                                    │ 5. Capture first golden    │
                                    │ 6. Re-run rescue_phase_    │
                                    │    check.sh                │
                                    └────────────────────────────┘
                                                │
                                          loop until green,
                                          then enter MAIN LOOP
```

Reference: [RESCUE-MISSIONS.md](RESCUE-MISSIONS.md),
[`rescue_phase_check.sh`](../scripts/rescue_phase_check.sh).

---

## Tree 3 — delete, stage, or keep?

```
                  [ code looks unused or suspicious ]
                                │
                                ▼
                ┌────────────────────────────────┐
                │ Run the 12-step gauntlet:      │
                │ scripts/dead_code_safety_check │
                └────────────────────────────────┘
                          │          │        │
                       clean      ev found   can't tell
                          │          │        │
                          │          │        ▼
                          │          │    ┌───────────────────┐
                          │          │    │ KEEP.             │
                          │          │    │ File a bead       │
                          │          │    │ "investigate      │
                          │          │    │  <sym>" with      │
                          │          │    │  partial evidence.│
                          │          │    │ DO NOT remove.    │
                          │          │    └───────────────────┘
                          │          ▼
                          │  ┌────────────────────┐
                          │  │ KEEP.              │
                          │  │ Document evidence  │
                          │  │ in code comment    │
                          │  │ if surprising, so  │
                          │  │ next session       │
                          │  │ doesn't re-scan.   │
                          │  └────────────────────┘
                          ▼
           ┌─────────────────────────────────┐
           │ User gave explicit approval to  │
           │ delete in this pass?            │
           └─────────────────────────────────┘
                  │          │
                 yes         no
                  │          │
                  ▼          ▼
        ┌────────────┐   ┌────────────────────────────┐
        │ Stage to   │   │ Stage to _to_delete/ only. │
        │ _to_delete/│   │ Commit: "refactor(dead):   │
        │ PLUS       │   │   stage <sym>"             │
        │ delete in  │   │                            │
        │ same PR.   │   │ Ask user; if they approve, │
        │            │   │ a second PR deletes.       │
        │ Risk: HIGH │   │                            │
        │ Require    │   │ Observation window: 7 days │
        │ explicit   │   │ on staging.                │
        │ user ack.  │   │                            │
        └────────────┘   └────────────────────────────┘
```

Reference: [DEAD-CODE-SAFETY.md](DEAD-CODE-SAFETY.md); subagent:
[subagents/dead-code-checker.md](../subagents/dead-code-checker.md).
AGENTS.md Rule #1: no deletion without explicit user approval.

---

## Tree 4 — extract-fn, dispatch, or leave alone?

```
                    [ candidate accepted, pick lever ]
                                 │
                                 ▼
                ┌────────────────────────────────┐
                │ How many axes vary across      │
                │ sites?                         │
                └────────────────────────────────┘
                     │         │         │
                     0         1       2+
                     │         │         │
                     ▼         ▼         ▼
              ┌────────┐  ┌──────────┐  ┌─────────────────────┐
              │ Type I │  │ Type II  │  │ Type IV semantic    │
              │ L-     │  │ L-       │  │ - 3+ sites? yes ─┐  │
              │ EXTRACT│  │ PARAMET- │  │ - 2 sites?  ───┐ │  │
              │        │  │ ERIZE    │  │                │ │  │
              │ Move   │  │          │  │                │ │  │
              │ to     │  │ Each     │  │                │ │  │
              │ shared │  │ axis     │  │                │ │  │
              │ module.│  │ becomes  │  │                │ │  │
              │        │  │ a param. │  │                │ │  │
              │ Watch: │  │          │  │                │ │  │
              │ don't  │  │ Watch:   │  │                │ │  │
              │ cross  │  │ > 3      │  │                │ │  │
              │ module │  │ params?  │  │                │ │  │
              │ bound- │  │ climb to │  │                │ │  │
              │ ary if │  │ rung 3   │  │                │ │  │
              │ security│  │ or 4    │  │                │ │  │
              │ tier   │  │          │  │                │ │  │
              │ differs│  │          │  │                │ │  │
              └────────┘  └──────────┘  │                │ │  │
                                        │    ▼           ▼ │  │
                                        │ ┌────────┐ ┌───────┐│
                                        │ │L-      │ │ Keep  ││
                                        │ │DISPATCH│ │ sepa- ││
                                        │ │        │ │ rate  ││
                                        │ │ table  │ │ OR    ││
                                        │ │ keyed  │ │ fold  ││
                                        │ │ by     │ │ ONE   ││
                                        │ │ enum / │ │ axis  ││
                                        │ │ tag    │ │ only  ││
                                        │ │        │ │       ││
                                        │ │ Watch: │ │ Watch:││
                                        │ │ don't  │ │ 2     ││
                                        │ │ dispatch│ │ sites ││
                                        │ │ across │ │ are   ││
                                        │ │ security│ │ Rule- ││
                                        │ │ tiers  │ │ of-3  ││
                                        │ │        │ │ NOT   ││
                                        │ │        │ │ YET.  ││
                                        │ └────────┘ └───────┘│
                                        └─────────────────────┘
```

If a helper grows > 5 parameters or a dispatch table has > 7 keys, you're
climbing too high on the ladder. Reconsider or split. See
[ABSTRACTION-LADDER.md § over-abstraction autopsies](ABSTRACTION-LADDER.md).

---

## Tree 5 — accept or reject a candidate by score + risk?

```
                    [ candidate has score S and risk R ]
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │ Score = (LOC_saved × Conf) / Risk   │
               │                                     │
               │ S < 2.0 ?                           │
               └─────────────────────────────────────┘
                         │         │
                        yes        no
                         │         │
                         ▼         ▼
                ┌────────────┐   ┌─────────────────────┐
                │ REJECT.    │   │ Risk ≥ 8 ?          │
                │ Log in     │   └─────────────────────┘
                │ rejection_ │        │         │
                │ log.md     │      yes         no
                │ with score │        │         │
                │ so it      │        ▼         │
                │ doesn't    │   ┌─────────┐    │
                │ re-propose │   │ ESCALATE│    │
                │ next pass  │   │ Cite    │    │
                │ at same    │   │ security│    │
                │ score.     │   │ or perf │    │
                └────────────┘   │ concern;│    │
                                 │ ask     │    │
                                 │ user    │    │
                                 │ before  │    │
                                 │ proceed.│    │
                                 └─────────┘    │
                                                ▼
                                  ┌─────────────────────────┐
                                  │ Sites in different      │
                                  │ security zones?         │
                                  │ (auth vs non-auth,      │
                                  │ sandbox vs privileged)  │
                                  └─────────────────────────┘
                                         │        │
                                       yes        no
                                         │        │
                                         ▼        │
                                  ┌──────────┐    │
                                  │ REJECT.  │    │
                                  │ Security │    │
                                  │ bound-   │    │
                                  │ aries    │    │
                                  │ must not │    │
                                  │ be       │    │
                                  │ crossed  │    │
                                  │ by a     │    │
                                  │ shared   │    │
                                  │ helper.  │    │
                                  └──────────┘    │
                                                  ▼
                                  ┌─────────────────────────┐
                                  │ Sites in different      │
                                  │ perf tiers?             │
                                  │ (hot path vs cold path) │
                                  └─────────────────────────┘
                                         │        │
                                       yes        no
                                         │        │
                                         ▼        ▼
                                  ┌──────────┐ ┌──────────────┐
                                  │ WARN     │ │ ACCEPT.      │
                                  │ Often    │ │ Fill card.   │
                                  │ reject;  │ │ Proceed to   │
                                  │ can      │ │ Phase D.     │
                                  │ proceed  │ └──────────────┘
                                  │ IFF      │
                                  │ helper   │
                                  │ is       │
                                  │ inlined  │
                                  │ or       │
                                  │ bench-   │
                                  │ marked.  │
                                  │ See PERF │
                                  └──────────┘
```

References: [SECURITY-AWARE-REFACTOR.md](SECURITY-AWARE-REFACTOR.md),
[PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md),
[`score_candidates.py`](../scripts/score_candidates.py),
[assets/rejection_log.md](../assets/rejection_log.md).
