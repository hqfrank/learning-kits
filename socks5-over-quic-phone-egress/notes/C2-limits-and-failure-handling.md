# C2 — Resource limits and failure handling

**Source:** internal design (resource limits, passthrough step table, phone-disconnect phases, error handling, process management, UX states), passthrough and tunnel-manager implementations, end-to-end test notes, task list (UDP buffer tuning), generalised; RFC 9000 §4 (flow control) and §10.1 (idle timeout); RFC 9002 §6.2 (PTO); quic-go wiki, "UDP Buffer Sizes". · **Status:** concept note. All limits and deadlines are illustrative design parameters.

## In one sentence
Every resource has a cap and every wait has a deadline, chosen so that a dead or busy phone is detected before the tool has received a single byte, which lets the listener fall back to a direct cloud connection invisibly; once the SOCKS5 reply has gone to the tool, the connection is committed, and a failure becomes an ordinary reset that the tool's HTTP client retries.

## What it is
A tunnel to a phone fails often and in many ways: the app goes to the background, the user walks out of Wi-Fi, the battery dies, a page opens fifty connections at once. This note lists the limits that bound the damage and the rules that decide what the agent sees.

## How it works
**Limits.**

| Resource | Limit (illustrative design parameter) | Enforced by |
|---|---|---|
| concurrent proxied connections | 64 streams (`phone_max_incoming_streams_illustrative`) | the phone's QUIC stream limit |
| phone-opened streams | 2 (`server_max_incoming_streams_illustrative`) | the server's QUIC stream limit |
| bytes in flight | per-stream and per-connection flow-control windows | QUIC flow control (RFC 9000 §4) |
| idle relayed connection | 120 s without a byte (`relay_idle_timeout_illustrative`) | a read deadline reset on every read |
| idle QUIC connection | 30 s (`conn_idle_timeout_illustrative`), keepalive every 10 s (`keepalive_illustrative`) | QUIC idle timeout (RFC 9000 §10.1) |
| control message | 512 bytes, 3 s (`control_msg_max_illustrative`, `control_payload_timeout_illustrative`) | the control-stream reader |

**Stream exhaustion fails fast.** When the phone's stream limit is reached, opening one more stream fails at once. The listener then answers the tool with REP `0x01` (general failure) and closes. It does not queue and it does not drop silently. The tool's HTTP client sees a proxy error and retries by its own rules. A counter records each case ([[C4-observability-without-user-data]]).

A browser is the stress case. One resource-heavy page reached an illustrative 50 concurrent streams (`heavy_page_concurrency_illustrative`) even after the bypass list. **Lesson from the source:** the design said that one phone QUIC stack offered no knob for the incoming stream limit. The shipped code found the knob, because the stack's small default limit killed the connection during a browser burst. Check the design against the shipped code, and test with a real browser page, not only with sequential requests.

**Backpressure comes free.** The relay copies with blocking reads and writes. If a site is slow, the phone stops reading from the QUIC stream; QUIC flow control then stops the cloud from sending; the cloud stops reading from the tool. No layer buffers without bound (my explanation of RFC 9000 §4 applied to this relay).

**The handshake phase and the commit point.** The listener's steps for one tool connection (internal design, generalised):

| Step | Action | Deadline (illustrative) | On failure |
|---|---|---|---|
| 1–2 | read method request; reply "no auth"; read `CONNECT` | — | close / REP `0x07` |
| 3 | cloud-side metadata filter | — | REP `0x02`, no stream |
| 4 | tunnel present? | — | no: direct connection |
| 5 | open a stream to the phone | 8 s (`stream_open_timeout_illustrative`) | direct connection |
| 6 | forward method request; read the phone's method reply | 3 s (`method_reply_deadline_illustrative`) | close stream; direct connection |
| 7 | forward `CONNECT`; read the phone's reply | 20 s (`connect_reply_deadline_illustrative`) | close stream; direct connection |
| 8 | relay both ways | 120 s idle | close both sides |

**The invariant:** in steps 5–7 the tool has received only the "no auth" reply. It is still waiting for its `CONNECT` reply, so the listener can switch to a direct connection without the tool noticing. After step 7 the tool starts its TLS handshake through the phone. Its TLS session is now bound to the phone's TCP connection to the site, so no fallback is possible; a failure is a reset.

Each deadline matches the work behind it. The phone answers the method request from memory, so 3 s is generous. The `CONNECT` reply waits for the phone's DNS (an illustrative worst case of 10 s, `phone_dns_worst_illustrative`) plus its TCP connect (an illustrative 8 s timeout, `phone_connect_timeout_illustrative`); the 20 s deadline exceeds their sum (my arithmetic: 10 + 8 = 18). Without these deadlines, a dead phone blocks each read until the QUIC idle timeout.

**What the tool sees when the phone goes away** (internal design, generalised):

