# A4 — Costs that grow with history: per-item logging on an event loop

**Source:** Python `asyncio` and `logging` behaviour (https://docs.python.org/3/library/asyncio.html, https://docs.python.org/3/library/logging.html); the ROS 2 logging path through `/rosout` (https://docs.ros.org/en/rolling/Concepts.html); numbers from [`constants.json`](../constants.json) by key · **Status:** teaching note; every measured value is illustrative.

## In one sentence
Most of the voice chain's full-stack delay is one logging loop: before it reacts to a turn, the dialogue engine writes one INFO line per conversation-history item on its asyncio thread, so the cost grows with history and the full stack multiplies it.

## What it measures
The metric is the speech recognizer's **transcript latency** p50: the time from the end of the user's utterance to the transcript on its topic. On the bench a stand-in for the cloud speech service fixes the first hops: it sends the transcript a fixed delay after the audio commit. The metric therefore measures the dialogue engine's handling after that commit. Inside the engine, the investigation also measures the **context loop**: the time from the engine's "context start" log line to its "context end" log line.

**Caution: these are bench conditions.** The conversation history grows to about 150 items (illustrative, `history_items`) because the bench does not reset it between conversations. The cloud speech service is a stand-in. Real sessions were not tested.

## How
**Mechanism, from code and log.** On every turn commit, the dialogue engine builds its context from the whole history. It then logs every input item at INFO level before it sends its request. Python logging goes to the ROS 2 client library: stdout plus one `/rosout` publish per line. The loop contains no `await`, so the asyncio thread does nothing else until the loop ends. The cost is items × cost per item: O(history).

Analogy: a clerk reads the whole customer file aloud before answering each new question.

**The factor.** No configuration flag removes these lines. The bench therefore mounts a `sitecustomize` module into the engine container; Python imports it at start-up. It adds a `logging.Filter` that drops only the per-item records. The message string is still built and the record still created; only the handler's emit is skipped. Two full-stack windows with the filter are compared with two plain full-stack windows, paired by turn number (so the history length is the same).

## Predicted
Written before the run: with the lines dropped, the transcript p50 returns near its alone value. The prediction is refuted if the engine's reaction (commit → request sent) stays long.

## Measured
Each value below is an illustrative measurement.

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Cost per history item, full stack | 1.5 ms | `ms_per_history_item` |
| History length | 150 items | `history_items` |
| Context loop, full stack | about 225 ms (my estimate from `ms_per_history_item` and `history_items`: 1.5 ms × 150) | — |
| Context loop, full stack with the filter | 10 ms | `context_build_ms_filtered` |
| Transcript p50: alone / full stack / full stack with the filter | 600 / 850 / 640 ms | `transcript_latency_ms` |

Before the filter, the loop is most of the engine's reaction time in every condition. The rest of the stack runs at its usual full-stack level during these windows, so the filter is the factor.

## The gap, and what it means
**Against the pre-registered outcomes:** the transcript p50 returns near alone (640 ms against 600 ms, illustrative, `transcript_latency_ms`). The refutation rule is not met: the remaining reaction is short. The prediction for the reaction itself is only "partly met": the fast mode matches, but some turns still wait before the context build.

**Why the full stack multiplies the cost.** In the full stack each item takes several times its alone time. Pool time-share times the same-work slowdown is enough to explain that step (see [[A1-cpu-queueing-on-a-shared-pool]] and [[A2-same-work-more-cycles]]). As a rough bound, a CPU-bound step on the pool takes about 4 to 6 times (3 × 1.4 ≈ 4.2; 3 × 2 = 6) its alone wall time (my estimate from `pool_wait_per_busy_full` and `cycles_growth_range`, both illustrative: (1 + 2.0) × (1 + 0.4 to 1 + 1.0)). No extra mechanism is needed.

**The transcript waits behind the loop (head-of-line).** The stand-in sends the transcript a fixed delay after the commit. In the full stack the loop is often still running at that moment, so the transcript callback waits; with the filter, it does not.

**What stays open.** The remaining reaction is bimodal, and the slow mode sits before the context build: commit → "audio committed" → context start. Its cause is open. The full stack + VLA step was not re-run with the filter.

The transcript gain is about 210 ms (my estimate from `transcript_latency_ms`: 850 − 640, unpaired windows).

## So what
- **Fix in the dialogue engine (recommendation):** make the per-item lines DEBUG with lazy `%` arguments or an `isEnabledFor` guard, or log one summary line, or move the logging off the event loop. A code change in the engine was not tested; only the handler-level filter was.
- **General lesson (interpretation):** any per-item work on a latency path grows with state, and contention multiplies it. Look for loops over history, queues or caches on an event-loop thread, and for logging inside them.

## Terms introduced
- **dialogue engine** — the service that decides how the robot replies; it runs an asyncio event loop.
- **context loop** — the dialogue engine's context build, from its "context start" log line to its "context end" log line.
- **transcript latency** — the speech recognizer metric, from the end of the utterance to the transcript on its topic.
- **O(history)** — a cost that grows in proportion to the number of conversation-history items.
- **event-loop thread (asyncio)** — the single thread that runs all callbacks of a Python asyncio program; a loop with no `await` blocks every other callback.
- **head-of-line wait** — the wait of a message that arrives while the thread is busy, until the current callback ends.
- **sitecustomize** — a Python module that the interpreter imports at start-up when it is on the module path; used here to install the log filter without changing the image.
