# D1 — Layer-3 tunnels versus layer-5 proxies

**Source:** internal analysis of a partner tunnelling platform (its educational section on layer-3 tunnelling, TUN/TAP, WireGuard and the layer mismatch), generalised; Linux kernel documentation, "Universal TUN/TAP device driver" (`Documentation/networking/tuntap.rst`); Donenfeld, "WireGuard: next generation kernel network tunnel", NDSS 2017; wg(8) manual page; iptables-extensions(8), `REDIRECT` target; RFC 1928. · **Status:** concept note.

## In one sentence
A layer-3 tunnel carries whole IP packets for every protocol and needs no help from applications, but it needs kernel interfaces, routing tables and VPN permission; a layer-5 proxy such as SOCKS5 carries one TCP connection at a time for applications that ask for it, which is all a proxy-aware agent sending TCP needs, and it makes per-connection policy trivial.

## What it is
Tunnels differ by the unit they carry.

| Layer | Unit carried | Example |
|---|---|---|
| L2 (data link) | Ethernet frames | a TAP device; GRE-TAP |
| L3 (network) | IP packets | a TUN device; WireGuard |
| L4 (transport) | TCP or UDP flows | QUIC carries streams for higher layers |
| L5 (session) | one proxied connection, opened by request | SOCKS5 (RFC 1928) |
| L7 (application) | application requests | an HTTP proxy |

SOCKS5 is usually placed at layer 5, because it sits between the application and the transport and acts per connection. The internal analysis calls the same idea "L7 proxying"; the distinction that matters is packet versus connection, not the layer number.

**TUN and TAP.** Linux offers virtual network interfaces that a program can open as a file. A **TUN** device exchanges IP packets (layer 3). A **TAP** device exchanges Ethernet frames (layer 2) (Linux TUN/TAP documentation). The kernel routes traffic to the interface like to any network card. Applications do not know that a program, not a wire, is on the other side.

**WireGuard** is a layer-3 tunnel built as a kernel interface. Its properties (Donenfeld 2017; wg(8)):