| When | What the tool sees | Recovery |
|---|---|---|
| before the server notices (stale tunnel) | nothing; a short wait | the step 6 deadline fires; direct connection |
| during the handshake phase | nothing | direct connection |
| relay, idle connection | a hang, then a reset after the relay idle timeout | the HTTP client retries; the retry goes direct |
| relay, active transfer | a partial response, then a reset | the HTTP client retries on a new connection |
| after cleanup | an immediate direct connection | none needed |

The server notices a dead phone when the QUIC connection closes: the phone stops answering keepalives, the server's probes back off (RFC 9002 §6.2), and the idle timeout ends the connection. Detection therefore takes about one keepalive interval plus several probe timeouts (my explanation). The end-to-end tests in the source saw exactly this pattern for an app sent to the background: a delay of a little more than one keepalive interval, then a disconnect.

**States the agent can be in** (internal UX specification, generalised):

| Tunnel state | Agent behaviour | User-visible |
|---|---|---|
| connected | requests leave from the phone | nothing |
| connecting | requests use the cloud IP for now | nothing |
| disconnected (app closed, network lost) | cloud IP; strict sites may block | nothing |
| unavailable (no front door, no certificate, flag off) | cloud IP | nothing |

"Degraded" in practice means connected but failing: the stream cap is hit, or `CONNECT` replies fail. It shows up in counters, not as a separate state.

**Reconnection on the phone.** The phone's states are disconnected → connecting → connected, plus failed. It reconnects with exponential backoff (an illustrative 1, 2, 4 … 32 s, `backoff_illustrative`). Two rules from the implementation keep it sane:

- a tunnel that dies sooner than an illustrative 10 s (`short_lived_threshold_illustrative`) counts as a failure and grows the backoff, so a server that accepts and then drops cannot cause a request storm;
- a tunnel that lived longer resets the backoff and reconnects after a brief pause.

After an illustrative 4 consecutive handshake timeouts (`handshake_fail_limit_illustrative`), the phone stops: the network probably blocks UDP. It tries again when the user re-enters the chat or the network changes. The tunnel runs only during an active chat session in the foreground; leaving the chat or backgrounding the app stops it, and returning starts it.

**Process failure on the cloud side.** The QUIC handler recovers from panics, clears the tunnel and keeps the listener up. If the process dies, the service manager restarts it; the listener comes back with direct fallback until the phone reconnects. The environment never names a dead tunnel, because `ALL_PROXY` always points at the always-on listener ([[A1-the-end-to-end-picture]]).

**The kernel's UDP buffers.** Linux default socket buffers are small for QUIC. When they fill, the kernel drops packets silently. The quic-go project recommends raising `net.core.rmem_max` and `wmem_max` to 7 500 000 bytes (`quicgo_udp_buffer_recommended`). The source sets this persistently in the boot script, before the service starts.

## How it is measured or used
- **Stream-limit test:** open streams up to the cap; all succeed. Open one more; it fails at once with REP `0x01` and the others are unaffected. Close ten; ten new ones succeed (internal test plan, generalised).
- **Relay timeout tests:** no data for longer than the idle timeout closes both sides; data at intervals shorter than the timeout keeps a connection alive for many minutes.
- **App-kill test:** kill the app, immediately send a proxied request, and expect success within about one method-reply deadline, through the cloud IP. **Known behaviour:** the first request after a kill is slower by that deadline; that is the designed trade-off.
- **Backoff test:** consecutive failures produce the doubling schedule and stop at the cap.

## Common confusions
- **"Fallback to direct is always possible."** Only before the SOCKS5 reply reaches the tool.
- **"A longer deadline is safer."** A longer deadline makes every request after a phone failure slower. Each deadline should just exceed the legitimate worst case of the work it waits for.
- **"Queue requests when the stream cap is full."** A queue hides overload and adds latency to every tool. A fast failure lets the tool's own retry logic act.
- **"The idle timeout and the relay timeout are the same."** One ends the QUIC connection; the other ends one relayed TCP connection.

## Why it matters for an agent service
The agent should never wait on a phone that is not there. Fast detection, fast fallback and fast failure keep the agent's latency bounded; the commit point keeps the behaviour honest, because the design never pretends a broken TLS session can be rescued.

## Terms introduced
- **stream limit** — the maximum number of concurrent streams a peer may open.
- **flow control** — receiver-advertised limits on bytes in flight, per stream and per connection.
- **backpressure** — a slow consumer slowing the producer instead of growing a buffer.
- **handshake phase** — the listener steps before the SOCKS5 reply reaches the tool, during which fallback is invisible.
- **commit point** — the moment after which a connection is bound to one path and cannot fall back.
- **stale tunnel** — a tunnel the server still believes alive after the phone has gone.
- **exponential backoff** — retry delays that double up to a cap.
