<proposed_plan>
# Evidence-Conditioned Cache Strategy

## Strategy Summary

Select and deliver the smallest cache strategy that meets latency and correctness requirements without public API growth. The system is classified as `complex`: first execute `ACTION-PROBE`; then select exactly one implementation action from `RULE-IMPLEMENT-A` or `RULE-IMPLEMENT-B`; finally execute `ACTION-FINAL-PROOF`. The mutation commitment horizon is one action.

## Source and Invariants

Policy `POLICY-cache-strategy` is bound to `SPEC-cache-001`, `SGR-cache-001`, source digest `sha256:16d96409090f9f523b17f4f7609c753df3b23e07d1c00701cad692ea3b15addd`, and repository head `head-sha`. `INV-PUBLIC`, `INV-CORRECT`, and `FORBID-BOTH` shield the public API, invalidation correctness, and single-strategy normal form.

## Current Belief and Critical Unknowns

Facts `FACT-SOURCE-CURRENT` and `FACT-API-LOCKED` are currently evidenced. Critical unknown `UNKNOWN-ROUTE` is resolved only by `OBS-ROUTE`, produced by `ACTION-PROBE` under one workload and correctness oracle.

## Commitment Horizon

Current state `STATE-0` materializes only `ACTION-PROBE`. Production actions `ACTION-IMPLEMENT-A` and `ACTION-IMPLEMENT-B` remain dormant until their route observation is present. `$st` and GCR remain required before repository mutation.

## Policy Branches

- `RULE-PROBE` selects `ACTION-PROBE` while route evidence is absent.
- `RULE-IMPLEMENT-A` selects `ACTION-IMPLEMENT-A` after `obs:OBS-ROUTE=route_a`.
- `RULE-IMPLEMENT-B` selects `ACTION-IMPLEMENT-B` after `obs:OBS-ROUTE=route_b`.
- `RULE-FINAL-PROOF` selects `ACTION-FINAL-PROOF` after the selected implementation proof passes.
- `RULE-BLOCK-NEITHER`, `RULE-RETURN-SPEC`, and the rollback rules handle failed evidence, contract invalidation, and proof failure.
- `RULE-SUCCESS` terminates only after both obligations and final proof are closed.

## Proof, Rollback, and Terminal States

`PROOF-PROBE` validates comparable evidence. `PROOF-IMPLEMENT` or `PROOF-IMPLEMENT-B` proves the selected route. `PROOF-FINAL` proves the final tree. Failure observations route to rollback; contract invalidation returns to the specification; neither viable route blocks. Success requires `OBL-IMPL`, `OBL-FINAL`, and `obs:OBS-FINAL=pass` with no forbidden-state atom.

## Policy Delta

Initial policy revision. It replaces speculative implementation sequencing with one evidence-producing probe and two guarded conditional implementation branches. The challenge to retain both strategies was rejected because it doubles semantic surface.

## Execution Policy Graph

