# C6 — Tiers, combined runs, and attribution

**Source:** general measurement method, abstracted; co-tenancy behaviour from [[../jetson-orin-thor-metrics/notes/B6-cotenancy-interference-matrix|the sibling co-tenancy notes]]. · **Status:** concept primer, no measured numbers.

## In one sentence
After the solo runs, the benchmark builds up the full stack in workload tiers, measures the combined run, and compares it to the sum of the solos — the ratio is the interference factor — then judges each timing property against pre-set PASS/UNRESOLVED/FAIL bands and attributes the first limit to a resource, while watching for the case where the baseline is already saturated so the attribution classifier cannot fire.

## What it is
- **workload tiers** — a sequence of increasingly heavy stacks: today's default load, the next-generation load, plus manipulation, plus on-demand large models.
- **combined run** — the whole tier running at once, as opposed to the solo runs.
- **the interference factor** — the combined latency (or cost) over the solo sum for the same work.
- **"carries" criteria** — per-KPI PASS / UNRESOLVED / FAIL bands set before data.
- **first-limit attribution** — a pre-registered rule that names which resource ran out first.
- **the saturated-baseline failure** — the case where the reference condition is already at its limit, so the classifier cannot attribute cause.

## How it works
**From solo sum to combined stack.** The solo runs (see [[C2-solo-runs-and-levels]]) give each service's cost alone. Summing them predicts the stack's cost *if there were no contention*. The combined run measures the stack with contention. The two differ because the services share CPU, GPU, and the memory controller.

**The interference factor.** For a given KPI, the interference factor is the combined value over the solo baseline — combined latency over solo latency, or combined cost over solo cost. A factor of 1 means the co-tenants are free; a large factor means they fight. The sibling kit shows that same-class GPU tenants keep their aggregate throughput but pay the cost in tail latency ([[../jetson-orin-thor-metrics/notes/B7-aggregate-throughput|the sibling B7 note]]), and that a control loop's tail can inflate many-fold under a full roster ([[../jetson-orin-thor-metrics/notes/B8-cotenancy-real-shape-mix-ladder|the sibling B8 note]]) — so the interference factor is read per KPI, and the tail matters more than the mean.

**"Carries" criteria with bands.** Each timing property (control-loop misses, camera rate, perception rate, VLA rate) has a PASS band, a FAIL band, and an UNRESOLVED zone between them, all fixed before data (see [[C5-experimental-design]]). A cell **carries** only if every applicable criterion is PASS over its valid windows. Any FAIL means "does not carry"; any UNRESOLVED with no FAIL means "unresolved." The UNRESOLVED zone is honest about the cases the benchmark cannot call either way.

**First-limit attribution.** Beside the verdicts, a pre-registered classifier names the first resource to bind. A simple form: **CPU-pool** if the pool is near-fully busy and the losing service's rate drop coincides with rising run-queue wait; **GPU** if GPU-busy is near-saturated and the loser is a GPU tenant whose CPU did not rise; **memory** if the memory index is high and a CPU-only service loses with no CPU saturation; otherwise **none-observed**. A loss with no matching signal is **unattributed**.

**The saturated-baseline failure.** The attribution classifier compares a loaded condition to a reference. If the *reference* condition is already saturated — the CPU pool full even at the lightest tier — then adding load barely moves the signal the classifier keys on, and it reads "unattributed" even though the stack is clearly at its limit. This is a real and important failure mode: when the baseline is already at the wall, the classifier cannot tell you *what* hit the wall. The benchmark must report this honestly ("saturated at the lightest tier, classifier unattributed") rather than pretending the classifier found nothing.

**Architecture direction.** Interference flows from providers to consumers. A lower-layer service (the camera, the memory controller) affects the higher layers that consume it; a higher-layer service does not slow the lower layer it depends on. Attribution respects this direction: you test the consumers of what changed, not its providers.

## How it is measured or used in a benchmark
- **Build up the tiers; measure each combined run.** Default, next-generation, plus manipulation, plus on-demand large models.
- **Report the interference factor per KPI.** Combined over solo; read the tail, not just the mean.
- **Judge each KPI against its pre-set PASS/UNRESOLVED/FAIL band.** A cell carries only if all PASS.
- **Run the first-limit classifier.** Name CPU / GPU / memory / none-observed; mark unattributed losses.
- **Flag a saturated baseline.** If the lightest tier is already at the wall, say so and note the classifier cannot attribute.

## Common confusions
- **"The combined cost equals the sum of the solos."** Contention makes it larger; the ratio is the interference factor.
- **"Report the mean interference."** Co-tenancy often costs tail latency, not mean; read the tail.
- **"No PASS and no FAIL means it passed."** The UNRESOLVED zone is a distinct verdict; it means the benchmark cannot call it.
- **"The classifier found nothing, so nothing limits."** If the baseline is already saturated, the classifier reads unattributed by construction; report the saturation.
- **"Test everything that touches the changed service."** Test its consumers, not its providers; interference flows one way.

## Why it matters for robotics workloads
The whole point of the benchmark is this moment: the full stack running together, and the question "which resource gives first, and does the control loop survive?" The interference factor, the PASS/UNRESOLVED/FAIL bands, and the first-limit classifier turn that question into a defensible answer. And the saturated-baseline caveat is what keeps the answer honest when the robot is already at its limit before you even add the heaviest tier — a common and important outcome that a naive classifier would silently mislabel.

## Terms introduced
- **workload tier** — one of a sequence of increasingly heavy stacks (default, next-generation, plus manipulation, plus on-demand large models).
- **combined run** — the whole tier running at once, versus the solo runs.
- **interference factor** — combined value over solo baseline for a KPI; 1 means co-tenants are free.
- **"carries" criteria** — per-KPI PASS / UNRESOLVED / FAIL bands, fixed before data; a cell carries only if all PASS.
- **UNRESOLVED zone** — the band between PASS and FAIL where the benchmark cannot call the result.
- **first-limit attribution** — a pre-registered rule naming the first resource to bind (CPU / GPU / memory / none-observed).
- **unattributed** — a loss with no matching resource signal.
- **saturated-baseline failure** — when the lightest tier is already at the limit, so the classifier cannot attribute cause.
- **architecture direction** — interference flows from providers to consumers; test consumers, not providers.
