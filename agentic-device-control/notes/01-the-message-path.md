# 01 — The message path: cloud → device → agent → result

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Android WorkManager guide, https://developer.android.com/topic/libraries/architecture/workmanager · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
A task travels from the cloud to the device as a message, passes four guards (validate, de-duplicate, lock, time-limit), runs in the agent graph, and always ends as exactly one result message back to the cloud.

## What it is
The message path has five stages.

1. **The cloud message channel (down).** A server sends a message to one device. The message carries a message ID, a session ID, a message type, and a payload with the natural-language task.
2. **The receiver.** A component on the device accepts the message and validates it.
3. **The work executor.** A background-work component runs the task outside the user interface. On Android-type devices this is a job scheduler such as WorkManager (Android WorkManager guide).
4. **The agent graph.** The graph runs the task ([[02-the-agent-graph]]).
5. **The cloud message channel (up).** The device sends one result message: a status, the execution time, and the task description.

The result status has four values: **SUCCESS**, **ERROR**, **BUSY**, and **TIMEOUT**.

## How it works
Each guard answers one question before the expensive work starts.

- **Validate.** Is the message well-formed and of a known type? If not, report ERROR at once.
- **De-duplicate.** Has this message ID been seen recently? Message channels can deliver one message twice. A de-duplication cache keeps recent message IDs for an illustrative 10 min. A second copy is dropped and does not run the task again.
- **Lock.** Is another task running? The device has one screen, so only one task can run at a time. An execution lock admits one task. A second task gets BUSY at once; it does not wait in a queue.
- **Time-limit.** Has the task run too long? A watchdog stops the task after an illustrative 5 min, cleans up, releases the lock, and reports TIMEOUT.

A session tracker groups several messages that belong to one conversation, by session ID.

**Idempotency** is the property that a repeated message has the same effect as one message. The de-duplication cache gives idempotency for exact repeats. It does not make the task itself idempotent: "add an item to the list" run twice adds two items. The cloud side must therefore not retry a task blindly after a lost result; it must first ask, or it must send tasks that are safe to repeat.

## Design choices and trade-offs
- **BUSY instead of a queue.** A queue hides load and lets stale tasks run minutes later on a changed screen. BUSY pushes the retry decision to the cloud, which knows whether the task is still wanted. The cost is that the cloud must implement retry with back-off.
- **A hard timeout.** An agent loop can stall: a model can repeat one wrong action. The timeout bounds cost and frees the device. Choose it from the task-time distribution, not by guess: a limit well above the slow tail of successful tasks (for example several times the illustrative 20 s simple-task time) stops runaways without killing slow successes.
- **Exactly one result per accepted task.** Every exit path (success, model error, exception, timeout) sends a result. A missing result is indistinguishable from a lost message, and the cloud then cannot decide whether to retry.
- **Privileged installation.** The device-side receiver needs permission to accept cloud messages and to capture the screen in the background. On a consumer device this usually means the agent is installed as a privileged system app, not as a store app. Short-lived cloud credentials are rotated on the device, never stored long-term.

## Common confusions
- **"De-duplication makes retries safe."** It makes exact message repeats safe. A retry with a new message ID runs the task again.
- **"BUSY is an error."** BUSY is a normal answer to concurrency. Count it separately from ERROR in every dashboard ([[09-evaluation]]).
- **"The timeout is a performance number."** It is a safety bound. A task that reaches it is a failure to investigate, not a slow success.

## Why it matters
Most production faults in a remote-control system are at the edges, not in the model: a message delivered twice, two tasks fighting for one screen, a task that never reports. Four cheap guards and a "one result per task" rule remove these faults before any model token is spent.

## Terms introduced
- **cloud message channel** — the service that carries messages from server to device (down) and from device to server (up).
- **work executor** — the background-work component that runs a task outside the user interface.
- **de-duplication cache** — a store of recent message IDs used to drop repeated deliveries.
- **execution lock** — a guard that admits only one task at a time on the device.
- **watchdog timeout** — a hard upper limit on task run time, after which the task is stopped and reported as TIMEOUT.
- **idempotency** — the property that doing an operation twice has the same effect as doing it once.
- **result status** — one of SUCCESS, ERROR, BUSY, TIMEOUT, sent once per accepted task.
