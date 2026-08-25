#!/bin/sh
set -eu

skill_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
jaq_bin=${JAQ_BIN:-jaq}
fixture="$skill_root/tests/fixtures/review-candidate-traces.json"

"$jaq_bin" -e '
  def contains_value($xs; $v): ($xs | index($v)) != null;

  def all_generators_complete:
    (.generator_states | length) > 0 and
    all(.generator_states[]; .complete == true);

  def generator_index($id):
    [.generator_states[].id] | index($id);

  def proof_inventory_complete($e):
    ($e.required_proof_refs | type) == "array" and
    ($e.required_proof_refs | length) > 0 and
    all($e.required_proof_refs[];
      type == "string" and length > 0) and
    ($e.required_proof_refs | unique | length) ==
      ($e.required_proof_refs | length) and
    ($e.proof_results | type) == "array" and
    all($e.proof_results[];
      (.proof_ref | type) == "string" and
      (.proof_ref | length) > 0 and
      .head == $e.head and
      (.disposition == "passed" or
       (.disposition == "not-applicable" and
        (.authority_ref | type) == "string" and
        (.authority_ref | length) > 0))) and
    ([ $e.proof_results[].proof_ref ] | unique | length) ==
      ($e.proof_results | length) and
    ([ $e.proof_results[].proof_ref ] | sort) ==
      ($e.required_proof_refs | sort);

  def candidate_proof_complete($e):
    $e.construction_complete == true and
    $e.causal_basis_complete == true and
    $e.factor_dispositions_complete == true and
    (["passed", "exhaustive", "not-meaningful"] |
      index($e.sibling_disposition)) != null and
    proof_inventory_complete($e);

  def semantic_barrier_complete:
    ((.launched_requests - .semantic_outcomes) | length) == 0;

  def fail($reason):
    .valid = false |
    .error = $reason;

  def initial($s):
    {
      valid: true,
      error: null,
      schedule: $s.schedule,
      required_initial_requests: $s.required_initial_requests,
      phase: "none",
      current_head: null,
      candidate_head: null,
      candidate_generation: 0,
      launched_requests: [],
      terminal_requests: [],
      semantic_outcomes: [],
      verdictless_requests: [],
      recovery_requests: [],
      evidence_cut_closed: false,
      selected_target_id: null,
      selected_targets: [],
      generator_states: [],
      gate_history: [],
      applied_history: [],
      realization_complete: false,
      validation_head: null,
      commit_heads: [],
      restart_heads: []
    };

  def apply_event($e):
    if .valid != true then .
    elif $e.type == "candidate-sealed" then
      if (candidate_proof_complete($e) | not) then
        fail("candidate-entry-incomplete")
      elif .phase == "none" then
        .phase = "reviewable" |
        .current_head = $e.head |
        .candidate_head = $e.head |
        .candidate_generation = 1
      elif .phase == "realizing" and
           .selected_target_id != null and
           .realization_complete == true and
           .validation_head == .current_head and
           $e.head == .current_head and
           all_generators_complete then
        .phase = "reviewable" |
        .candidate_head = .current_head |
        .candidate_generation += 1 |
        .launched_requests = [] |
        .terminal_requests = [] |
        .semantic_outcomes = [] |
        .verdictless_requests = [] |
        .recovery_requests = [] |
        .evidence_cut_closed = false |
        .selected_target_id = null |
        .generator_states = [] |
        .realization_complete = false |
        .validation_head = null
      else fail("candidate-not-sealable")
      end
    elif $e.type == "review-launched" then
      if .phase != "reviewable" then fail("review-dispatch-requires-reviewable")
      elif $e.head != .candidate_head then fail("review-head-mismatch")
      elif contains_value(.launched_requests; $e.request) then
        fail("duplicate-review-request")
      elif (.schedule == "serial" or .schedule == "confirmation") and
           (semantic_barrier_complete | not) then
        fail("serial-request-overlap")
      else
        .launched_requests += [$e.request] |
        if .candidate_generation > 1 and
           (contains_value(.restart_heads; .candidate_head) | not) then
          .restart_heads += [.candidate_head]
        else . end
      end
    elif $e.type == "review-terminal" then
      if (contains_value(.launched_requests; $e.request) | not) then
        fail("terminal-without-launch")
      elif contains_value(.terminal_requests; $e.request) then
        fail("duplicate-terminal")
      elif .schedule == "parallel" and
           (.terminal_requests | length) == 0 and
           (.launched_requests | length) != .required_initial_requests then
        fail("parallel-terminal-before-complete-launch")
      elif (["clean", "material-finding", "non-material-finding", "verdictless"] |
            index($e.verdict)) == null then
        fail("unknown-terminal-verdict")
      else
        .terminal_requests += [$e.request] |
        if $e.verdict == "verdictless" then
          .verdictless_requests += [$e.request]
        else
          .semantic_outcomes += [$e.request]
        end |
        if $e.verdict == "material-finding" then
          .phase = "invalidated"
        else . end
      end
    elif $e.type == "recovery-launched" then
      if (contains_value(.verdictless_requests; $e.request) | not) then
        fail("recovery-without-verdictless-terminal")
      elif contains_value(.recovery_requests; $e.request) then
        fail("duplicate-recovery")
      elif .schedule == "parallel" and
           (.terminal_requests | length) != (.launched_requests | length) then
        fail("parallel-recovery-before-transport-barrier")
      else
        .recovery_requests += [$e.request]
      end
    elif $e.type == "recovery-terminal" then
      if (contains_value(.recovery_requests; $e.request) | not) then
        fail("recovery-terminal-without-launch")
      elif contains_value(.semantic_outcomes; $e.request) then
        fail("duplicate-semantic-outcome")
      elif (["clean", "material-finding", "non-material-finding"] |
            index($e.verdict)) == null then
        fail("verdictless-recovery-terminal")
      else
        .semantic_outcomes += [$e.request] |
        if $e.verdict == "material-finding" then
          .phase = "invalidated"
        else . end
      end
    elif $e.type == "evidence-cut-closed" then
      if .phase != "invalidated" then fail("cut-requires-invalidated-candidate")
      elif (semantic_barrier_complete | not) then fail("semantic-barrier-incomplete")
      else .evidence_cut_closed = true
      end
    elif $e.type == "reconciliation-selected" then
      if .phase != "invalidated" or .evidence_cut_closed != true then
        fail("selection-requires-closed-cut")
      elif $e.classes_folded != true then fail("classes-not-folded")
      elif $e.causal_basis_complete != true then fail("causal-basis-incomplete")
      elif $e.factor_dispositions_complete != true then
        fail("factor-dispositions-incomplete")
      elif (["passed", "exhaustive", "not-meaningful"] |
            index($e.sibling_disposition)) == null then
        fail("sibling-disposition-incomplete")
      elif ($e.target_id | type) != "string" or ($e.target_id | length) == 0 then
        fail("target-not-stated")
      elif ($e.generators | type) != "array" or
           ($e.generators | length) == 0 or
           ([ $e.generators[].id ] | unique | length) !=
             ($e.generators | length) then
        fail("invalid-generator-set")
      elif any($e.generators[];
           .disposition as $disposition |
           (["direct-repair", "architecture"] | index($disposition)) == null) then
        fail("unknown-generator-disposition")
      elif any($e.generators[];
           .same_generator_recurrence == true and
           .separation_proof != true and
           .proposed_member_enumeration == true) then
        fail("same-generator-member-enumeration")
      elif any($e.generators[];
           .same_generator_recurrence == true and
           .separation_proof != true and
           .generative_family_evidence != true and
           .exhaustive_family_evidence != true) then
        fail("same-generator-family-evidence-missing")
      else
        .selected_target_id = $e.target_id |
        .selected_targets += [$e.target_id] |
        .generator_states = ($e.generators | map(. + {
          gate_head: null,
          started: false,
          complete: false
        })) |
        .phase = "realizing"
      end
    elif $e.type == "direct-gate" then
      (generator_index($e.generator)) as $i |
      if .phase != "realizing" then fail("direct-gate-outside-realization")
      elif $i == null then
        fail("direct-gate-unknown-generator")
      elif .generator_states[$i].disposition != "direct-repair" then
        fail("direct-gate-for-architecture-generator")
      elif $e.head != .current_head then fail("direct-gate-head-mismatch")
      elif .generator_states[$i].gate_head != null then
        fail("duplicate-direct-gate-generator")
      else
        .generator_states[$i].gate_head = $e.head |
        .gate_history += [{generator: $e.generator, head: $e.head}]
      end
    elif $e.type == "commit" then
      (generator_index($e.generator)) as $i |
      if .phase != "realizing" or .selected_target_id == null then
        fail("commit-before-successor-selection")
      elif $i == null then fail("commit-unknown-generator")
      elif $e.from_head != .current_head or $e.to_head == .current_head then
        fail("commit-head-mismatch")
      elif .generator_states[$i].complete == true then
        fail("commit-after-generator-complete")
      elif .generator_states[$i].disposition == "direct-repair" and
           .generator_states[$i].started != true and
           .generator_states[$i].gate_head != $e.from_head then
        fail("direct-repair-gate-predecessor-mismatch")
      else
        .generator_states[$i].started = true |
        if (if ($e | has("completes_generator"))
            then $e.completes_generator else true end) == true then
          .generator_states[$i].complete = true
        else . end |
        .applied_history += [{generator: $e.generator, head: $e.to_head}] |
        .current_head = $e.to_head |
        .commit_heads += [$e.to_head] |
        .realization_complete = false |
        .validation_head = null
      end
    elif $e.type == "generator-complete" then
      (generator_index($e.generator)) as $i |
      if .phase != "realizing" or $i == null then
        fail("generator-complete-before-selection")
      elif $e.head != .current_head then fail("generator-complete-head-mismatch")
      elif .generator_states[$i].started != true then
        fail("generator-complete-before-commit")
      elif .generator_states[$i].complete == true then
        fail("duplicate-generator-complete")
      else .generator_states[$i].complete = true
      end
    elif $e.type == "realization-complete" then
      if .phase != "realizing" or .selected_target_id == null then
        fail("realization-complete-before-selection")
      elif $e.head != .current_head or .current_head == .candidate_head then
        fail("realization-complete-head-mismatch")
      elif (all_generators_complete | not) then fail("generators-unrealized")
      else .realization_complete = true
      end
    elif $e.type == "validation" then
      if .phase != "realizing" or .realization_complete != true then
        fail("validation-before-complete-realization")
      elif $e.head != .current_head or $e.passed != true then
        fail("validation-not-current-or-failed")
      else .validation_head = $e.head
      end
    else fail("unknown-event")
    end;

  .scenarios |= map(
    . as $s |
    .result = (reduce $s.events[] as $e (initial($s); apply_event($e)))
  ) |
  .schema == "actuating-review-candidate-traces/v1" and
  (.scenarios | length) >= 16 and
  ([.scenarios[].id] | length == (unique | length)) and
  all(.scenarios[];
    .result.valid == .expected.valid and
    .result.error == .expected.error and
    .result.phase == .expected.phase and
    .result.current_head == .expected.current_head and
    .result.restart_heads == .expected.restart_heads and
    .result.selected_targets == .expected.selected_targets and
    ([.result.gate_history[].generator] == .expected.gate_generators)
  ) and
  ([.scenarios[] |
      select(.equivalence_group == "parallel-arrival-order") |
      .result.selected_targets[-1]] | unique | length) == 1 and
  ([.scenarios[] |
      select(.equivalence_group == "parallel-arrival-order") |
      .result.current_head] | unique | length) == 1 and
  any(.scenarios[];
    .id == "missing-factor-disposition-blocks-selection" and
    .result.error == "factor-dispositions-incomplete") and
  any(.scenarios[];
    .id == "review-cannot-run-on-intermediate-head" and
    .result.error == "review-dispatch-requires-reviewable") and
  any(.scenarios[];
    .id == "parallel-recovery-precedes-cut" and
    .result.valid == true) and
  any(.scenarios[];
    .id == "two-generator-direct-repair-gates-on-current-heads" and
    ([.result.gate_history[].generator] == ["generator-a", "generator-b"])) and
  any(.scenarios[];
    .id == "duplicate-gate-for-generator-is-rejected" and
    .result.error == "duplicate-direct-gate-generator") and
  any(.scenarios[];
    .id == "same-generator-exhaustive-repair" and
    .result.valid == true) and
  any(.scenarios[];
    .id == "initial-candidate-requires-complete-entry-proof" and
    .result.error == "candidate-entry-incomplete") and
  any(.scenarios[];
    .id == "candidate-proof-result-must-match-head" and
    .result.error == "candidate-entry-incomplete") and
  any(.scenarios[];
    .id == "candidate-proof-inventory-is-required" and
    .result.error == "candidate-entry-incomplete") and
  any(.scenarios[];
    .id == "candidate-proof-references-must-be-unique" and
    .result.error == "candidate-entry-incomplete") and
  any(.scenarios[];
    .id == "candidate-nonapplicability-requires-authority" and
    .result.error == "candidate-entry-incomplete") and
  any(.scenarios[];
    .id == "candidate-authorized-nonapplicability-is-reviewable" and
    .result.phase == "reviewable") and
  any(.scenarios[];
    .id == "one-generator-gate-spans-coherent-commits" and
    .result.valid == true) and
  any(.scenarios[];
    .id == "pre-gating-later-generator-is-rejected" and
    .result.error == "direct-repair-gate-predecessor-mismatch") and
  any(.scenarios[];
    .id == "mixed-generator-successor-is-representable" and
    .result.valid == true)
' "$fixture" >/dev/null

echo "actuating review candidate trace scenarios: pass"
