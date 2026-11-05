# B2 — QUIC for this job

**Source:** RFC 9000 (QUIC transport), RFC 9001 (QUIC-TLS), RFC 9002 (loss detection and congestion control), RFC 9308 (applicability of QUIC), RFC 8446 (TLS 1.3), RFC 9298 and RFC 9484 (MASQUE); internal design (transport and protocol alternatives, server configuration), generalised. · **Status:** concept note. Protocol numbers are from the RFCs; design limits are illustrative.

## In one sentence
QUIC gives this tunnel four things at once: TLS 1.3 encryption with a one-round-trip handshake, many independent streams on one connection so that each proxied TCP connection gets its own stream without head-of-line blocking, connection IDs that let the connection survive the phone's move from Wi-Fi to cellular, and a single UDP flow that is easy to keep alive through NAT.

## What it is
**QUIC** (RFC 9000) is a transport protocol that runs over UDP. It puts reliability, congestion control, encryption and stream multiplexing into one layer. The cryptographic handshake is TLS 1.3, carried inside QUIC frames (RFC 9001). This design uses raw QUIC streams, not HTTP/3.

## How it works
**Handshake.** A new QUIC connection completes its TLS 1.3 handshake in one round trip, then sends application data. TCP plus TLS 1.3 needs two round trips, and TCP plus TLS 1.2 needs three (`quic_handshake_round_trips`; RFC 9001 §4, RFC 8446 §2). QUIC also offers **0-RTT**: a resuming client sends data in its first flight. This design turns 0-RTT off. 0-RTT data has no protection against replay (RFC 9001 §9.2, RFC 8446 §8), and a replayed tunnel request is a real risk for a proxy.

**Streams.** A **stream** is an ordered, reliable byte sequence inside a connection. Each stream has its own flow control, and a lost packet delays only the streams whose data it carried. That removes **head-of-line blocking** across streams: one stalled download does not stall the other proxied connections. The two low bits of a stream ID give its type (`quic_stream_id_types`, RFC 9000 §2.1):

| Low bits | Type | First IDs (my arithmetic, `quic_first_stream_ids`) |
|---|---|---|
| `0x00` | client-initiated, bidirectional | 0, 4, 8 … |
| `0x01` | server-initiated, bidirectional | 1, 5, 9 … |
| `0x02` | client-initiated, unidirectional | 2, 6 … |
| `0x03` | server-initiated, unidirectional | 3, 7 … |

The phone is the QUIC client. Its first bidirectional stream is stream 0, the **control stream** ([[B5-the-control-stream]]). The cloud is the QUIC server. It opens one **server-initiated bidirectional stream** per proxied TCP connection (IDs 1, 5, 9 …). Each endpoint caps how many streams its peer may open with the `initial_max_streams_bidi` parameter and later `MAX_STREAMS` frames (RFC 9000 §4.6). The phone's cap is therefore the tunnel's concurrency cap (an illustrative 64, `phone_max_incoming_streams_illustrative`). The cloud's cap for phone-opened streams is tiny (an illustrative 2, `server_max_incoming_streams_illustrative`), because the phone opens only the control stream.

**Connection IDs and migration.** QUIC identifies a connection by a **connection ID** (up to 20 bytes in version 1, `quic_max_connection_id_len`), not by the address 4-tuple. When the phone's address changes, the server can still match packets to the connection. Two cases exist (RFC 9000 §9):

- **NAT rebinding:** a NAT on the path gives the same phone a new port. The phone did nothing.
- **Connection migration:** the phone deliberately moves to a new network, for example from Wi-Fi to cellular, and sends from the new address.

In both cases, the peer runs **path validation**: it sends a `PATH_CHALLENGE` with 8 random bytes (`quic_path_challenge_data`) and waits for a matching `PATH_RESPONSE` (RFC 9000 §8.2). Only the client migrates in QUIC version 1, which suits this design: the phone moves, and the cloud instance stays still.

**Idle timeout and keepalive.** Each endpoint advertises `max_idle_timeout`. The effective value is the smaller of the two, and never less than three probe timeouts (`quic_idle_timeout_min_pto_multiple`, RFC 9000 §10.1). A connection with no packets for that long closes silently. NATs and firewalls also forget idle UDP flows. RFC 9308 §3.2 tells applications to assume a NAT binding can expire after 30 s (`udp_nat_idle_assumption`); RFC 4787 asks NATs for at least 120 s, but many are shorter (`rfc4787_udp_mapping_timer`). The design sends a QUIC `PING` as a **keepalive** (an illustrative every 10 s, `keepalive_illustrative`) and uses an idle timeout of an illustrative 30 s (`conn_idle_timeout_illustrative`). Caution: RFC 9308 warns that pings more often than every 30 s cost power on mobile devices. This design accepts that cost only while a chat session is active.

