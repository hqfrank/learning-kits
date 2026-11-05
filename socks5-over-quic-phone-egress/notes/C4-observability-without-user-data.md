# C4 — Observability without user data

**Source:** internal design (operational observability, data model and classification, user-attributable observability, on-call runbook), QUIC server and passthrough implementations (session and routing metrics), generalised. · **Status:** concept note. Alert thresholds are illustrative design parameters.

## In one sentence
The tunnel reports counts, durations, byte totals and reasons for every connection, stream, handshake and refusal, but by default it never records where the agent went, because destination names are the user's browsing history.

## What it is
A proxy sees two kinds of information. **Operational data** says whether the system works: is a tunnel up, how many streams, how many failures and why. **User data** says what the user did: which sites, which pages. The design keeps the first and drops the second, and still leaves enough to answer "whose traffic was this?" when a site complains.

## How it works
**Counters and gauges** (internal design, generalised):

| Signal | Type | Labels | Answers |
|---|---|---|---|
| tunnel connected | gauge 0/1 | — | is a phone attached now? |
| tunnel connects / disconnects | counters | disconnect reason: idle, error, replaced, shutdown | how stable are tunnels? |
| tunnel duration | histogram | — | how long do sessions last? |
| session type | counter | initial or reconnect (same device back within a short window) | how often do phones reconnect? |
| streams active / total | gauge / counter | — | how much concurrency? |
| bytes relayed | counter | direction | how much traffic, each way? |
| requests routed | counter | tunnel or direct; consumer (tool or browser) | what fraction actually used the phone? |
| handshakes started / failed / retried | counters | failure reason: timeout, invalid, rate-limited | is someone scanning or flooding? |
| tokens rejected | counter | expired, invalid, wrong device | is someone replaying tokens? |
| stream limit hit | counter | — | is the stream cap too low? |
| destinations blocked | counter | — | is a tool trying private addresses? |

The "requests routed" counter is the honest launch metric: a connected tunnel that carries no traffic is not a success ([[A0-why-the-users-ip]]).

**Log events** carry identifiers that operators need and nothing more:

| Event | Fields | Deliberately absent |
|---|---|---|
| tunnel established | device ID, platform, port | — |
| tunnel disconnected | device ID, reason, duration, stream count | — |
| tunnel replaced | old device ID, new device ID | — |
| token rejected | reason | the device ID, because the token did not prove it |
| handshakes rate-limited | count | source addresses |
| destination blocked | destination port | the destination host name |

**Destination logging is opt-in.** Host names from `CONNECT` requests reveal browsing. They are omitted by default. A configuration flag turns them on for a specific debugging session (internal design).

**Classify data when it is written.** The source labels every stored item at the point of write (internal data model, generalised):

| Item | Where | Lifetime | Class |
|---|---|---|---|
| QUIC private key | disk, owner-only | instance | secret |
| certificate fingerprint | instance environment, memory | instance | internal (public-safe, but identifies the instance) |
| front-door mapping | parameter store, per user | instance | internal; the user-to-port pairing is the sensitive part |
| connection token | memory only | seconds | secret |
| active device ID | memory only | session | identity, internal |
| last-activity time | memory only | session | ephemeral, but a security input (the activity guard) |
| proxied stream state | memory only | one request | ephemeral; no content |

No new database tables exist. Everything about a live tunnel is memory-only.

**Attribution.** Once sites see the user's address, the user is blamed for anything the agent does there. An investigation needs to tie traffic to a device and a time. In the first release (internal design, generalised):

- attribution is **per instance**, not per chat session: the chat session ID never reaches the listener, because the agent runtime shares one environment across tool calls ([[D2-a-platform-owned-data-plane]]);
- token issuance is logged with the device ID and time, which ties each tunnel session to a device;
- the stream counters carry time and destination port.

**Controls that act on what is observed.**

- A per-user **kill switch**: the feature flag. Turning it off makes the config call return "disabled"; the tunnel ends at the next reconnect ([[C6-rollout-and-migration]]).
- No per-tool rate limit in the first release. The phone's stream cap bounds a flooding tool ([[C2-limits-and-failure-handling]]).
- No "requests sent through your phone" indicator for the user yet; it needs per-session attribution.

**Alerts** (illustrative thresholds, `alert_thresholds_illustrative`):

- handshake failures above an illustrative 200 per minute: scanning or a flood;
- token rejections above an illustrative 20 per minute: possible token theft;
- no tunnel for more than an illustrative 20 minutes during an active chat: a health problem;
- the front door's dropped-packet metric above its baseline during rollout: an instance not allowed or a wrong mapping.

**An on-call checklist** for "the tunnel does not work", in order (internal runbook, generalised): (1) call the config endpoint — "disabled" means a missing certificate, mapping or flag; (2) check that the QUIC socket is bound on the host; (3) list the front-door mapping for the instance's private address; (4) check that the host packet filter accepts the QUIC port above its final drop; (5) read the phone's logs for "connected", `invalid_token` or handshake failures; (6) read the handshake and token counters.

## How it is measured or used
Tests check that counters move: a successful and a failed handshake each increment the right counter; a blocked destination increments the blocked counter and logs only the port. The end-to-end checklist confirms that requests to the model API and other cloud services never appear in the listener's logs, which proves `NO_PROXY` works ([[A1-the-end-to-end-picture]]).

## Common confusions
- **"No host names means no debugging."** Reasons, ports, counts and durations solve most tunnel problems. Host names are needed rarely and can be enabled for one session.
- **"A device ID is harmless."** It links a tunnel session to one installation, and through push registration to a person. It is identity data, kept in memory and in logs only where needed.
- **"Rejected tokens should log the device."** The device ID in a rejected hello is unproven. Logging it would let an attacker write arbitrary IDs into the logs.
- **"Attribution needs content."** It needs who, when and how much, not what.

## Why it matters for an agent service
Phone egress spends the user's reputation. The operator must be able to answer "did our agent do this from your address?" without having stored the user's browsing. Designing the signals before launch, and classifying each one at write time, is what makes both possible.

## Terms introduced
- **operational data** — signals about whether the system works.
- **user data** — signals about what the user did, such as destinations.
- **gauge / counter / histogram** — a current value / a running total / a distribution of observed values.
- **disconnect reason** — the label that says why a tunnel ended (idle, error, replaced, shutdown).
- **attribution** — tying traffic to a device and a time for investigation.
- **kill switch** — a control that disables the feature for a user or for everyone without a deployment.
- **data classification at write time** — labelling each stored item's sensitivity when it is first written.
