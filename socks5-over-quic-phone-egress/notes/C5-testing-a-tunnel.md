# C5 — Testing a tunnel

**Source:** internal test plan (unit, integration, end-to-end, manual checklist) and end-to-end test plan (executed cases, log checks, known behaviours), generalised; RFC 1928, RFC 9000. · **Status:** concept note. Test sizes are illustrative.

## In one sentence
Test the tunnel in four layers: pure unit tests for the byte formats and state machines, loopback integration tests that run a real QUIC client and server in one process, end-to-end tests over real networks that compare the exit address and break the network on purpose, and negative tests that must fail closed.

## What it is
A tunnel has three kinds of logic, and each needs a different test:

- **wire formats** (SOCKS5 messages, control-stream framing, config JSON): deterministic, so unit tests can cover every branch;
- **concurrency and timing** (streams, deadlines, backoff, the activity guard): need a real QUIC stack, but not a real network;
- **the world** (NATs, cellular, background rules, firewalls, UDP blocking): only real networks and real devices show it.

## How it works
**Layer 1 — unit tests** (internal test plan, generalised):

| Component | Cases |
|---|---|
| SOCKS5 encoder/decoder | every message type and address type; round trips; truncated input; wrong version; unsupported command; port byte order |
| control-stream reader | valid hellos per platform; missing fields; empty, malformed, oversized and slow messages; error-reply building |
| token store | unique per call; full length (`token_bits_illustrative`); expiry; single use (concurrent and after disconnect); device binding; grace period and its expiry |
| activity guard | busy refuses a swap; idle allows it; a fresh tunnel is protected; each relay direction alone keeps it busy |
| relay | data both ways; EOF on each side; write error; cancellation; idle timeout; a slow but active stream survives |
| config handler | enabled and disabled cases; each missing variable; feature flag off; port as a string; rate limit; no authentication gives 401 |
| phone SOCKS5 handler | negotiation; each address type; DNS failure → REP `0x04`; refused → `0x05`; each blocked range and port → `0x02`; a name resolving to a private address → `0x02` |
| pinner | match; mismatch; empty pin; hex case |
| tunnel manager | state transitions; disabled config; HTTP errors → failed; backoff schedule and cap; stop is idempotent |

**Layer 2 — loopback integration tests.** Server and client run on one host with a test certificate:

1. handshake plus control hello returns the port;
2. a SOCKS5 client through the listener reaches a local HTTP server, and the response arrives intact;
3. device B replaces device A; traffic then exits through B;
4. many concurrent connections (an illustrative 50) relay with no mixed data;
5. the stream cap: up to the cap succeed, one more fails fast, closing some frees the same number;
6. migration simulation: rebind the client's UDP socket during a relay;
7. pin mismatch after a server certificate change;
8. the same device reconnects and gets a clean tunnel with no stale streams.

**Layer 3 — end-to-end over real networks.** The source ran these on an instance with the full stack and on a phone simulator, an emulator and devices:

| Case | Steps | Pass condition |
|---|---|---|
| exit address | request a what-is-my-address service once through the proxy and once direct | the two addresses differ; the proxied one is the phone's |
| bypass works | send a chat message that calls the model API | no listener log line for cloud API hosts |
| app killed | kill the app; send a proxied request at once | success through the cloud IP within about one method-reply deadline |
| app restarted | relaunch | a new tunnel within a few seconds |
| second device | connect a second device after the guard window | the first gets `device_replaced`; traffic exits through the second |
| guard | connect a second device while traffic flows | the second gets `device_active`; the first is untouched |
| background / foreground | background the app; wait; return | disconnect after about one keepalive plus probe timeouts; reconnect on return |
| network toggle | airplane mode on and off | disconnected → connecting → connected; requests work after |
| feature off | disable the flag | config says disabled; the app makes no QUIC attempt; tools still work |
| pin tampered | alter the fingerprint in the config response | phone state "failed"; no proxied traffic |

**Latency** is measured, not assumed. The method: send an illustrative 200 sequential requests after an illustrative 10 discarded warm-up requests (`latency_test_requests_illustrative`), take p50 and p99, repeat with concurrent requests, and repeat on Wi-Fi and on cellular, including an IPv6-only carrier that reaches the front door through NAT64 ([[B3-who-dials-whom]]). Compare against the targets (`latency_target_illustrative`) and against the round-trip model in [[A1-the-end-to-end-picture]]. If p99 approaches a tool's default timeout, document it.

**Layer 4 — negative tests must fail closed:**

- a wrong fingerprint and a wrong ALPN value fail the handshake;
- an expired, reused or wrong-device token gets `invalid_token` before any listener work;
- every private range, a blocked port, a name that resolves privately, and every metadata encoding get REP `0x02` ([[C1-threat-model]]);
- a client that skips the Retry round trip does not get a handshake;
- excess concurrent handshakes are dropped.

**Cases worth adding** (my addition, not in the source's plans): a **captive portal**, where a hotel or café Wi-Fi intercepts traffic until the user accepts terms. UDP may be dropped and HTTPS redirected. Expected behaviour: handshake timeouts, the phone stops after its limit, and the agent continues on the cloud IP. Also a mid-transfer Wi-Fi → cellular handover on Android, which the source marks as unverified ([[C3-the-two-client-stacks]]).

**Write down known behaviours.** The source keeps a short list of things that look like bugs but are designed (end-to-end plan, generalised):

1. after an app kill, the first proxied request is slower by one method-reply deadline;
2. a backgrounded iOS app disconnects after a little more than one keepalive interval;
3. one client stack opens an internal stream first, so the first control-hello attempt times out and the next succeeds ([[B5-the-control-stream]]);
4. if the agent answers from memory and calls no tool, no traffic crosses the tunnel; test the tunnel with a direct request on the instance instead of through the agent.

**Separate test scaffolding from production rules.** The infrastructure test script seeded front-door parameters itself to exercise the boot path. The design notes say so explicitly, so that nobody reads the test as permission to set `ALL_PROXY` without a listener in production ([[A1-the-end-to-end-picture]]).

## How it is measured or used
Each acceptance criterion in the source names its test: for example, "the proxied exit address equals the phone's" traces to the exit-address case, and "a private destination gets REP `0x02`" traces to the handler's filter rows. A criterion without a named test is not done.

## Common confusions
- **"End-to-end tests can replace unit tests."** They cannot reach most branches, and a failure in them rarely says which layer broke.
- **"An emulator is a phone."** It shares the host's network. Background suspension, cellular NATs and real handovers need devices.
- **"Testing through the agent proves the tunnel."** The agent may not call a tool. Test the transport directly.
- **"Negative tests are optional."** For a proxy, the negative tests are the security tests.

## Why it matters for an agent service
A tunnel's worst failures are silent: packets dropped by a firewall, a filter that lets one encoding through, a fallback that hides a dead phone. Only tests that compare exit addresses, break networks and attack the filters make those failures loud.

## Terms introduced
- **loopback integration test** — a test that runs a real client and server over the local host's network stack.
- **end-to-end test** — a test over the real deployed path, from device to site.
- **negative test** — a test that passes only if the system refuses.
- **fail closed** — refuse service when a check cannot be completed.
- **captive portal** — a network that intercepts traffic until the user signs in or accepts terms.
- **known behaviour** — designed behaviour that looks like a bug, recorded so that nobody files it.
- **test scaffolding** — setup that exists only to exercise a code path in a test.
