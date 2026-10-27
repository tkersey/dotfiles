# Architecture-to-senses examples

These are invented, stipulated architectures—not observations of a user's code.
Use them to see the operation, not as a stock metaphor dictionary. Preserve a
user's requested sensory richness and adapt the representation to the artifact.

## Ports and adapters: an explanatory rendition

**Given:** domain logic calls explicit ports; adapters implement those ports for
external systems. The dependency rule excludes direct infrastructure imports
from the domain. No timings, security isolation, or failure rates are supplied.

**Rendition:** The domain is a resonant chamber with a few deliberately shaped
openings. Outside it, machinery clatters in different materials and tempos; each
adapter meets an opening with the right fitting. Inside, the architecture has a
recognizable acoustic shape even when the machinery outside changes. At a port,
your hand meets a defined edge rather than an exposed bundle of moving parts.

**Translation:** The chamber is the domain dependency boundary, the openings are
ports, and the fittings are adapters. Spatial separation expresses dependency
direction; the recurring acoustic shape expresses a stable domain-facing
contract; the tactile edge expresses a deliberate interaction surface.

**Limit:** This is not a claim of process isolation, interchangeable behavior in
all circumstances, or immunity to external failures. A dependency boundary can
still carry latency, errors, or leaked infrastructure semantics through a port.
No defect or refactor is required for this explanation to be useful.

## Synchronous pipeline and event fan-out: a fair comparison

**Given:** A performs three stages in request order and returns after completion.
B publishes an event; independent subscribers handle it, and acknowledgment means
publication rather than completion of every subscriber. Subscriber order and
end-to-end latency are unspecified.

**Rendition:** A feels like three linked gates: each click admits you to the next,
and the final release has a definite position. B feels like striking a bell in
a room with several listening alcoves: the initiating gesture is singular, but
its consequences unfold along different paths beyond your hand.

**Shared axes:** The gates and alcoves express dependency shape; clicks and
responses express completion boundaries. A makes completion feel contiguous;
B separates publication from downstream completion. Neither “clean clicks” nor
“resonance” makes an alternative intrinsically superior.

**Limit and implication:** Do not infer that B is faster, reliable, unordered, or
synchronized merely from the sound image. Choose using the required completion
contract, failure handling, observability, and measured workload—not the more
attractive rendition.

## Separate services, shared rhythm: a diagnostic hypothesis

**Given:** a dependency graph shows separate workers; timestamps show periodic
bursts. Average throughput alone does not establish spare capacity during bursts.

**Rendition:** The workers occupy separate rooms, yet their footsteps repeatedly
land on the same beat. The architectural space is separated; the activity is not
uniformly spread through time.

**Hypothesis, not finding:** aligned retry schedules might concentrate arrivals.
A shared scheduler, upstream batching, or periodic external work might also fit.
The rhythmic view suggests inspecting phase alignment before assuming sustained
capacity exhaustion.

**Discriminator:** inspect retry timing and upstream scheduling; in an authorized
controlled experiment, vary phase alignment while holding total offered work
comparable and measure burst concentration. Periodicity by itself does not prove
retry synchronization. The performance owner executes and judges the experiment.
