# Giving a cloud agent the user's own IP address: a SOCKS5 proxy tunnelled over QUIC through the phone — study notes

**Start here: the story** — [The house line](stories/01-the-house-line.html): a picture-first, interactive tour of the whole design in about ten minutes ([all stories](stories/INDEX.md)).

## In one paragraph

A cloud-hosted agent that browses and acts for a user is often blocked, because websites distrust
data-centre addresses. This kit teaches one answer: lend the agent the user's own address by sending
its TCP connections out through the user's phone. **Part A** frames the problem (IP reputation,
geo-fencing, why the user's phone and not a residential-proxy vendor) and walks one request end to end:
a tool reads `ALL_PROXY=socks5h://localhost:…`, a local passthrough listener puts the SOCKS5 bytes on a
new QUIC stream, the phone resolves the name and connects from its own network. **Part B** covers the
protocols: SOCKS5 byte by byte and why remote DNS matters; what QUIC gives (one-round-trip TLS 1.3,
independent streams, connection migration, keepalive through NAT) and why not TCP, WebSocket,
WireGuard or MASQUE; why the phone dials out and an anycast port-map front door reaches the private
instance; trust from a boot-time self-signed certificate whose fingerprint arrives over the existing
HTTPS channel; and the small control stream with its single-use token and one-device policy. **Part C**
makes it safe and operable: a layered threat model (SSRF into the home network, the cloud metadata
service, UDP amplification, admission, local processes), limits and deadlines with an invisible
fallback before the commit point, the iOS and Android client stacks, observability that never records
destinations, a four-layer test strategy, and rollout and rollback with the lessons learned. **Part D**
compares layer-3 tunnels with layer-5 proxies and asks when one platform team should own the data plane
for many callers. The kit carries no measured numbers; every number is a public protocol value or a
labelled illustrative figure (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). It assumes basic
networking (IP, TCP, UDP, NAT, TLS, DNS) and basic cloud concepts (instances, firewalls). It does not
assume any QUIC or SOCKS background.

## How to read these notes

Read Part A → Part B → Part C → Part D. Part A gives you the shape; Part B the protocols; Part C what it
takes to ship; Part D the alternatives. Each note starts with a one-sentence takeaway; a reader who
stops there still leaves with something true.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, how the internal material was generalised, the public sources, and the number rules.

### Part A — the problem and the shape of the answer
- [`notes/A0-why-the-users-ip.md`](notes/A0-why-the-users-ip.md) — IP reputation, CAPTCHAs and geo-fencing; phone egress versus a residential-proxy vendor; first release versus later phases; how success is measured.
- [`notes/A1-the-end-to-end-picture.md`](notes/A1-the-end-to-end-picture.md) — the two paths; one request from tool to site; a static environment with an always-on listener; `NO_PROXY`; the browser bridge; a round-trip latency model.

### Part B — the protocols
- [`notes/B1-socks5-in-ten-minutes.md`](notes/B1-socks5-in-ten-minutes.md) — method negotiation, `CONNECT` with IPv4 / domain / IPv6, reply codes, `socks5` versus `socks5h`, passthrough, authentication as a non-goal.
- [`notes/B2-quic-for-this-job.md`](notes/B2-quic-for-this-job.md) — 1-RTT handshake and 0-RTT off; stream types and IDs; stream caps; connection IDs, NAT rebinding and migration; idle timeout, keepalive and PTO; the alternatives.
- [`notes/B3-who-dials-whom.md`](notes/B3-who-dials-whom.md) — the phone dials out, the cloud opens streams; the anycast port-map front door; why not a load balancer; cost relations; two silent firewalls; NAT64; UDP-blocking networks.
- [`notes/B4-trust-without-a-ca.md`](notes/B4-trust-without-a-ca.md) — boot-time ECDSA P-256 certificate; fingerprint pinning over the control channel; ALPN as a gate; decoding QUIC close codes; rotation, compromise and stale mappings.
- [`notes/B5-the-control-stream.md`](notes/B5-the-control-stream.md) — the config call; the single-use device-bound token and its grace period; length-prefixed hello; four error codes; last writer wins with an activity guard.