**Loss recovery.** RFC 9002 declares a packet lost when a packet sent three packets later is acknowledged (`rfc9002_packet_threshold`) or after 9/8 of the RTT (`rfc9002_time_threshold`). The **probe timeout (PTO)** is the smoothed RTT plus four RTT deviations plus the peer's maximum acknowledgement delay; before any sample, the initial RTT is 333 ms (`rfc9002_initial_rtt`). PTO decides how fast a dead phone is noticed ([[C2-limits-and-failure-handling]]).

**Why not the alternatives** (internal design, generalised):

| Option | For | Against |
|---|---|---|
| One TCP + TLS connection per proxied connection | standard everywhere | a new two-RTT handshake per request; no migration |
| SOCKS5 over a WebSocket on the existing HTTPS control channel | no new port, no new cost, passes every firewall | all proxied connections share one TCP connection, so one loss stalls all; the connection dies on a network change; the HTTPS tunnel provider terminates the outer TLS and sees the destination names |
| WireGuard | mature, fast, 1-RTT | a network-level VPN; needs VPN permission on the phone; no streams; see [[D1-l3-versus-l5-tunnelling]] |
| MASQUE (RFC 9298 CONNECT-UDP, RFC 9484 CONNECT-IP) | an IETF standard on QUIC | needs a full HTTP/3 stack on both ends; the source found no ready server or mobile client for these methods; interoperability brings nothing when one team owns both ends |
| **Raw QUIC streams + SOCKS5 (chosen)** | streams, migration, one handshake | needs a UDP front door; fails where UDP is blocked |

The WebSocket option stayed as the documented fallback if UDP blocking turned out to be common.

## How it is measured or used
- **Loopback integration tests** (internal test plan, generalised): handshake with the right ALPN succeeds and with a wrong one fails; many concurrent streams relay without mixing data; the stream cap rejects one stream over the limit and recovers when streams close; rebinding the client's UDP socket to a new port keeps the relay running.
- **End-to-end:** handshake time on Wi-Fi and cellular, and per-request latency percentiles ([[C5-testing-a-tunnel]]).

## Common confusions
- **"QUIC means HTTP/3."** HTTP/3 is one application on QUIC. This design uses QUIC streams directly.
- **"Migration keeps the same exit address."** Migration keeps the tunnel alive. New connections to sites leave from the phone's new address, so a site can see a mid-session address change.
- **"Migration handles a server crash."** It handles a client path change only. A dead server means a new handshake.
- **"0-RTT is free speed."** It is free speed with replay risk. The tunnel reconnects rarely, so the saving is small and the risk is not.
- **"UDP always gets through."** Some guest and corporate networks drop UDP to non-standard ports. QUIC then fails at the handshake, with no error from the network.

## Why it matters for an agent service
An agent opens many short connections in bursts, often several at once for one browser page, from a phone that moves. Streams remove the cross-connection stalls, migration removes most reconnects, and one long-lived UDP flow is cheaper to keep alive than many TCP flows. The price is a UDP path into the cloud, which is the subject of [[B3-who-dials-whom]].

## Terms introduced
- **QUIC** — the RFC 9000 transport over UDP with built-in TLS 1.3 and multiplexed streams.
- **0-RTT** — data sent in a resuming client's first flight, before the handshake completes; replayable.
- **stream (QUIC)** — an ordered, reliable byte sequence with its own flow control inside a QUIC connection.
- **head-of-line blocking** — one lost packet delaying data that does not depend on it.
- **server-initiated bidirectional stream** — a stream the server opens and both sides write; stream IDs 1, 5, 9 …
- **control stream** — the first client-initiated bidirectional stream (ID 0), used here for device identification.
- **connection ID** — the identifier that ties QUIC packets to a connection independent of addresses.
- **NAT rebinding** — a NAT on the path changing the client's apparent address or port.
- **connection migration** — the client deliberately moving a QUIC connection to a new network path.
- **path validation** — the `PATH_CHALLENGE` / `PATH_RESPONSE` check of a new path.
- **idle timeout** — the time without packets after which a QUIC connection closes silently.
- **keepalive** — a packet sent only to keep a connection and on-path NAT state alive.
- **PTO (probe timeout)** — the RFC 9002 timer after which a sender probes for lost data.
- **MASQUE** — the IETF family of HTTP/3-based proxying methods (CONNECT-UDP, CONNECT-IP).
