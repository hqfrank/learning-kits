# Sources — SOCKS5 over QUIC through the user's phone

This kit teaches a general design. It carries no measured numbers from any specific product,
deployment or test run.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one
question: **how do you give a cloud-hosted agent the user's own IP address, by tunnelling its TCP
connections through the user's phone, and how do you make that safe and operable?** Part A covers the
problem and the shape of the answer. Part B covers the protocols: SOCKS5, QUIC, who dials whom, trust
without a certificate authority, and the control stream. Part C covers safety and operations: the
threat model, limits and failure handling, the two phone stacks, observability, testing, and rollout.
Part D covers the alternatives: layer-3 tunnels, and a platform that owns the data plane for many
callers.

## Provenance of the method

The engineering ideas — the passthrough listener and its commit point, remote DNS through `socks5h`,
the reverse stream pattern, the anycast port-map front door, boot-time certificates with a pinned
fingerprint, the single-use device-bound token, the activity guard, the two-layer destination filter,
the deadlines and fallback rules, the client-library survey, the rollout and rollback order, and the
platform-owned data plane — are abstracted from **internal design, test and deployment documents and
the implementation of a phone-egress proxy feature for an agent service, 2026**. No internal material
is reproduced. No project, product, company, partner, person, host, account, address, port mapping or
internal identifier from those documents appears here. Diagrams in those documents are not copied,
traced or described.

The internal material is cited in the notes only by its kind ("internal design", "internal test plan",
"deployment runbook"), so that each claim can be traced to its kind of source without naming it:

| Kind | What it covered |
|---|---|
| requirements | the problem, goals, non-goals, user flows, acceptance criteria, later phases |
| design | architecture, server, control-stream protocol, passthrough listener, browser bridge, certificates, config API, both phone clients, the front door, network isolation, data model, rollback, security, error handling, user-experience states |
| Android transport follow-up | the client-library survey, cross-compilation, native bridge, the protocol-inversion fallback |
| test plan and end-to-end test plan | unit, integration, end-to-end and manual cases; known behaviours |
| deployment runbook, deploy automation, firewall-migration runbook | rollout steps, verification, teardown, known issues |
| task list | the delivery slices and their order |
| platform proposal (request for comments, high-level design, demonstration design) | the platform-owned data plane, caller API, fleet tiers, cost reasoning, protocol selection |
| analysis of a partner tunnelling platform | layer-3 tunnelling concepts and the layer mismatch |
| implementation (server, listener, SOCKS5 codec, phone tunnel manager, SOCKS5 handler, pinner) | exact mechanics |

## Number rules

Every number in this kit is one of two classes, recorded in [`constants.json`](constants.json):

1. **public** — a value from an RFC, open-source documentation or a published paper, or arithmetic on
   such values. Arithmetic is labelled "my arithmetic" in `constants.json` and in the prose.
2. **illustrative** — a round value invented to teach a relation or a design choice. Design limits
   (ports, timeouts, stream caps, token lifetimes, rate limits, backoff) are illustrative with source
   "design parameter". Product, test, cost and size figures are illustrative values of the same order
   of magnitude as the internal ones, chosen not to equal them, and they keep only the relation the
   internal figure taught (a ratio, a direction, an ordering). The prose says "an illustrative …" every
   time. **An illustrative number is never a measurement.**

Key names in backticks in the notes (for example `phone_max_incoming_streams_illustrative`) point into
`constants.json`. Every example address comes from the documentation ranges of RFC 5737 and RFC 3849.
The two design ports (`quic_listen_port_illustrative`, `socks_listen_port_illustrative`) are kept as
illustrative design parameters.

## Public sources cited

QUIC and TLS:

- RFC 9000, *QUIC: A UDP-Based Multiplexed and Secure Transport* (streams and stream IDs §2.1, flow
  control §4, handshake §7, address validation and amplification §8, migration §9, idle timeout §10.1,
  Initial size §14.1, packet formats §17, frames §19, error codes §20, security §21).
- RFC 9001, *Using TLS to Secure QUIC* (handshake §4, error mapping §4.8, Retry integrity §5.8, ALPN
  §8.1, 0-RTT replay §9.2).
- RFC 9002, *QUIC Loss Detection and Congestion Control* (thresholds §6.1, PTO §6.2, initial window §7.2).
- RFC 9308, *Applicability of the QUIC Transport Protocol* (NAT timeouts and keepalives §3.2).
- RFC 8446, *TLS 1.3*; RFC 7301, *ALPN*.
- The IETF QUIC-LB draft, *QUIC-LB: Generating Routable QUIC Connection IDs*.
- RFC 9298 (CONNECT-UDP) and RFC 9484 (CONNECT-IP), the MASQUE proxying methods.
- RFC 9113, *HTTP/2* (§8.5, the CONNECT method).