### Part C — making it safe and operable
- [`notes/C1-threat-model.md`](notes/C1-threat-model.md) — the phone-side destination filter after DNS; the cloud-side metadata filter and its encodings; amplification and Retry; admission; local processes; the reputation the user carries.
- [`notes/C2-limits-and-failure-handling.md`](notes/C2-limits-and-failure-handling.md) — caps and deadlines; fail fast on stream exhaustion; backpressure; the handshake phase and the commit point; states; reconnection; UDP buffers.
- [`notes/C3-the-two-client-stacks.md`](notes/C3-the-two-client-stacks.md) — iOS Network.framework mapping; the Android library survey; msquic through a native bridge; protocol inversion as a reserve; migration per platform.
- [`notes/C4-observability-without-user-data.md`](notes/C4-observability-without-user-data.md) — counters, gauges and log fields; destinations opt-in only; classification at write time; attribution and kill switch; alerts; an on-call checklist.
- [`notes/C5-testing-a-tunnel.md`](notes/C5-testing-a-tunnel.md) — unit, loopback integration, end-to-end and negative tests; the latency method; captive portals; known behaviours.
- [`notes/C6-rollout-and-migration.md`](notes/C6-rollout-and-migration.md) — delivery slices; a fail-closed feature flag; idempotent environment-scoped scripts; the firewall migration; re-provisioning; rollback order; six lessons.

### Part D — alternatives and the platform view
- [`notes/D1-l3-versus-l5-tunnelling.md`](notes/D1-l3-versus-l5-tunnelling.md) — TUN and TAP; WireGuard and cryptokey routing; the transparency spectrum; why a layer-5 proxy is enough for TCP-only, proxy-aware agents; when layer 3 is right.
- [`notes/D2-a-platform-owned-data-plane.md`](notes/D2-a-platform-owned-data-plane.md) — caller-owned versus platform-owned; a CONNECT-style tunnel API; two tiers; failure and cost; multi-device routing and the transparent proxy with `iptables REDIRECT`.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, each with a source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why do sites block my agent, and why not just buy residential proxies? | [[notes/A0-why-the-users-ip]] |
| What path does one HTTPS request take, and what does it cost in round trips? | [[notes/A1-the-end-to-end-picture]] |
| Why doesn't the browser use `ALL_PROXY`? | [[notes/A1-the-end-to-end-picture]] |
| What bytes does SOCKS5 actually send? What does REP `0x02` mean? | [[notes/B1-socks5-in-ten-minutes]] |
| Why `socks5h` and not `socks5`? | [[notes/B1-socks5-in-ten-minutes]] |
| Why QUIC instead of WebSocket, TCP+TLS, WireGuard or MASQUE? | [[notes/B2-quic-for-this-job]] |
| Does the tunnel survive a move from Wi-Fi to cellular? | [[notes/B2-quic-for-this-job]], [[notes/C3-the-two-client-stacks]] |
| How does the phone reach a private cloud instance without a load balancer? | [[notes/B3-who-dials-whom]] |
| How can a self-signed certificate be trusted? What does close code `0x0128` mean? | [[notes/B4-trust-without-a-ca]] |
| How does the server know the phone is the user's? What if two phones connect? | [[notes/B5-the-control-stream]] |
| Could the agent reach my home router or the cloud's credentials through this? | [[notes/C1-threat-model]] |
| What does the agent see when the phone disappears mid-request? | [[notes/C2-limits-and-failure-handling]] |
| Why was Android so much harder than iOS? | [[notes/C3-the-two-client-stacks]] |
| What should we log, and what must we never log? | [[notes/C4-observability-without-user-data]] |
| How do I test a tunnel so that silent failures become loud? | [[notes/C5-testing-a-tunnel]] |
| In what order do we roll this out, and how do we roll it back? | [[notes/C6-rollout-and-migration]] |
| Should this be a VPN instead? | [[notes/D1-l3-versus-l5-tunnelling]] |
| When should one team run this for every agent service? | [[notes/D2-a-platform-owned-data-plane]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "the assistant service", "an agent service", "the phone app", "the agent runtime", "a global anycast UDP front door", "the partner tunnelling platform".
- Every number is public (an RFC, open-source documentation, a paper, or labelled arithmetic) or labelled illustrative; the backticked key after a number points into [`constants.json`](constants.json). No number is a measurement from a specific deployment.
- Internal material is cited only by its kind ("internal design", "internal test plan", "deployment runbook"), described in [`SOURCES.md`](SOURCES.md). "(my explanation)" and "my addition" mark reasoning that is mine, not a source's.
- Example addresses come from the documentation ranges of RFC 5737 and RFC 3849.
- `[[wikilinks]]` connect notes inside this kit (Obsidian-compatible).
