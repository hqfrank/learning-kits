# C1 — Threat model

**Source:** internal design (threat model, UDP DoS mitigation, phone-side destination filter, server-side metadata filter, listener security, residual abuse surface), passthrough and phone-handler implementations, generalised; RFC 9000 §8 and §21 (address validation, amplification, security considerations); RFC 9001 §9.2 (0-RTT replay); OWASP Server-Side Request Forgery Prevention Cheat Sheet; RFC 1918, 3927, 4193, 4291, 6598, 6890. · **Status:** concept note.

## In one sentence
The tunnel turns a phone into an internet exit and opens a public UDP port on a cloud instance, so the design defends five things in layers: the phone's own network (destination filter after DNS), the cloud's metadata service (a second filter in the cloud), the UDP port (address validation and handshake caps), the tunnel's admission (pin, ALPN, single-use token), and the listener (bound to localhost only).

## What it is
A **threat model** lists what an attacker could want, how they could reach it, and which control stops them. Five threats shape this design.

## How it works
**Threat 1 — an open proxy into the user's home.** Anything that can send a `CONNECT` through the tunnel can make the phone open a TCP connection. Without a filter, that includes the user's router admin page, a home NAS, or an office intranet on the phone's Wi-Fi. This is **server-side request forgery (SSRF)** with the phone as the victim's server (OWASP SSRF cheat sheet).

The control is the **phone-side destination filter**. The phone refuses with REP `0x02` (B1) any destination in these ranges (`blocked_ranges_ipv4`, `blocked_ranges_ipv6`):

| Range | Why |
|---|---|
| `10/8`, `172.16/12`, `192.168/16` | RFC 1918 private networks |
| `100.64/10` | RFC 6598 shared space (carrier NAT; also used by some overlay VPNs) |
| `169.254/16` | RFC 3927 link-local, including the cloud metadata address |
| `127/8`, `0/8`, `240/4` | loopback, "this network", reserved |
| `::1`, `fe80::/10`, `fc00::/7` | IPv6 loopback, link-local, unique-local |
| `::ffff:0:0/96` | IPv4-mapped IPv6: apply the IPv4 rules to the embedded address |

The phone also allows only destination ports 80 and 443 in the first release (`allowed_ports_illustrative`).

Order matters. The phone applies the filter **after** it resolves the name and **before** it connects, and it connects to the exact address it checked. A filter on the name alone fails to **DNS rebinding**: an attacker's name that resolves to `192.168.1.1` (OWASP SSRF cheat sheet). The IPv4-mapped rule closes a second gap: `::ffff:192.168.1.1` is the private address in IPv6 clothing.

**Threat 2 — stealing cloud credentials through the metadata service.** A cloud instance can fetch its own credentials from a link-local **metadata service** at `169.254.169.254` (`metadata_address`). A request that reaches it from the instance, through some proxy, could leak those credentials. The phone filter already blocks `169.254/16`, but the source adds **defence in depth** in the cloud: the listener parses the `CONNECT` destination before it opens any stream and refuses:

- IPv4 `169.254/16` and IPv6 `fe80::/10`;
- known metadata host names, compared case-insensitively;
- the same address written in other forms that some resolvers accept: decimal `2852039166`, hex `0xa9fea9fe`, octal `025177524776`, dotted octal `0251.0376.0251.0376`, dotted hex `0xa9.0xfe.0xa9.0xfe` (`metadata_address_encodings`, my arithmetic; these are the classic filter bypasses in the OWASP cheat sheet).

The source states the limits honestly. Short forms such as `169.254.43518` and names that resolve to the metadata address pass the cloud check. The phone's post-resolution filter is the authoritative guard; the cloud check catches common bypasses before any byte reaches the phone. The **direct fallback** path in the cloud applies the same post-resolution check in its dialer, so a name that resolves to a private address fails there too.

`NO_PROXY` keeps legitimate metadata and cloud-API traffic off the proxy entirely ([[A1-the-end-to-end-picture]]).

**Threat 3 — the open UDP port.** The QUIC port accepts packets from anywhere ([[B3-who-dials-whom]]). Two attacks follow.

- **Amplification.** An attacker sends a small Initial packet with a victim's address as source. If the server answered with its full certificate flight, it would amplify traffic toward the victim. RFC 9000 §8.1 limits a server to three times the bytes it received from an unvalidated address (`quic_amplification_factor`). A client's first datagram is at least 1200 bytes (`quic_min_client_initial_datagram`, RFC 9000 §14.1), so the budget for one Initial is 3600 bytes (my arithmetic, `quic_amplification_budget_one_initial`).
- **Handshake exhaustion.** Each handshake costs the server public-key work. A flood of Initials consumes CPU.

