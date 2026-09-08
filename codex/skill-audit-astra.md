# Skill audit for GPT-6 Astra

Reviewed **34 personal skill packages and all 21 active managed skills**. Applied
changes to **26 personal and 14 managed skills**. The other 15 retain their current
behavior. Personal coverage includes `elenctic`, which exists locally but is not
in this session's active catalog; inactive plugin-cache copies were not treated
as active skills. This was a current-source audit and local implementation, not a
historical session-effectiveness study.

Astra's documented tendencies make literal instruction conflicts particularly
important: unnecessary clarification, broad testing, detailed output, and
underuse of parallel work can all be amplified by skill instructions. The useful
response is precise activation, clear continuation, conditional resource loading,
and verification proportional to the task. [Official Astra guidance](https://developers.openai.com/api/docs/guides/latest-model#gpt-6-astra-behavior)

The edits target those behaviors without adding a shared optimizer, new workflow
protocol, model pin, or mandatory audit stage. Existing review counts, exact-head
merge guards, authority boundaries, independent oracles, and canonical source
custody remain intact. `glaze` and `metanoetic` are entirely byte-identical.

## Changes with the strongest evidence

- **Land could falsely admit a merge.** Python set membership accepted JSON
  numeric `0`/`1` as booleans, while subsequent identity comparisons interpreted
  them differently. Strict type checks now reject malformed approval, required
  check, and freshness fields. Regression cases cover numbers, strings, null,
  arrays, and objects. [Evaluator](skills/land/scripts/evaluate_preflight.py)
- **Lean's lexical trust audit concealed scan failures.** A missing target could
  return success because every search error was suppressed. Both search backends
  now distinguish no matches from failure. [Helper](skills/lean/scripts/lean_trust_audit.sh)
- **Four auxiliary reviewers requested the wrong output.** Their instructions
  asked for bare `clean` or prose `findings`. They now preserve the native review
  object, including location and correctness fields. Search priorities and
  review scheduling are unchanged. [Example lens](skills/actuating/references/lenses/footgun-review.md)
- **Authorized work could stop unnecessarily.** Grill now adopts explicit user
  answers and resumes already-authorized implementation. The API-key skill
  honors prior credential authorization and permits independent offline work
  while a credential decision is pending. Secret creation, destination consent,
  and live-call authority remain required.
- **Several operations depended on the wrong environment.** Installed helper
  paths now resolve independently of the target repository; missing optional
  planning tools no longer force calls to nonexistent tools; network diagnosis
  respects effective approval policy. Image edits use the current tool's actual
  local-path arguments.
- **Contracts and metadata disagreed.** Registered Seq's existing token-usage
  definition, removed undefined Zig artifact requirements, repaired retired skill
  routes, and removed obsolete aggregate memory-checkpoint instructions. Two
  existing decision contracts had schema-invalid extra keys; their source
  meaning now resides in the supported rationale field.

## Personal skills

Each package's kernel and agent metadata were reviewed, with contracts, helpers,
tests, and references inspected where the proposed change depended on them.

| Skill | Disposition | Applied optimization or reason to retain |
|---|---|---|
| [actuating](skills/actuating/SKILL.md) | Changed | Four lenses return native structured reviews; align contract shape and intentional instruction fingerprints. Preserve all review counts, reset rules, and process digest. |
| [cas](skills/cas/SKILL.md) | Changed | Standalone review examples no longer include workflow bindings that belong to `start --wait`. |
| [codebase-doctrine](skills/codebase-doctrine/SKILL.md) | Changed | Use existing output/candidacy references conditionally; replace unavailable evidence-provider routes. Kernel falls from 557 to 493 lines. |
| [complexity-mitigator](skills/complexity-mitigator/SKILL.md) | Retained | Its compact kernel already scopes local work, preserves uncertainty, and prevents duplicate Actuating work. |
| [creative-problem-solver](skills/creative-problem-solver/SKILL.md) | Changed | Replace missing `ideate` and `codebase-archaeology` routes with direct appropriate analysis. Preserve its explicit five-tier portfolio construction. |
| [deckset](skills/deckset/SKILL.md) | Changed | Restrict discovery to Deckset/markdown decks; editable PowerPoint and Google Slides route to Presentations. Preserve upstream-refresh behavior. |
| [elenctic](skills/elenctic/SKILL.md) | Retained | Seed lineage, selected-file coverage, and PR epoch semantics are substantive obligations. Generic worker substitution would change the construction. |
| [emulator](skills/emulator/SKILL.md) | Changed | Narrow discovery to executable environments and comparisons. Scope broad pilot qualification separately from a request for one chart. |
| [ergon](skills/ergon/SKILL.md) | Changed | Ordinary task views skip development acceptance tests and redundant diagnostics. Reuse compatible runtime readiness; preserve graph and revision laws. |
| [first-principles](skills/first-principles/SKILL.md) | Retained | Compact canonical instruction with explicit-intent routing. No demonstrated defect warrants rewriting it. |
| [footgun-finder](skills/footgun-finder/SKILL.md) | Changed | Default to concise evidence-bearing findings; full ledger/agenda only when requested. Align the default prompt and preserve embedded review output. |
| [fresh-eyes](skills/fresh-eyes/SKILL.md) | Retained | Compact canonical instruction and appropriate explicit/auxiliary activation. |
| [glaze](skills/glaze/SKILL.md) | Protected | Entire file unchanged, including verbatim encouragement. |
| [grill-me](skills/grill-me/SKILL.md) | Changed | Respect explicit answers, continue authorized work, and use question tools only within their actual host contract. Remove fallback banners and invented `Other` options. |
| [invariant-ace](skills/invariant-ace/SKILL.md) | Changed | Preserve seven authority dimensions and vetoes; make the 22-section public report conditional. Repair missing worker reference and align the default prompt. |
| [land](skills/land/SKILL.md) | Changed | Fix malformed-boolean admission, portable evaluator execution, and explicit natural-language merge-intent wording. Preserve review reconciliation and live merged-state proof. |
| [lean](skills/lean/SKILL.md) | Changed | Propagate scan errors, resolve helper location correctly, and scope default trust auditing to the actual verification claim. |
| [learnings](skills/learnings/SKILL.md) | Changed | Evaluate a possible no-op from existing evidence before runtime/store discovery. Canonical operations and accepted capture retain their existing requirements. |
| [ledger](skills/ledger/SKILL.md) | Retained | Bootstrap reuse and definition-relative custody are already explicit. No additional coordinator or wrapper is justified. |
| [lift](skills/lift/SKILL.md) | Changed | Move CLI-specific launcher detail behind a conditional reference; replace mandatory ten-part chat output with the relevant measurements and proof. Default prompt no longer suggests publication. |
| [memory-source-notes](skills/memory-source-notes/SKILL.md) | Changed | Resolve adapters from the installed package; pass the target repository explicitly for Negative Ledger operations. |
| [metanoetic](skills/metanoetic/SKILL.md) | Protected | Entire file unchanged, including verbatim canonical pass. |
| [negative-ledger](skills/negative-ledger/SKILL.md) | Changed | Remove retired lifecycle-checkpoint prompt, reuse runtime readiness, and repair admission paths without changing the route-exclusion gate. |
| [noetic-effects](skills/noetic-effects/SKILL.md) | Retained | Existing skip, native-handler reuse, and one-pass rules already limit unnecessary cognitive machinery. |
| [plan](skills/plan/SKILL.md) | Changed | Generate challengers only for a live material choice or existing Metanoetic trigger. Preserve invariant challenge, source reread, executable specification, and proof/rollback. |
| [prove-it](skills/prove-it/SKILL.md) | Changed | Ordinary certainty words no longer launch a gauntlet. Load numbered lens detail at assignment time; explicitly isolate worker context. Preserve nine lenses followed by one oracle. |
| [reduce](skills/reduce/SKILL.md) | Changed | Report the affected abstraction, obligation, operation, preservation evidence, and safe first change; expand only where a broad audit needs it. |
| [review-fold](skills/review-fold/SKILL.md) | Changed | Discovery metadata no longer claims Actuating's architecture or closure authority; fix decision-contract structural shape. |
| [seq](skills/seq/SKILL.md) | Changed | Register the existing token-usage definition and reuse unchanged capability readiness. Preserve lineage, denominators, contamination, and source boundaries. |
| [ship](skills/ship/SKILL.md) | Changed | Concise PR/state/head/validation output replaces a mandatory nine-row chat form. Immutable receipts and live publication readback remain required. |
| [synesthesia](skills/synesthesia/SKILL.md) | Changed | Remove retired coordination prompt; keep durability gate in the kernel and move persistence mechanics to its existing reference. Preserve canonical capture before note transport. |
| [tune](skills/tune/SKILL.md) | Changed | Read conditional resources only when needed; explicitly complete portfolio requests per target without requiring historical dossiers for direct text defects. |
| [universalist](skills/universalist/SKILL.md) | Changed | Align the categorical specialist with the existing typed-hole gate and three-card limit. Main reasoning kernel and team-activation boundary remain unchanged. |
| [zig](skills/zig/SKILL.md) | Changed | Replace nonexistent receipt requirements with existing bounds/assertion/final-context proof obligations; repair helper paths and audit-output permission friction. |

## Active managed skills

These changes are applied to installed `.system` and plugin-cache copies.
**Updates or reinstalls can replace them.** The
[managed-copy patch](skill-audit-astra-managed.patch) preserves the exact 22-file
delta for review and version-aware reapplication. It is not a plugin fork or an
automatic override. Its paths identify this machine's installed versions.

| Skill | Disposition | Applied optimization or reason to retain |
|---|---|---|
| imagegen | Changed | Support current `referenced_image_paths` editing and mutually exclusive conversation-image selection; use transient CLI dependencies. |
| openai-docs | Changed | Align local-evidence-first source order throughout routed references; allow the relevant official OpenAI domains. Preserve current-source verification and exact-model selection. |
| plugin-creator | Retained | Concrete scaffolding/manifest checks remain useful. Boilerplate compression alone did not justify changing its maintained generator workflow. |
| skill-installer | Retained | Installation behavior is bounded; its conditional sandbox guidance remains subordinate to current execution policy. No installation was requested. |
| skill-creator | Retained | Already emphasizes capable models, concise discovery, progressive disclosure, and scoped validation. Tune owns this portfolio's edits. |
| Browser | Changed | Reuse connector discovery for unchanged capability/resource/access conditions; preserve explicit browser intent and state-freshness rules. |
| Computer Use | Retained | Existing API/state-freshness and consequential-action boundaries are substantive; no concrete correction selected. |
| Deep Research | Changed | Use `update_plan` only if exposed; otherwise maintain research state internally and continue. |
| Plugin Management | Changed | Discover actual search/suggestion capabilities, avoid invented calls, and keep installation authority separate. |
| Agents SDK | Retained | Preserve runnable minimal implementation and real-path smoke tests. Its inherited credential friction is fixed in the credential owner. |
| Build ChatGPT App | Retained | Preserve documented scaffold/API requirements. Broad loading reduction needs representative app-edit evaluation before changing its required baseline. |
| ChatGPT App Submission | Changed | Honor existing authorization to correct metadata instead of asking for it again. Preserve truthful annotations and source-derived JSON. |
| OpenAI API Troubleshooting | Changed | Respect effective escalation policy; remove the stale suggestion that changing models remedies exhausted credit. Align generic transport evals. |
| OpenAI Platform API Key | Changed | Preserve prior reuse authorization, allow independent offline work, and gate the destination tool on its actual picker prerequisites. Update corresponding eval expectations. |
| Documents | Changed | Make render gates consistent with the existing missing-LibreOffice fallback; align final verification on every page. |
| PDF | Changed | Preserve form interactivity when intent is ambiguous; use transient `uv run` dependencies. |
| Presentations | Changed | Permit native diagram objects, preserve explicitly requested editability, and reserve all-26-module qualification for library maintenance. |
| Spreadsheets | Changed | Preserve requested CSV/TSV format; discover supported runtime capabilities before declaring them absent; make planning-tool use conditional. No unsupported exporter is invented. |
| Excel Live Control | Retained | Workbook/session identity safeguards remain useful. Setup-path changes need a real connected-session exercise. |
| Template Creator | Changed | Resolve its dependency loader through available capabilities or explicit runtime instructions; report a real missing runtime instead of inventing a path. |
| Visualize | Changed | Honor host-required progress/skill announcements while keeping product-facing explanations concise. |

## Verification and limits

- All **34 personal packages** pass the existing skill validator. Every personal
  kernel is below 500 lines. Changed managed frontmatter and personal YAML/TOML
  parse, and changed personal Markdown has no missing local link targets.
- All **eight decision contracts** validate through native Ledger 1.2.0 under
  Tune's existing definition. Stable trigger, route, and clause IDs are preserved.
- Land: **23 tests pass**, including malformed-boolean cases and required-approval
  bypass regression. Lean: both search backends distinguish clean, matching,
  missing, and mixed valid/missing targets.
- Plan: **18 tests pass**, including native admission. Actuating's local suite
  passes its process/byte guards, 27 construction cases, 16 revocation cases,
  seven reissue cases, semantic-hotspot checks, and auxiliary/admission fixtures.
  No live CAS/GitHub review or unrelated corpus-storage integration was run.
- Independent forward exercises covered **eight personal-routing and eight
  managed-tool scenarios**. Newly discovered destination-tool and diagram-output
  conflicts were corrected and reviewed again.
- A small matched review experiment used the same defective and valid dry-run
  subjects in four fresh contexts. The old lens returned prose findings and bare
  `clean`; the revised lens returned native structured objects for both. Both
  versions identified the defect and accepted the valid control. This establishes
  a format improvement on these subjects, not a general defect-discovery gain.
- Independent source review found no remaining actionable regressions in the
  selected changes. The managed patch was applied to reconstructed originals in
  a temporary directory and reproduced all **22 installed files exactly**.
- Personal entrypoints total **8,343 lines**, down from **8,921**; their UTF-8
  size falls by **12,740 bytes**. These are file-size measurements, not runtime
  token, latency, or quality measurements. Discovery descriptions are slightly
  longer overall because some boundaries needed explicit clarification.

Protected full-file SHA-256 values:

```text
glaze       e1124dfce9b9c5f7d28e5f74e27cafc516926b08369cd022775e31c0e38da2a0
metanoetic  a9e5a8a03b1202ada4479d41bae1ce95182ff32522efd527808526372b425811
```

The recommendations adopted here are source-supported corrections and scoped
usability improvements. No evidence establishes a globally optimal skill set or
a general Astra speed/quality uplift. Changing fixed cognitive constructions,
such as Lift's score selection or the five-tier strategy portfolio, was not
justified by this pass's routing and helper evidence. Those remain deliberate
non-changes. At audit completion, all work was local and publication had not yet
been requested.
