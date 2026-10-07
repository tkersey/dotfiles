# Measure feedback dynamics

Use in the existing performance route when backlog growth, oscillation, repeated
correction, or adaptive allocation makes feedback timing or policy-dependent
exposure material to the result. Reuse the baseline, protected contract,
experiment, and outcome report.
This is not a queueing primer, startup checklist, controller framework, or new
permission to run load. A stateless CPU hotspot stays on its ordinary route.

## Explain the observed time pattern

Identify the accumulating state and its units, initial condition, material inflows
and outflows, and decisions that regulate them. Trace how a response changes the
condition that elicited it. A plausible loop diagram is a hypothesis, not evidence
of its strength or dominance. Distinguish fixed shortage, demand variation, and
measurement noise from feedback amplification.

Separate three timings when they matter:

| Timing | Evidence to bind |
|---|---|
| Observation delay | Which state/policy generated the signal, its age, and aggregation/smoothing |
| Adjustment time and strength | How often the policy changes and how much it corrects each discrepancy |
| Action-to-effect delay | Startup, delivery, execution, or propagation before the correction changes the observed state |

Account for actions already issued but not yet reflected in feedback. A supervisor
that requests more workers while prior requests are still starting can overshoot;
a router can react to outcomes generated under the policy it has already replaced.
Inspect pending-state representation and observation attribution before prescribing
cooldowns. Faster sensing or adjustment, greater concurrency, and stronger correction
are candidates whose direction must be established, not default improvements.

## Choose a discriminating comparison

Name the response predicted by the mechanism and a comparison that could reject
it. Use an authorized replay, source argument, or representative experiment with
the relevant disturbance and horizon. Compare settling, overshoot, recovery, and
the accepted task outcome only when implicated; do not impose every metric.

Cover the supported regime where the controlling relationship may change, such as
before and after a shared dependency saturates. Include in-flight work in the
observation horizon so unfinished corrections cannot masquerade as improvement.
Preserve the baseline's target lineage; a degraded recent result does not silently
revise the accepted target. Keep finite observations distinct from stability proof.

An equivalent faster pure function under unchanged demand does not need damping.
A larger delay is not inherently stabilizing, and delay is not the universal cause
of oscillation. Stop extending the model when another variable cannot distinguish
the candidate, or report the specific unmeasured response.

## Separate reserves, sustainable rates, and induced demand

For a resource-dependent result, distinguish initial reserve, replenishment,
consumption, and recovery. A larger token bucket or queue may absorb a burst while
leaving sustained capacity unchanged. A short run that spends reserves cannot
establish sustainable throughput; a finite job may legitimately need only a finite
budget. Retain the required disturbance/recovery range when removing buffers.

If an optimization removes a cost, delay, or declining yield that regulates demand,
ask whether the resulting demand changes the gain. Isolate the local effect under
comparable admitted demand, then inspect the actual induced workload when material
and authorized. Preserve necessary regulation explicitly if its incidental owner
disappears. Without a supported demand response, do not invent a rebound penalty.

## Account for policy-dependent exposure

When success determines future task/resource allocation, check whether early
selection also supplies easier tasks, more samples, or warmer caches. Raw success
totals may then reward the allocation history. Use the existing matched comparison
to distinguish configuration capability from the deployed allocation effect;
state which of those is the actual objective. Real cache affinity can be a valid
policy benefit rather than a nuisance to erase.

Control or explicitly model assignment, workload, cache state, and delayed policy
attribution only as needed to reveal a decision-changing alternative. A matched
replay or controlled sample can suffice; require neither permanent equal allocation
nor a general exploration policy. Keep all-attempt costs, quality, and existing
holdout/authority rules. No provider-specific retention or routing constants follow
from this model.

Source: Donella H. Meadows, *Thinking in Systems: A Primer*, edited by Diana
Wright, Earthscan, 2009: delays pp. 51-58 (faster adjustment worsens the inventory
example on pp. 56-57); resources and changing feedback pp. 59-72; resilience
pp. 76-78; goal erosion pp. 122-123; success to the successful pp. 127-130;
buffers/delays/feedback pp. 149-156. These are engineering adaptations, not
numerical reproductions of the book or measured improvements to an agent.