The design forces **address validation** on every new connection: the server first answers with a small **Retry** packet that carries a token, and does crypto work only when the client returns that token from the claimed address (RFC 9000 §8.1.2; the Retry carries a 128-bit integrity tag, `retry_integrity_tag`, RFC 9001 §5.8). The cost is one extra round trip on each new connection; the phone connects rarely, so that is cheap. The server also caps concurrent unvalidated handshakes (an illustrative 16, `max_unvalidated_handshakes_illustrative`) and total connections (an illustrative 4, `max_established_connections_illustrative`). 0-RTT is off, so a captured first flight cannot be replayed (RFC 9001 §9.2).

**Threat 4 — admission to the tunnel.**

| Who proves what | Mechanism | Note |
|---|---|---|
| Server to phone | pinned certificate fingerprint ([[B4-trust-without-a-ca]]) | stops a man in the middle |
| Protocol | private ALPN value | stops protocol confusion and casual scanners |
| Phone to server | single-use, short-lived, device-bound token ([[B5-the-control-stream]]) | checked before the connection is attached |

The residual risk: someone who reads the HTTPS config response gets a token and its device ID, and can open a tunnel within the token lifetime. They can then use the phone as an exit for public web ports only, because the phone filter still applies. A stolen fingerprint alone gives nothing; it is public.

**Threat 5 — a malicious or manipulated process on the instance.** The listener has no SOCKS5 authentication. It binds to `localhost`, so only processes on the same instance can reach it. In a single-user instance, those are the user's own agent and tools. A manipulated tool (for example, one steered by a prompt injection on a web page) can still send traffic through the phone. The phone filter and the port allowlist bound what it can reach. The same tool could read the QUIC private key, which shares its user account; the source accepts this and lists a separate service account as hardening. A fully compromised instance can do anything the agent can; the phone filter is then the last line.

**What the user carries.** Sites now attribute the agent's traffic to the user's address. Phone addresses are valuable for fraud, scraping and credential stuffing. The filters reduce the risk; they do not remove it. The source answers with per-user kill switches and attribution counters ([[C4-observability-without-user-data]], [[C6-rollout-and-migration]]).

## How it is measured or used
Negative tests are the evidence (internal test plan, generalised): `CONNECT` to each private range, to a blocked port, to a name that resolves to a private address, and to each metadata encoding must return REP `0x02`, and the cloud-side checks must open no QUIC stream. A malformed octet such as `999.1.1.1` must be forwarded and fail at DNS, not be mistaken for the metadata address. A Retry must be required. Excess handshakes must be dropped. Counters for blocked destinations and rejected tokens feed alerts ([[C4-observability-without-user-data]]).

## Common confusions
- **"The phone filter makes the cloud filter redundant."** It is redundant on purpose. Two filters in different code bases, on different platforms, rarely share a bug.
- **"Blocking `192.168.0.0/16` blocks the home router."** Only if the filter runs after DNS and covers IPv4-mapped IPv6 and the other private ranges.
- **"Retry stops all amplification."** A Retry is about the size of the Initial, so a factor near one remains. RFC 9000 accepts this.
- **"Localhost binding is authentication."** It limits who can connect to processes on the same host. It says nothing about which of those processes is trustworthy.

## Why it matters for an agent service
An agent is driven by text from the open web. Assume that some of that text will try to make the agent fetch a private address. The filters must hold even when the agent itself is the attacker's tool.

## Terms introduced
- **threat model** — a list of attacker goals, paths and the controls that stop them.
- **SSRF (server-side request forgery)** — making a server fetch a destination of the attacker's choice, typically an internal one.
- **destination filter** — the phone's check of each destination address and port before it connects.
- **DNS rebinding** — a name that resolves to a different (often private) address than a filter expected.
- **metadata service** — the link-local service from which a cloud instance reads its configuration and credentials.
- **defence in depth** — independent controls in layers, so that one failure does not expose the asset.
- **amplification attack** — using a server's larger replies to flood a spoofed victim address.
- **address validation** — proof that a client can receive packets at its claimed address.
- **Retry packet** — the QUIC server's stateless reply that carries an address-validation token.