- a 1-RTT handshake based on the Noise IK pattern (`wireguard_handshake_round_trips`);
- new session keys every 120 s, and old keys rejected after 180 s (`wireguard_timers`);
- **cryptokey routing**: each peer's public key is tied to a list of allowed IP prefixes; outbound packets pick the peer by longest-prefix match, and inbound packets are dropped if their inner source is not in the sending peer's list;
- roaming: a peer's endpoint updates to the source address of its latest authenticated packet (wg(8));
- an optional persistent keepalive for peers behind NAT (25 s is the manual's example, `wireguard_persistent_keepalive_example`);
- a cookie reply under load, which makes an initiator prove its address before the responder does expensive work (Donenfeld 2017 §5.4.7); compare QUIC Retry in [[C1-threat-model]].

Each data packet carries 32 bytes of WireGuard header and tag, so 60 bytes over IPv4 and UDP (`wireguard_data_overhead`, my arithmetic).

## How it works
**What each kind gives** (internal analysis, generalised):

| Property | L2/L3 tunnel | L5 proxy |
|---|---|---|
| who decides what is tunnelled | the kernel's routing table | the application, per connection |
| protocols | everything: TCP, UDP, ICMP, … | what the proxy protocol supports (here TCP `CONNECT`) |
| connection awareness | none; encrypted packets | full: destination, state, lifetime |
| multiplexing | one encrypted flow per peer | many connections on one transport (QUIC streams) |
| DNS | whatever the client's resolver does | the proxy can resolve (`socks5h`, [[B1-socks5-in-ten-minutes]]) |
| per-destination policy | routing rules and packet filters | a check before each `CONNECT` |
| errors | lost packets | a reply code per connection |
| infrastructure | kernel interfaces, routes, keys per peer | one listening socket and user-space code |
| on a phone | a VPN profile and permission | an ordinary app feature |

**The transparency spectrum.** From "the application does not know" to "the application takes part":

1. **L2 tunnel** — a whole unmodified operating system believes it has a network card.
2. **L3 tunnel** — every IP packet of a host or VPN app goes through the tunnel.
3. **Transparent proxy** (defined in [[A0-why-the-users-ip]]) — `iptables -t nat … -j REDIRECT` sends every outbound TCP connection to a local port (iptables-extensions(8)); a local program reads the original destination with the `SO_ORIGINAL_DST` socket option and opens a SOCKS5 connection upstream. Applications are unmodified, but only TCP is covered.
4. **SOCKS-aware application** — the application reads `ALL_PROXY` and speaks SOCKS5. This design.
5. **Explicit HTTP proxy** — the application sends HTTP requests to a configured proxy.

**Why layer 5 is enough here.** The agent's traffic is TCP: HTTPS from tools and from a browser. Its tools already honour proxy variables. The design wants per-connection decisions: bypass the model API, refuse private destinations, resolve on the phone. Every one of these is a line of code at layer 5 and a routing or filtering problem at layer 3 (my explanation). The internal analysis lists further layer-3 costs for this case:

- a peer that must route arbitrary internet destinations needs `0.0.0.0/0` in its allowed IPs, and on one interface only one peer can own that prefix, so a shared interface cannot serve many such peers;
- a dedicated tunnel fleet adds a hop between the agent and the phone;
- the phone needs VPN permission, and an always-on VPN is invasive for a feature the user does not see;
- WireGuard has no streams, so all connections share one flow's loss and ordering.

**Why layer 5 is cheaper to secure.** A proxy sees each destination before it connects, and answers each refusal with a code (`0x02`). A layer-3 tunnel must filter packets, after the fact, with the full complexity of IP: fragments, every protocol, every address form. The phone-side filter of [[C1-threat-model]] is one short function; the equivalent packet policy on a phone VPN is a firewall (my explanation).

**When layer 3 is the right tool.** Use a packet tunnel when the traffic is not only TCP (QUIC-based apps, DNS, games, STUN, ICMP), when applications cannot be changed or configured, or when a whole operating system must see a network card. The partner platform in the source served exactly that case: an unmodified Android operating system in a container needed a layer-2 interface. Different callers need different layers; the mistake is to give a proxy-aware caller a packet tunnel because one already exists.

## How it is measured or used
Decide the layer by listing the traffic: protocols, whether applications can be configured, and which per-destination decisions are needed. If the list is "TCP, configurable, per-destination policy", layer 5 wins. If it includes UDP or unmodifiable software, start from layer 3 or the transparent-proxy middle ground.

## Common confusions
- **"A VPN is more secure than a proxy."** Both can encrypt. The proxy also knows what each connection is for, which makes policy easier to get right.
- **"Transparent means layer 3."** A transparent proxy (`REDIRECT` + local SOCKS client) is transparent to applications and still per connection underneath.
- **"QUIC competes with WireGuard."** QUIC carries streams for applications; WireGuard carries packets for kernels. This design uses QUIC to carry layer-5 connections.
- **"WireGuard roaming is QUIC migration."** WireGuard updates the peer endpoint from authenticated packets; there are no streams to keep. QUIC validates the new path and keeps every stream.

## Why it matters for an agent service
Agents are proxy-aware by construction: their tools are code the service controls. That puts them at the cheap end of the spectrum. A design that starts from "what does the caller actually send?" avoids building network-level machinery for an application-level need.

## Terms introduced
- **layer-3 tunnel** — a tunnel that carries IP packets.
- **layer-5 proxy** — a proxy that carries one requested connection at a time, such as SOCKS5.
- **TUN device** — a virtual interface that exchanges IP packets with a user-space program.
- **TAP device** — a virtual interface that exchanges Ethernet frames with a user-space program.
- **WireGuard** — a kernel layer-3 tunnel with a Noise-based handshake and cryptokey routing.
- **cryptokey routing** — tying allowed IP prefixes to peer public keys, for both routing and source checks.
- **`SO_ORIGINAL_DST`** — the Linux socket option that returns a redirected connection's original destination.
