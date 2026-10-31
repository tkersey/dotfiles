# Native-Codex migration validation

## Subject and scope

Development base: dotfiles `3caf6c2b2c96bf418c64a30495fc58c675bc03fe`.
All 923 original blobs were checked against the pinned Git tree before editing.
Rebased onto `f4bd5fbd1467e709eff69fffc9f206cbf1d9d809` after verifying all
926 current-source blobs; the newer Actuating construction guidance and tests
remain intact.
The complete source snapshot, not only changed files, was available for local checks.

Native runtime: released `@openai/codex@0.166.0`, Linux x86-64.
Native executable SHA-256:
`b8a11fedf24b2dfb59a70c9e52b030f9a508dcd49cd2dd0d41956f4c785156b8`.
Tests used isolated homes, disposable repositories and a controlled loopback model
provider, with no user account credentials. A poison `cas` command failed/logged
any accidental invocation; no invocation occurred. This is executable integration
qualification, not a real-model review, account qualification or efficacy study.

## Reproduce

```bash
node agents/skills/cas/tests/test-native-contract.mjs
sh agents/skills/actuating/tests/test-reconciler-contract.sh --local-only
uv run --no-project --with aiohttp==3.13.3 \
  agents/skills/cas/tests/test_native_codex.py --codex /exact/path/to/codex
```

The Python test's client/provider and artifact oracle are test-only. Production
uses native Codex and caller-owned process/input/output facilities, not this test
harness, another executable wrapper, or a new receipt/attempt store.

## Completed checks

| Check | Observed result |
|---|---|
| Native standard, original structured artifact, model-side WebSocket | Passed; one actual review request and exact parent/root/target readback. |
| Auxiliary instruction delivery and findings with a correct-patch label | Passed; quotes, backslash, Unicode and trailing newlines preserved through native CLI configuration. Findings remain present. |
| Malformed reviewer output | Passed; native exit zero can coexist with parser fallback, which does not meet structured-verdict requirements. |
| Observation timeout | Passed; the same process completed without a duplicate model request. |
| Cancellation and provider failure | Passed; verified process termination/failure, with no completed usable review result. |
| Prepared seed and control WebSocket | Passed; completed preparation retained across two verified children, one child's subsequent assignment does not alter seed/sibling; native loopback control handshake succeeds. |
| Native migration source checks | Passed; 10 mutation controls, active-guidance command scan and historical provenance/custody distinction. |
| Actuating local suite | Passed; preserved review inventory/counts/freezes/lens bytes and construction contracts; 25 offline credit cases, 27 barrier scenarios and existing admission/discovery/revocation checks. |
| Elenctic non-browser suite | 116 tests passed. |
| Ergasterion suite | 33 tests passed. |

The native qualification has seven tests. Its negative artifact mutations test a
qualification oracle, not a new production parser or proof of model compliance.
The existing Actuating source suite retains its 18 routing and 10 construction
mutation controls. Offline evaluation keys are not completed agent evaluations.

## Important observations and limits

Public exec JSONL and the public `exitedReviewMode.review` projection are rendered
output, not the original structured object. The qualified native rollout retains
`ExitedReviewMode.review_output` under exact parent/root-turn identity. Readback
must not mistake the delegated reviewer's different turn ID for the root review.

An initial SIGINT-only expectation failed: Codex 0.166.0 can report a root/delegate
turn-ID mismatch and continue the review. The final cancellation test verifies
actual termination of its owned process group, not signal submission. The skill
preserves possibly live work and withholds cancelled-request credit; no upstream
runtime fix or universal Ctrl-C guarantee is claimed.

The full Elenctic file-origin browser run reached 158 tests: 136 passed, one
existing opt-in test skipped, and 21 navigation errors were blocked by the host's
`ERR_BLOCKED_BY_ADMINISTRATOR` policy. Loopback navigation is also blocked. These
are **not passes**; no browser policy or renderer was changed. The separately
completed non-browser suite above is not a substitute for file-origin qualification.

External Review Fold/Ledger integration, a real-account review-convergence campaign,
a real-model efficacy/latency comparison, same-turn unfinished coordinator-history
qualification, and inspection of the user's local scheduler were not performed.
The preserved full-history contract still requires actual retained preparation;
the completed-cutoff fork fixture does not certify unobserved histories.

This PR changes instruction/execution contracts, not the installed user runtime.
The later executable deletion must inventory and migrate/retire any remaining
local automation scheduler or external caller. Stored schedules, histories and
old CAS evidence remain untouched.