Proxying and DNS:

- RFC 1928, *SOCKS Protocol Version 5*; RFC 1929, *Username/Password Authentication for SOCKS V5*.
- curl documentation, "SOCKS proxy" (`socks5://` versus `socks5h://`):
  https://everything.curl.dev/usingcurl/proxies/socks.html
- Chromium source tree, `net/docs/proxy.md` (SOCKSv5 always resolves proxy-side; bypass-list syntax;
  implicit bypass of localhost and link-local).
- RFC 8484, *DNS Queries over HTTPS* (the alternative not chosen).

Addresses and NAT:

- RFC 1918, RFC 3927, RFC 4193, RFC 4291, RFC 6598, RFC 6890 (private, link-local, unique-local,
  shared and special-purpose ranges); RFC 5737 and RFC 3849 (documentation ranges).
- RFC 4787 (NAT UDP mapping timer); RFC 8085 (UDP usage guidelines, keepalive intervals).
- RFC 6052 (NAT64 well-known prefix).
- OWASP, *Server-Side Request Forgery Prevention Cheat Sheet* (post-resolution checks, DNS rebinding,
  alternative IP encodings).

Tunnels and Linux networking:

- J. A. Donenfeld, "WireGuard: Next Generation Kernel Network Tunnel", NDSS 2017 (handshake, timers,
  cookie reply, message format).
- wg(8) manual page (AllowedIPs, endpoint roaming, PersistentKeepalive).
- Linux kernel documentation, "Universal TUN/TAP device driver" (`Documentation/networking/tuntap.rst`).
- iptables-extensions(8), the `REDIRECT` target; the `SO_ORIGINAL_DST` socket option.

Libraries and platforms:

- quic-go documentation and wiki, "UDP Buffer Sizes":
  https://github.com/quic-go/quic-go/wiki/UDP-Buffer-Sizes
- msquic documentation (API table, connection and stream events, MIT licence).
- Apple Network.framework documentation (`NWConnectionGroup`, `NWMultiplexGroup`,
  `NWProtocolQUIC.Options`, `NWParameters.multipathServiceType`).
- FIPS 180-4 (SHA-256).

## How the material was read

The internal documents and source files were read in full as text. Only the generic mechanism, the
reasoning behind each choice, the trade-offs, the failure modes and the lessons were carried over.
Every internal number was replaced by an illustrative value or dropped; every name was replaced by a
role. Points where the sources disagree were resolved as follows:

- The phone's incoming stream cap appears with two different values in different sections, and the
  design says one phone stack offered no knob for it while the shipped code sets that knob. The kit
  uses one illustrative cap and teaches the disagreement as a lesson ([[notes/C2-limits-and-failure-handling|C2]]).
- The source's latency budget counts four cloud-to-phone message legs for the SOCKS5 set-up. The kit
  counts round trips explicitly in a labelled model ([[notes/A1-the-end-to-end-picture|A1]]).
- One octal spelling of the metadata address in a test table does not decode to that address. The kit
  uses the value computed from the address (`metadata_address_encodings`).
- The design lists a cap on established connections that the server source file does not show; the kit
  presents it as a design parameter.

Where a statement is my own reasoning rather than a source's, the note says "(my explanation)" or
"my addition".

## Public-safety check

Before hand-off the kit was scanned with the repository's public-content scanner
(`tools/public-scan.sh`) and with the generic name check from the kit brief. Both returned no hits.

## Rung 2 — diagrams

`diagrams/` (six pages, see `diagrams/INDEX.md`) was drawn from this kit's own notes A1, B1–B5,
C1 and C2 and from `constants.json` only. Every number on a canvas is loaded from `constants.json`
by key and tagged public or illustrative. No source figure was copied or traced.

## Rung 3 — explorers

`explorers/` (four single-file pages, see `explorers/INDEX.md`) was built from this kit's notes A1, B1, B2, B3, C1, C2,
C3 and C5, `glossary.md` and `constants.json` only. Each page's parameters are copied verbatim from `constants.json` by
key into an inline block and into `explorers/params.json`. Values that only one page's model needs are named `page_*`,
are class `illustrative`, and have the source "page model choice (not in constants.json)". The pages carry no
measurements and no measured overlays. Public protocol values are cited to RFC 1928, RFC 9000, RFC 9001, RFC 9002,
RFC 8446, RFC 9308, RFC 4787 and RFC 8085, as in the notes. Example names come from RFC 2606 and example addresses
from RFC 5737 and RFC 3849.
