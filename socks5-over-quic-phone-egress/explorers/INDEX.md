# Explorers — rung 3 (learn-explorer)

Four single-file HTML explorers for the *socks5-over-quic-phone-egress* kit. Open one with a double-click, or
`open 01-socks5-connect-walkthrough.html`. They need no server, network or build step.

Each page inlines its parameters in a `<script type="application/json" id="params">` block, also shipped as `params.json`.
Every entry is copied verbatim (value, unit, class, source) from `../constants.json` by key. Nothing is retyped. Prose
numbers on the pages are filled from the same block. Values that only one page's model needs are named `page_*`. They are
class `illustrative` and their source starts "page model choice (not in constants.json)". The pure model sits between
`/*MODEL-START*/` and `/*MODEL-END*/` and runs unchanged under node. Its `selfTest(P, assert)` runs `console.assert` on the
page and in node, and the page prints the pass count above its sources table.

**This kit has no measurements.** Every number is `public` (an RFC value or arithmetic on one) or `illustrative` (a design
parameter, a round teaching value, or a page choice). There are no measured overlays. Sources: this kit's `notes/`,
`glossary.md` and `constants.json` only.

---

## Spec — 01-socks5-connect-walkthrough.html  (notes B1, A1, C1, C2)

```
Explorer: socks5h moves name resolution to the phone; socks5 leaves it in the cloud
Teaches:  One SOCKS5 CONNECT, byte by byte: method request and reply, the request with ATYP, the reply. The listener answers
          the method itself, applies a fixed cloud-side metadata check, opens server stream 1 and forwards the original
          bytes. The phone resolves (socks5h), filters the resolved address, connects, replies. The reply that reaches the
          tool is the commit point.
Inputs:   scheme socks5h / socks5; destination (12 names and literals: RFC 2606 names, RFC 5737 / 3849 addresses, private,
          IPv4-mapped, CGNAT, link-local, metadata in 4 spellings); port 443 / 80 / 22 / 8080; CMD CONNECT / BIND /
          UDP ASSOCIATE. Step with Prev / Next, the step slider, or ← → on the figure.
Outputs:  per step: the bytes with field names; headline: where the name was resolved, ATYP, request size, the reply the
          tool gets, whether a QUIC stream was opened, what the site sees.
          — encode_method_request_rfc1928_s3, encode_request_rfc1928_s4, encode_reply_rfc1928_s6,
          cloud_metadata_check_C1, phone_filter_C1 (after DNS), parse_inet_aton, simulate_01 (pure trace).
Picture:  a sequence diagram (tool, listener, phone, site) on cloud / user-side bands, built up step by step.
Cases:    socks5h to a name · socks5 to the same name · IPv6 literal · name that resolves to a home router · IPv4-mapped
          private · metadata in hex · metadata in short form · port 22 · BIND.
Overlays: none.
Out of scope: authentication (RFC 1929), the deadlines and direct fallback (named in the callout only), TLS after the reply.
```

Self-tests (29): every message size matches `socks5_message_sizes`, including 7 + L for a name. Port 4433 encodes as
`11 51`. Each of the five `metadata_address_encodings` decodes to `metadata_address`, and `999.1.1.1` is not an address.
The phone filter blocks 192.168.1.1, `::ffff:192.168.1.1`, `fe80::1`, 100.64.0.1 and port 22, and allows 203.0.113.5.
socks5h resolves on the phone and connects to the phone's answer. socks5 resolves in the cloud and connects to the
cloud's answer. The rebinding name is refused by the phone with either scheme. The hex spelling is refused in the cloud
with no stream. The short form `169.254.43518` passes the cloud list and is caught by the phone, as C1 says. BIND gets
`0x07` with no stream. All 144 input combinations (2 schemes × 12 destinations × 3 ports × 2 commands) end with exactly one reply to the tool.

## Spec — 02-streams-vs-connections.html  (notes B2, A1, C1, C2)