```json
{
  "execution_policy_graph": {
    "policy_version": "EPG-v1",
    "policy_id": "POLICY-cache-strategy",
    "revision": 1,
    "parent": null,
    "created_at": "2026-06-24T12:00:00-07:00",
    "profile": "strict",
    "source": {
      "mode": "spec_handoff",
      "authority": "spec-pipeline/SGR-v2",
      "source_refs": [
        "docs/cache-strategy-spec.md",
        "SGR-cache-001"
      ],
      "source_digest": "sha256:16d96409090f9f523b17f4f7609c753df3b23e07d1c00701cad692ea3b15addd",
      "spec_id": "SPEC-cache-001",
      "spec_governance_ref": "SGR-cache-001",
      "artifact_state": {
        "repo_bound": "yes",
        "repository": "/repo/cache",
        "branch": "feature/cache",
        "base": "base-sha",
        "head": "head-sha",
        "dirty_fingerprint": "sha256:85067f37b8beae9917f4a78fc064f83002089a7eefaa11f4f5ab70a00784eb20"
      },
      "locked_decision_refs": [
        "SPEC-DEC-public-api"
      ],
      "current": "yes"
    },
    "goal": {
      "objective": "Select and deliver the smallest cache strategy that meets latency and correctness requirements without public API growth.",
      "obligations": [
        {
          "obligation_id": "OBL-IMPL",
          "statement": "One evidence-selected cache strategy is implemented without the rejected strategy surface.",
          "source_refs": [
            "SPEC-cache-001#implementation"
          ],
          "terminal_predicate_refs": [
            "TP-IMPL"
          ],
          "proof_refs": [
            "PROOF-IMPLEMENT"
          ]
        },
        {
          "obligation_id": "OBL-FINAL",
          "statement": "The final tree meets latency, invalidation correctness, and repository closure proof.",
          "source_refs": [
            "SPEC-cache-001#proof"
          ],
          "terminal_predicate_refs": [
            "TP-FINAL"
          ],
          "proof_refs": [
            "PROOF-FINAL"
          ]
        }
      ],
      "terminal_predicates": [
        {
          "predicate_id": "TP-IMPL",
          "statement": "Selected implementation obligation is closed.",
          "atom": "obligation:OBL-IMPL=closed"
        },
        {
          "predicate_id": "TP-FINAL",
          "statement": "Final proof obligation is closed.",
          "atom": "obligation:OBL-FINAL=closed"
        }
      ],
      "safety_invariants": [
        {
          "invariant_id": "INV-PUBLIC",
          "statement": "No public cache API is added.",
          "violation_atom": "custom:public-api-growth",
          "source_refs": [
            "SPEC-DEC-public-api"
          ]
        },
        {
          "invariant_id": "INV-CORRECT",
          "statement": "Invalidation correctness is never traded for latency.",
          "violation_atom": "custom:invalidation-incorrect",
          "source_refs": [
            "SPEC-cache-001#correctness"
          ]
        }
      ],
      "forbidden_states": [
        {
          "forbidden_id": "FORBID-BOTH",
          "statement": "Both cache strategies survive in production.",
          "atom": "custom:both-strategies-live",
          "response_terminal": "rollback"
        }
      ]
    },
    "regime": {
      "kind": "complex",
      "confidence": "high",
      "rationale": "The correct representation depends on representative workload evidence unavailable before execution.",
      "reclassify_on_observation_refs": [
        "OBS-ROUTE"
      ]
    },
    "belief": {
      "facts": [
        {
          "fact_id": "FACT-SOURCE-CURRENT",
          "atom": "fact:FACT-SOURCE-CURRENT",
          "statement": "The governed spec and repository tuple are current.",
          "evidence_refs": [
            "SGR-cache-001",
            "git:head-sha"
          ],
          "confidence": "high",
          "invalidators": [
            "INV-SOURCE",
            "INV-TREE"
          ]
        },
        {
          "fact_id": "FACT-API-LOCKED",
          "atom": "fact:FACT-API-LOCKED",
          "statement": "The public API is locked by the source spec.",
          "evidence_refs": [
            "SPEC-DEC-public-api"
          ],
          "confidence": "high",
          "invalidators": [
            "INV-SOURCE"
          ]
        }
      ],
      "unknowns": [
        {
          "unknown_id": "UNKNOWN-ROUTE",
          "statement": "Which representation meets the workload bar with the least semantic surface?",
          "consequence_if_wrong": "Implementation rework or latency/correctness failure.",
          "decision_relevance": "Selects the only allowed production mutation route.",
          "evidence_required": [
            "same workload digest",
            "P95 latency",
            "memory ceiling",
            "invalidation proof"
          ],
          "observation_refs": [
            "OBS-ROUTE"
          ],
          "status": "open",
          "urgency": "critical"
        }
      ]
    },
    "observations": [
      {
        "observation_id": "OBS-ROUTE",
        "source_kind": "metric",
        "command_or_evidence": "run bounded comparison benchmark and correctness matrix",
        "predicate": "Compare both strategies under the same workload and correctness checks.",
        "freshness": "valid only for current source/workload/tree digest",
        "evidence_schema": "route, workload_digest, p95_ms, memory_bytes, invalidation_pass",
        "resolves_unknown_refs": [
          "UNKNOWN-ROUTE"
        ],
        "outcomes": [
          {
            "outcome": "route_a",
            "atom": "obs:OBS-ROUTE=route_a"
          },
          {
            "outcome": "route_b",
            "atom": "obs:OBS-ROUTE=route_b"
          },
          {
            "outcome": "neither",
            "atom": "obs:OBS-ROUTE=neither"
          },
          {
            "outcome": "contract_invalid",
            "atom": "obs:OBS-ROUTE=contract_invalid"
          }
        ]
      },
      {
        "observation_id": "OBS-IMPLEMENT-A",
        "source_kind": "test",
        "command_or_evidence": "zig build test-cache-a --summary all",
        "predicate": "Selected route A satisfies focused latency and invalidation obligations.",
        "freshness": "current implementation tree",
        "evidence_schema": "status, p95_ms, invalidation_pass, artifact_digest",
        "resolves_unknown_refs": [],
        "outcomes": [
          {
            "outcome": "pass",
            "atom": "obs:OBS-IMPLEMENT-A=pass"
          },
          {
            "outcome": "fail",
            "atom": "obs:OBS-IMPLEMENT-A=fail"
          }
        ]
      },
      {
        "observation_id": "OBS-IMPLEMENT-B",
        "source_kind": "test",
        "command_or_evidence": "zig build test-cache-b --summary all",
        "predicate": "Selected route B satisfies focused latency and invalidation obligations.",
        "freshness": "current implementation tree",
        "evidence_schema": "status, p95_ms, invalidation_pass, artifact_digest",
        "resolves_unknown_refs": [],
        "outcomes": [
          {
            "outcome": "pass",
            "atom": "obs:OBS-IMPLEMENT-B=pass"
          },
          {
            "outcome": "fail",
            "atom": "obs:OBS-IMPLEMENT-B=fail"
          }
        ]
      },
      {
        "observation_id": "OBS-FINAL",
        "source_kind": "command",
        "command_or_evidence": "zig build check --summary all",
        "predicate": "Complete final-tree closure proof passes.",
        "freshness": "exact final tree/toolchain/options",
        "evidence_schema": "status, artifact_digest, command, toolchain",
        "resolves_unknown_refs": [],
        "outcomes": [
          {
            "outcome": "pass",
            "atom": "obs:OBS-FINAL=pass"
          },
          {
            "outcome": "fail",
            "atom": "obs:OBS-FINAL=fail"
          }
        ]
      }
    ],
    "actions": [
      {
        "action_id": "ACTION-PROBE",
        "kind": "probe",
        "owner": "performance",
        "preconditions": {
          "all": [
            "fact:FACT-SOURCE-CURRENT",
            "fact:FACT-API-LOCKED"
          ],
          "any": [],
          "none": [
            "obs:OBS-ROUTE=route_a",
            "obs:OBS-ROUTE=route_b",
            "obs:OBS-ROUTE=neither",
            "obs:OBS-ROUTE=contract_invalid"
          ]
        },
        "requires_actions": [],
        "mutation_boundary": {
          "kind": "repository",
          "paths": [
            "bench/cache_bench.zig",
            "test/cache_test.zig"
          ],
          "symbols": []
        },
        "lock_roots": [
          "bench/cache_bench.zig",
          "test/cache_test.zig"
        ],
        "expected_effects": {
          "facts_added": [],
          "unknowns_resolved": [
            "UNKNOWN-ROUTE"
          ],
          "obligations_closed": [],
          "potential_delta": {
            "critical_unknowns": -1,
            "unsatisfied_obligations": 0,
            "hard_semantic_surface": 0
          }
        },
        "expected_observation_refs": [
          "OBS-ROUTE"
        ],
        "failure_observation_refs": [
          "OBS-ROUTE"
        ],
        "proof_obligations": [
          {
            "proof_id": "PROOF-PROBE",
            "statement": "Both alternatives use one workload and correctness oracle.",
            "evidence_kind": "experiment",
            "command_or_evidence": "run bounded comparison benchmark",
            "artifact_binding": "action"
          }
        ],
        "rollback": {
          "trigger_atoms": [
            "obs:OBS-ROUTE=contract_invalid"
          ],
          "action_id": null,
          "instructions": "Discard probe changes and return to the source contract."
        },
        "utility": {
          "obligation_reduction": 0,
          "information_gain": 100,
          "downstream_unlock": 100,
          "proof_gain": 30,
          "execution_cost": 25,
          "irreversible_risk": 5,
          "semantic_surface_growth": 0,
          "rework_risk": 5
        },
        "repeatable": false
      },
      {
        "action_id": "ACTION-IMPLEMENT-A",
        "kind": "mutate",
        "owner": "engineering",
        "preconditions": {
          "all": [
            "obs:OBS-ROUTE=route_a",
            "fact:FACT-API-LOCKED"
          ],
          "any": [],
          "none": [
            "custom:public-api-growth",
            "custom:both-strategies-live"
          ]
        },
        "requires_actions": [
          "ACTION-PROBE"
        ],
        "mutation_boundary": {
          "kind": "repository",
          "paths": [
            "src/cache.zig",
            "test/cache_test.zig"
          ],
          "symbols": [
            "Cache.get",
            "Cache.invalidate"
          ]
        },
        "lock_roots": [
          "src/cache.zig"
        ],
        "expected_effects": {
          "facts_added": [],
          "unknowns_resolved": [],
          "obligations_closed": [
            "OBL-IMPL"
          ],
          "potential_delta": {
            "critical_unknowns": 0,
            "unsatisfied_obligations": -1,
            "hard_semantic_surface": 0
          }
        },
        "expected_observation_refs": [
          "OBS-IMPLEMENT-A"
        ],
        "failure_observation_refs": [
          "OBS-IMPLEMENT-A"
        ],
        "proof_obligations": [
          {
            "proof_id": "PROOF-IMPLEMENT",
            "statement": "Route A focused latency and invalidation proof passes.",
            "evidence_kind": "command",
            "command_or_evidence": "zig build test-cache-a --summary all",
            "artifact_binding": "action"
          }
        ],
        "rollback": {
          "trigger_atoms": [
            "obs:OBS-IMPLEMENT-A=fail"
          ],
          "action_id": null,
          "instructions": "Revert route A implementation and return to policy."
        },
        "utility": {
          "obligation_reduction": 80,
          "information_gain": 20,
          "downstream_unlock": 80,
          "proof_gain": 60,
          "execution_cost": 50,
          "irreversible_risk": 20,
          "semantic_surface_growth": 20,
          "rework_risk": 20
        },
        "repeatable": false
      },
      {
        "action_id": "ACTION-IMPLEMENT-B",
        "kind": "mutate",
        "owner": "engineering",
        "preconditions": {
          "all": [
            "obs:OBS-ROUTE=route_b",
            "fact:FACT-API-LOCKED"
          ],
          "any": [],
          "none": [
            "custom:public-api-growth",
            "custom:both-strategies-live"
          ]
        },
        "requires_actions": [
          "ACTION-PROBE"
        ],
        "mutation_boundary": {
          "kind": "repository",
          "paths": [
            "src/cache.zig",
            "test/cache_test.zig"
          ],
          "symbols": [
            "Cache.get",
            "Cache.invalidate"
          ]
        },
        "lock_roots": [
          "src/cache.zig"
        ],
        "expected_effects": {
          "facts_added": [],
          "unknowns_resolved": [],
          "obligations_closed": [
            "OBL-IMPL"
          ],
          "potential_delta": {
            "critical_unknowns": 0,
            "unsatisfied_obligations": -1,
            "hard_semantic_surface": 0
          }
        },
        "expected_observation_refs": [
          "OBS-IMPLEMENT-B"
        ],
        "failure_observation_refs": [
          "OBS-IMPLEMENT-B"
        ],
        "proof_obligations": [
          {
            "proof_id": "PROOF-IMPLEMENT-B",
            "statement": "Route B focused latency and invalidation proof passes.",
            "evidence_kind": "command",
            "command_or_evidence": "zig build test-cache-b --summary all",
            "artifact_binding": "action"
          }
        ],
        "rollback": {
          "trigger_atoms": [
            "obs:OBS-IMPLEMENT-B=fail"
          ],
          "action_id": null,
          "instructions": "Revert route B implementation and return to policy."
        },
        "utility": {
          "obligation_reduction": 80,
          "information_gain": 20,
          "downstream_unlock": 80,
          "proof_gain": 60,
          "execution_cost": 55,
          "irreversible_risk": 20,
          "semantic_surface_growth": 15,
          "rework_risk": 20
        },
        "repeatable": false
      },
      {
        "action_id": "ACTION-FINAL-PROOF",
        "kind": "prove",
        "owner": "engineering",
        "preconditions": {
          "all": [
            "obligation:OBL-IMPL=closed"
          ],
          "any": [
            "obs:OBS-IMPLEMENT-A=pass",
            "obs:OBS-IMPLEMENT-B=pass"
          ],
          "none": [
            "custom:invalidation-incorrect"
          ]
        },
        "requires_actions": [],
        "mutation_boundary": {
          "kind": "none",
          "paths": [],
          "symbols": []
        },
        "lock_roots": [],
        "expected_effects": {
          "facts_added": [],
          "unknowns_resolved": [],
          "obligations_closed": [
            "OBL-FINAL"
          ],
          "potential_delta": {
            "critical_unknowns": 0,
            "unsatisfied_obligations": -1,
            "hard_semantic_surface": 0
          }
        },
        "expected_observation_refs": [
          "OBS-FINAL"
        ],
        "failure_observation_refs": [
          "OBS-FINAL"
        ],
        "proof_obligations": [
          {
            "proof_id": "PROOF-FINAL",
            "statement": "Final-tree repository closure proof passes.",
            "evidence_kind": "command",
            "command_or_evidence": "zig build check --summary all",
            "artifact_binding": "final_tree"
          }
        ],
        "rollback": {
          "trigger_atoms": [
            "obs:OBS-FINAL=fail"
          ],
          "action_id": null,
          "instructions": "Do not deliver; return to implementation or rollback."
        },
        "utility": {
          "obligation_reduction": 100,
          "information_gain": 10,
          "downstream_unlock": 100,
          "proof_gain": 100,
          "execution_cost": 30,
          "irreversible_risk": 0,
          "semantic_surface_growth": 0,
          "rework_risk": 5
        },
        "repeatable": false
      }
    ],
    "policy": {
      "selection": "lexicographic_utility",
      "utility_order": [
        {
          "maximize": "obligation_reduction"
        },
        {
          "maximize": "information_gain"
        },
        {
          "maximize": "downstream_unlock"
        },
        {
          "maximize": "proof_gain"
        },
        {
          "minimize": "irreversible_risk"
        },
        {
          "minimize": "semantic_surface_growth"
        },
        {
          "minimize": "rework_risk"
        },
        {
          "minimize": "execution_cost"
        }
      ],
      "rules": [
        {
          "rule_id": "RULE-PROBE",
          "priority": 10,
          "when": {
            "all": [
              "fact:FACT-SOURCE-CURRENT",
              "fact:FACT-API-LOCKED"
            ],
            "any": [],
            "none": [
              "obs:OBS-ROUTE=route_a",
              "obs:OBS-ROUTE=route_b",
              "obs:OBS-ROUTE=neither",
              "obs:OBS-ROUTE=contract_invalid"
            ]
          },
          "candidate_action_ids": [
            "ACTION-PROBE"
          ],
          "terminal": null,
          "rationale": "Resolve the critical route uncertainty before production mutation.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [
            "UNKNOWN-ROUTE"
          ],
          "evidence_refs": [
            "SPEC-cache-001"
          ],
          "replan_if_atoms": [
            "obs:OBS-ROUTE=contract_invalid"
          ]
        },
        {
          "rule_id": "RULE-IMPLEMENT-A",
          "priority": 20,
          "when": {
            "all": [
              "obs:OBS-ROUTE=route_a"
            ],
            "any": [],
            "none": [
              "action:ACTION-IMPLEMENT-A=success"
            ]
          },
          "candidate_action_ids": [
            "ACTION-IMPLEMENT-A"
          ],
          "terminal": null,
          "rationale": "Route A won the governed evidence comparison.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [
            "UNKNOWN-ROUTE"
          ],
          "evidence_refs": [
            "obs:OBS-ROUTE=route_a"
          ],
          "replan_if_atoms": [
            "obs:OBS-IMPLEMENT-A=fail"
          ]
        },
        {
          "rule_id": "RULE-IMPLEMENT-B",
          "priority": 21,
          "when": {
            "all": [
              "obs:OBS-ROUTE=route_b"
            ],
            "any": [],
            "none": [
              "action:ACTION-IMPLEMENT-B=success"
            ]
          },
          "candidate_action_ids": [
            "ACTION-IMPLEMENT-B"
          ],
          "terminal": null,
          "rationale": "Route B won the governed evidence comparison.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [
            "UNKNOWN-ROUTE"
          ],
          "evidence_refs": [
            "obs:OBS-ROUTE=route_b"
          ],
          "replan_if_atoms": [
            "obs:OBS-IMPLEMENT-B=fail"
          ]
        },
        {
          "rule_id": "RULE-FINAL-PROOF",
          "priority": 30,
          "when": {
            "all": [
              "obligation:OBL-IMPL=closed"
            ],
            "any": [
              "obs:OBS-IMPLEMENT-A=pass",
              "obs:OBS-IMPLEMENT-B=pass"
            ],
            "none": [
              "action:ACTION-FINAL-PROOF=success"
            ]
          },
          "candidate_action_ids": [
            "ACTION-FINAL-PROOF"
          ],
          "terminal": null,
          "rationale": "Close the final obligation only on the current realized tree.",
          "obligation_refs": [
            "OBL-FINAL"
          ],
          "unknown_refs": [],
          "evidence_refs": [
            "PROOF-IMPLEMENT"
          ],
          "replan_if_atoms": [
            "obs:OBS-FINAL=fail"
          ]
        },
        {
          "rule_id": "RULE-SUCCESS",
          "priority": 40,
          "when": {
            "all": [
              "obligation:OBL-IMPL=closed",
              "obligation:OBL-FINAL=closed",
              "obs:OBS-FINAL=pass"
            ],
            "any": [],
            "none": [
              "custom:public-api-growth",
              "custom:invalidation-incorrect",
              "custom:both-strategies-live"
            ]
          },
          "candidate_action_ids": [],
          "terminal": "success",
          "rationale": "All source obligations and final proof are current.",
          "obligation_refs": [
            "OBL-IMPL",
            "OBL-FINAL"
          ],
          "unknown_refs": [],
          "evidence_refs": [
            "PROOF-FINAL"
          ],
          "replan_if_atoms": []
        },
        {
          "rule_id": "RULE-BLOCK-NEITHER",
          "priority": 5,
          "when": {
            "all": [
              "obs:OBS-ROUTE=neither"
            ],
            "any": [],
            "none": []
          },
          "candidate_action_ids": [],
          "terminal": "blocked",
          "rationale": "Neither source-authorized route meets the bar.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [
            "UNKNOWN-ROUTE"
          ],
          "evidence_refs": [
            "OBS-ROUTE"
          ],
          "replan_if_atoms": []
        },
        {
          "rule_id": "RULE-RETURN-SPEC",
          "priority": 4,
          "when": {
            "all": [
              "obs:OBS-ROUTE=contract_invalid"
            ],
            "any": [],
            "none": []
          },
          "candidate_action_ids": [],
          "terminal": "return_to_spec",
          "rationale": "The experiment invalidated the governing contract.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [
            "UNKNOWN-ROUTE"
          ],
          "evidence_refs": [
            "OBS-ROUTE"
          ],
          "replan_if_atoms": []
        },
        {
          "rule_id": "RULE-ROLLBACK-A",
          "priority": 3,
          "when": {
            "all": [
              "obs:OBS-IMPLEMENT-A=fail"
            ],
            "any": [],
            "none": []
          },
          "candidate_action_ids": [],
          "terminal": "rollback",
          "rationale": "Route A failed its focused proof.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [],
          "evidence_refs": [
            "OBS-IMPLEMENT-A"
          ],
          "replan_if_atoms": []
        },
        {
          "rule_id": "RULE-ROLLBACK-B",
          "priority": 2,
          "when": {
            "all": [
              "obs:OBS-IMPLEMENT-B=fail"
            ],
            "any": [],
            "none": []
          },
          "candidate_action_ids": [],
          "terminal": "rollback",
          "rationale": "Route B failed its focused proof.",
          "obligation_refs": [
            "OBL-IMPL"
          ],
          "unknown_refs": [],
          "evidence_refs": [
            "OBS-IMPLEMENT-B"
          ],
          "replan_if_atoms": []
        },
        {
          "rule_id": "RULE-ROLLBACK-FINAL",
          "priority": 1,
          "when": {
            "all": [
              "obs:OBS-FINAL=fail"
            ],
            "any": [],
            "none": []
          },
          "candidate_action_ids": [],
          "terminal": "rollback",
          "rationale": "Final-tree proof failed.",
          "obligation_refs": [
            "OBL-FINAL"
          ],
          "unknown_refs": [],
          "evidence_refs": [
            "OBS-FINAL"
          ],
          "replan_if_atoms": []
        }
      ],
      "tie_breakers": [
        "lowest_irreversible_risk",
        "lowest_semantic_surface_growth",
        "action_id"
      ]
    },
    "potential": {
      "lexicographic_order": [
        "safety_violations",
        "critical_unknowns",
        "unsatisfied_obligations",
        "hard_semantic_surface"
      ],
      "dimensions": [
        {
          "dimension_id": "safety_violations",
          "statement": "Violated safety invariants.",
          "direction": "minimize",
          "current_value": 0,
          "terminal_threshold": 0
        },
        {
          "dimension_id": "critical_unknowns",
          "statement": "Unresolved critical unknowns.",
          "direction": "minimize",
          "current_value": 1,
          "terminal_threshold": 0
        },
        {
          "dimension_id": "unsatisfied_obligations",
          "statement": "Open source obligations.",
          "direction": "minimize",
          "current_value": 2,
          "terminal_threshold": 0
        },
        {
          "dimension_id": "hard_semantic_surface",
          "statement": "Hard production semantic surface.",
          "direction": "minimize",
          "current_value": 1,
          "terminal_threshold": 1
        }
      ],
      "initial": {
        "safety_violations": 0,
        "critical_unknowns": 1,
        "unsatisfied_obligations": 2,
        "hard_semantic_surface": 1
      }
    },
    "safety_shield": {
      "rules": [
        {
          "shield_id": "SHIELD-A",
          "when": {
            "all": [
              "fact:FACT-SOURCE-CURRENT"
            ],
            "any": [],
            "none": []
          },
          "forbids_action_ids": [
            "ACTION-IMPLEMENT-A"
          ],
          "forbids_action_kinds": [],
          "requires_atoms": [
            "obs:OBS-ROUTE=route_a",
            "fact:FACT-API-LOCKED"
          ],
          "response": "block",
          "reason": "Route A mutation requires route-A evidence and locked API authority."
        },
        {
          "shield_id": "SHIELD-B",
          "when": {
            "all": [
              "fact:FACT-SOURCE-CURRENT"
            ],
            "any": [],
            "none": []
          },
          "forbids_action_ids": [
            "ACTION-IMPLEMENT-B"
          ],
          "forbids_action_kinds": [],
          "requires_atoms": [
            "obs:OBS-ROUTE=route_b",
            "fact:FACT-API-LOCKED"
          ],
          "response": "block",
          "reason": "Route B mutation requires route-B evidence and locked API authority."
        }
      ]
    },
    "horizon": {
      "mutation_actions_max": 1,
      "evidence_actions_max": 3,
      "delivery_transitions_max": 1
    },
    "initial_state": {
      "state_version": "EPS-v1",
      "state_id": "STATE-0",
      "satisfied_atoms": [
        "fact:FACT-SOURCE-CURRENT",
        "fact:FACT-API-LOCKED"
      ],
      "completed_actions": [],
      "failed_actions": [],
      "resolved_unknowns": [],
      "closed_obligations": [],
      "current_potential": {
        "safety_violations": 0,
        "critical_unknowns": 1,
        "unsatisfied_obligations": 2,
        "hard_semantic_surface": 1
      },
      "active_action_id": null
    },
    "terminal_states": {
      "success": {
        "when": {
          "all": [
            "obligation:OBL-IMPL=closed",
            "obligation:OBL-FINAL=closed",
            "obs:OBS-FINAL=pass"
          ],
          "any": [],
          "none": [
            "custom:public-api-growth",
            "custom:invalidation-incorrect",
            "custom:both-strategies-live"
          ]
        },
        "proof_refs": [
          "PROOF-FINAL"
        ]
      },
      "blocked": {
        "when": {
          "all": [
            "obs:OBS-ROUTE=neither"
          ],
          "any": [],
          "none": []
        }
      },
      "return_to_spec": {
        "when": {
          "all": [
            "obs:OBS-ROUTE=contract_invalid"
          ],
          "any": [],
          "none": []
        }
      },
      "rollback": {
        "when": {
          "all": [],
          "any": [
            "obs:OBS-IMPLEMENT-A=fail",
            "obs:OBS-IMPLEMENT-B=fail",
            "obs:OBS-FINAL=fail"
          ],
          "none": []
        }
      }
    },
    "invalidators": [
      {
        "invalidator_id": "INV-SOURCE",
        "condition": "The source specification or governance digest changes.",
        "required_action": "return_to_spec",
        "affected_refs": [
          "SPEC-cache-001",
          "OBL-IMPL",
          "OBL-FINAL"
        ]
      },
      {
        "invalidator_id": "INV-TREE",
        "condition": "The repository head, tree, or workload artifact changes before the selected action.",
        "required_action": "replan",
        "affected_refs": [
          "ACTION-PROBE",
          "ACTION-IMPLEMENT-A",
          "ACTION-IMPLEMENT-B",
          "ACTION-FINAL-PROOF"
        ]
      }
    ],
    "challenge": {
      "candidate": "Implement both strategies and choose at runtime.",
      "disposition": "reject",
      "reason": "It doubles semantic surface and violates the source requirement to select one route from evidence.",
      "affected_refs": [
        "OBL-IMPL",
        "FORBID-BOTH"
      ],
      "source_change_required": false
    },
    "revision_summary": {
      "parent_diff_ref": null,
      "policy_changes": [
        "initial evidence-conditioned strategy"
      ],
      "semantic_changes": [],
      "source_changes": []
    },
    "handoff": {
      "next_owner": "st",
      "runtime_ready": "yes",
      "mutation_allowed": "no",
      "gate_result": "pass",
      "reason": "The policy is source-current, closed over modeled outcomes, and ready for short-horizon materialization."
    },
    "gate": {
      "source_current": "yes",
      "semantic_drift": "none",
      "obligations_covered": "yes",
      "critical_unknowns_observable_or_blocked": "yes",
      "actions_bounded": "yes",
      "policy_references_valid": "yes",
      "policy_closed": "yes",
      "safety_shield_complete": "yes",
      "potential_complete": "yes",
      "terminal_states_complete": "yes",
      "downstream_runtime_ready": "yes",
      "fresh_eyes_blockers": 0,
      "policy_ready": "yes"
    }
  }
}
```
</proposed_plan>