```
Explorer: QUIC streams combine one handshake with per-connection loss isolation
Teaches:  N proxied TCP connections carried three ways between cloud and phone: N separate TCP + TLS 1.3 connections
          (2 RTT each), one shared TCP connection (the WebSocket option; any loss stalls all N), or one QUIC connection
          with N streams (one handshake, a loss stalls only its own stream).
Inputs:   cloud-phone RTT 10–300 ms (rtt_cloud_phone_illustrative); loss 0–10 % (page_loss_02); N 1–64
          (phone_max_incoming_streams_illustrative); packets per connection 1–100 (page_packets_per_connection_02);
          tunnel warm, Retry on a cold start, SOCKS5 pipelining.
Outputs:  mean time to first byte per option = setup + A1 request path + P(stall) × stall time; expected stalled
          connections; handshakes on the cloud-phone leg.
          — ttfb_A1 (A1 model), stall_time_est = RTT × (1 + kTimeThreshold) (my estimate from RFC 9002 §6.1.2),
          p_any_loss = 1 − (1 − p)^k, compare_02, draw_02 (seeded draw, common random numbers).
Picture:  stacked bars (handshake / request path / expected stall, hatched) per option; one seeded draw as N squares per
          option (filled red with × = stalled, hollow green = not).
Cases:    heavy page on cellular (heavy_page_concurrency_illustrative) · light page with bypass list · no bypass list ·
          cold start on cellular · one request, no loss.
Overlays: none.
Out of scope: congestion control and windows, loss on the phone-site leg, bandwidth, the stream cap's REP 0x01.
```

Self-tests (16): `ttfb_A1` reproduces all five `ttfb_model_illustrative` values (320, 600, 270, 480, and 60 direct). TCP +
TLS 1.3 costs one RTT more than a new QUIC handshake. The stall estimate at 50 ms is 106.25 ms. With no loss there are no
stalls. The stall formulas hold at 1 % loss. Shared TCP stalls more connections than QUIC, and QUIC stalls as many as
separate connections. With N = 1, sharing changes nothing. A cold start costs 2 RTT with Retry and 1 RTT without. The
seeded draw stalls the same connections for QUIC and for separate connections, and all-or-none for shared TCP.

## Spec — 03-migration-and-idle-timeout.html  (notes B2, C2, C3, C5)

```
Explorer: The tunnel survives a Wi-Fi → cellular switch only if the phone migrates before the idle timer runs out
Teaches:  The connection closes silently after idle-timeout seconds without a packet. A migrating stack carries the
          connection to the new network if the outage ends in time. A non-migrating stack leaves it on the dead path
          until the timer kills it, then reconnects with backoff. Keepalive must be below the NAT binding timeout
          (the cloud opens the streams) and well under the idle timeout.
Inputs:   idle timeout 5–120 s; keepalive 1–60 s; NAT binding 15–300 s; switch time 5–80 s; outage 0–60 s
          (page_timeline_03); migration on/off; active transfer on/off.
Outputs:  connection survived / closed n times; relayed stream survives or reset time; time down; time stale (server
          still believes up); longest NAT-expired stretch (compared with stream_open_timeout_illustrative); keepalives
          per minute. — simulate_03 (50 ms time steps; backoff_illustrative, short_lived_threshold_illustrative;
          reconnect handshake = 1 RTT + 1 Retry RTT).
Picture:  timeline lanes: network (Wi-Fi / outage / cellular), keepalives (delivered ● / lost ○), the server's idle timer
          as a sawtooth against the dashed timeout, tunnel state (up / NAT expired / stale / down) with event symbols,
          and the relayed stream.
Cases:    migrating stack, short gap · non-migrating stack · long outage · idle tunnel, medium gap · active transfer,
          medium gap · keepalive slower than the NAT · keepalive ≥ idle timeout.
Overlays: none.
Out of scope: PTO and RTT inside the idle timer, path-validation timing, the per-stream relay idle timeout.
```

Self-tests (12): the design keepalive is below the RFC 9308 NAT assumption and at most one third of the idle timeout. A
migrating stack survives a 3 s gap. A non-migrating stack closes at 40 + 30 s and reconnects after the initial backoff
plus 2 RTT. A long outage closes the connection even with migration, and the phone reconnects when cellular is up. With
a 28 s gap the idle tunnel closes and the active transfer survives. A 45 s keepalive behind a 30 s NAT survives by
rebinding, but leaves the phone unreachable for longer than the stream-open timeout. A keepalive ≥ the idle timeout
closes the connection with no switch at all.

## Spec — 04-amplification-and-retry.html  (notes C1, B2, B3)

```
Explorer: The 3× limit caps what a spoofed Initial can reflect; a Retry token cuts it below 1× and keeps the handshake
          slots for real phones
Teaches:  Before address validation a server sends at most 3× what it received (RFC 9000 §8.1). A stateless Retry with a
          token removes the server's work and state for spoofed sources. The handshake cap alone protects the CPU but
          locks out real phones under a flood. The Retry costs a real phone one round trip.
Inputs:   Initial size 600–1500 B (quic_min_client_initial_datagram); server first flight 500–12 000 B (page_flight_04);
          Retry on/off; token 16–200 B (page_retry_token_04); spoofed rate 1–100 000 /s, log scale (page_flood_rate_04);
          the phone's network (rtt_cloud_phone_illustrative).
Outputs:  bytes out ÷ bytes in per spoofed Initial; victim and attacker bytes per second; crypto handshakes started by
          spoofs; slots busy of max_unvalidated_handshakes_illustrative (each held page_abandoned_handshake_04 s);
          the real phone's extra round trips. — amp_budget_rfc9000_s8_1, retry_size_rfc9000_s17_2_5 (1 + 4 + 1 + CID
          + 1 + CID + token + 128-bit tag, worst-case 20-byte CIDs), analyse_04.
Picture:  bars per spoofed Initial (received, full flight, sent without Retry, sent with Retry) inside the dashed 3× budget;
          two sequence diagrams: the spoofed Initial (attacker, server, victim) and the real phone (phone, server).
Cases:    design, Retry on under a flood · no Retry, same flood · no Retry, long chain, light probing · Retry on, long
          chain · undersized Initial.
Overlays: none.
Out of scope: the server's own flood detection, connection-ID routing at the front door, 0-RTT (off in the design).
```

Self-tests (12): 3 × 1200 = 3600 = `quic_amplification_budget_one_initial`. A 5000-byte flight sends 3600 bytes (factor
3) and costs a real phone one extra round trip. A 1500-byte flight fits (factor 1.25). An Initial under 1200 bytes is
dropped. The Retry is 127 bytes for a 64-byte token, with a factor below 1 and no crypto work. The Retry costs exactly one
round trip. Without a Retry a flood fills every slot and locks out the phone, and the cap bounds reflection to cap ÷
lifetime flights per second. With a Retry under the same flood there is no lock-out. A 1500-byte Initial raises the
budget to 4500.

---

## Points for the notes (found while building; the notes were not changed)

- **C1, Retry size.** C1 says a Retry "is about the size of the Initial, so a factor near one remains". From the fields
  in RFC 9000 §17.2.5, a Retry with worst-case 20-byte connection IDs and a 64-byte token is 127 bytes, about 0.11× a
  1200-byte Initial. "At most about one" would be accurate. Explorer 04 says so in a callout.
- **`keepalive_illustrative` source text.** It says "below one third of `conn_idle_timeout_illustrative`", but 10 s is
  exactly one third of 30 s. Explorer 03's self-test checks "at most one third".
- **Needs a constants entry.** The `page_*` values (resolver answers, loss rates, packets per connection, the
  switch timeline, flight sizes, token length, flood rate, abandoned-handshake lifetime) are page choices. If the video
  rung reuses them, move them to `constants.json` as `illustrative`.

## Verification

- Node, all four pages: 69 self-tests pass (29 + 16 + 12 + 12). Inline params deep-equal `params.json` and
  `constants.json`. A model sweep over every slider and option extreme (pages 02–04) gave 320 outputs, none of them non-finite.
- Browser (Playwright, Chromium), every range at min and max (one at a time and all together) × every checkbox, select
  and radio combination: 1 320 page states, with no NaN, Infinity, undefined or null in the text and no console errors.
- `learning/stories/tools/shoot.py` on each page at 1280 px and 390 px: no console errors, no failed asserts, no
  overflow. Scenes: 01 steps through the trace (`seq`) and through the 9 cases (`out`). 02, 03 and 04 step through
  their cases.

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-socks5-connect-walkthrough.html` | SOCKS5 bytes; `socks5h` = DNS on the phone; filters after DNS; commit point | scheme, destination, port, CMD, step | B1, A1, C1, C2; RFC 1928 |
| `02-streams-vs-connections.html` | one handshake + per-stream loss isolation | RTT, loss, N, packets, warm, Retry, pipelining | B2, A1; RFC 9000/9001/8446/9002 |
| `03-migration-and-idle-timeout.html` | migration vs idle timeout; keepalive < NAT < idle ordering | idle, keepalive, NAT, switch, outage, migration | B2, C2, C3; RFC 9000 §9–10, RFC 9308 |
| `04-amplification-and-retry.html` | the 3× limit, Retry tokens, the handshake cap | Initial, flight, Retry, token, rate | C1, B3; RFC 9000 §8, §14.1, §17.2.5 |
| `params.json` | the constants the pages load | — | `../constants.json` + `page_*` choices |
