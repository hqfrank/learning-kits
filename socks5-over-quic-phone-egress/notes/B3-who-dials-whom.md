# B3 — Who dials whom

**Source:** internal design (front-door section, alternatives and cost tables, network isolation, host firewall, IPv6/NAT64), deployment runbook (known issues), generalised; RFC 9000 §9 and §5.1 (connection IDs); RFC 9308 §3.2 (NAT); RFC 6052 (NAT64 prefix); the IETF QUIC-LB draft ("QUIC-LB: Generating Routable QUIC Connection IDs"). · **Status:** concept note. Costs are illustrative.

## In one sentence
The phone always dials out, so home routers and carrier NATs need no configuration, and a global anycast UDP front door with static ports mapped to private instances gives each cloud instance a fixed public `address:port` without a load balancer, at the cost of a new inbound UDP port whose only gate is the QUIC handshake.

## What it is
Two parties must meet: a phone behind one or more NATs, and a cloud instance in a private subnet. Neither can accept unsolicited inbound connections by default. One of them must be reachable.

**Direction chosen: the phone is the QUIC client.** A connection that the phone opens creates its own NAT state on the way out. Replies come back through that state. This is the same reason a phone can browse the web without port forwarding. The cloud cannot dial the phone, because the phone has no stable public address and sits behind NATs that drop unsolicited packets.

**Direction of streams: the cloud opens them.** After the phone's connection is up, the cloud opens a QUIC stream whenever a tool needs a connection ([[B2-quic-for-this-job]]). The phone therefore dials once, and the cloud asks for work over that connection. This "reverse" pattern is why the phone's QUIC library must accept server-initiated streams ([[C3-the-two-client-stacks]]).

## How it works
**The front door.** A **global anycast UDP front door** advertises a small set of static public IPv4 addresses from many edge locations (anycast). The phone's packets enter the provider's network at the nearest edge and travel on the provider's backbone. In **custom-routing mode** the front door is not a load balancer. It is a deterministic port map:

```
private 10.0.0.11:4433  ↔  public 203.0.113.10:20147   (instance A)
private 10.0.0.12:4433  ↔  public 203.0.113.10:23811   (instance B)
```

(The public address comes from a documentation range, `documentation_addresses`; the private addresses are generic RFC 1918 examples; port 4433 is an illustrative design port, `quic_listen_port_illustrative`; the public ports come from an illustrative range, `front_door_port_range_illustrative`.) Each `(subnet, private address, port)` gets one public port. Traffic is **deny-by-default**: the provisioning step allows each new instance, asks the front door which public port it got, and stores the pair. The config endpoint later returns that pair to the phone ([[B5-the-control-stream]]). The front door has no discovery mechanism of its own; the application must tell the phone where to go.

**Why not a load balancer.** A QUIC connection must reach the same instance for its whole life. An ordinary layer-4 load balancer picks a backend by hashing the address 4-tuple. After NAT rebinding or migration the 4-tuple changes, and the hash can send packets to a different backend that does not know the connection. The IETF QUIC-LB draft fixes this by encoding a server ID in the connection ID (RFC 9000 §5.1 lets the server choose its connection IDs), but the source found no mainstream library support. A per-instance port map avoids the problem.

**Alternatives considered** (internal design, generalised; costs are illustrative relations, not prices):

| Option | Per-instance routing | Cost as instances grow | Verdict |
|---|---|---|---|
| Anycast front door, custom routing | automatic port map | flat: one shared fixed fee plus per-GB (`front_door_fixed_cost_illustrative`, `front_door_per_gb_illustrative`) | chosen |
| Layer-4 load balancer, one listener per instance | manual listener per instance | steps up, because each balancer has a listener limit | viable only when small |
| Load balancer with QUIC-LB connection IDs | via the connection ID | flat | no library support at the time |
| A public IP per instance | direct | linear in instance count; every instance exposed | rejected |
| A VPN mesh to the phone | through the VPN | low | needs a VPN client on the phone; poor mobile experience |

With illustrative numbers, one instance that proxies 5 GB a month (`traffic_per_instance_illustrative`) adds about 0.10 USD of variable cost (my arithmetic: 5 × 0.02). The same traffic through a residential-proxy vendor costs about 40 USD (my arithmetic: 5 × `residential_proxy_price_illustrative`). The fixed fee is shared by every instance.

**What the front door does not do.** It gives addressability, not access control. The source states it plainly: the instances in that deployment also had public addresses, and the cloud firewall rule for the QUIC port allowed all sources, because the front door publishes no stable source range. Anyone who learns the address can send UDP to the port. All authentication therefore happens in the QUIC handshake: the certificate the phone pins, the ALPN value, and the single-use token on the control stream ([[B4-trust-without-a-ca]], [[C1-threat-model]]).

**Two firewalls, both silent.** A packet must pass the cloud network's firewall rule and the host's own packet filter. Both drop silently. The host filter in the source appended rules in order: accept loopback, accept established flows, then drop everything. A rule that accepts the QUIC port **must come before** the final drop; appended after it, it never matches, and the phone shows "connecting" for ever with no log anywhere (internal design). The source restructured the boot script so that the drop is unambiguously last, instead of inserting at a line number.

**IPv6-only phones.** The front door in the source was IPv4-only. A phone on an IPv6-only cellular network reaches an IPv4 address through **NAT64**: the carrier's DNS64 synthesises an address under the well-known prefix `64:ff9b::/96` (`nat64_well_known_prefix`, RFC 6052), for example `203.0.113.5` becomes `64:ff9b::cb00:7105` (`nat64_example`, my arithmetic). The phone's network stack handles this when given the address string. The source lists a dual-stack front door as the fix if NAT64 paths misbehave for UDP.

**Networks that block UDP.** Some guest and corporate Wi-Fi networks allow outbound UDP only to ports 53 and 443. The front door's high ports are then unreachable. The phone sees handshake timeouts, gives up after a few (an illustrative 4, `handshake_fail_limit_illustrative`), and the agent falls back to the cloud IP ([[C2-limits-and-failure-handling]]).

## How it is measured or used
- The front door's own dropped-packet metric shows packets refused before they reach the instance: an instance that was never allowed, or a wrong mapping.
- An operator check lists the port mapping for an instance's private address and expects state "allow".
- On the host, a socket listing shows whether the QUIC port is bound; the packet filter listing shows whether the accept rule sits above the drop.

## Common confusions
- **"Anycast is load balancing."** In custom-routing mode, anycast only brings packets to the nearest edge. The port map, not a hash, picks the instance.
- **"The front door protects the instance."** It does not filter sources. The QUIC handshake is the gate.
- **"The phone needs port forwarding."** The phone only dials out. Its NATs see an ordinary outbound UDP flow, which the keepalive keeps open.
- **"One public port per instance cannot scale."** The port map has tens of thousands of ports per address and per endpoint group. The binding limit in the source was the number of endpoint groups per listener, which is far beyond one team's instance count.

## Why it matters for an agent service
Choosing who dials whom decides what can break. Here the phone's side never needs configuration. The cloud side needs exactly one new inbound UDP port per instance, and every design choice in Part C exists because that port is open to the internet.

## Terms introduced
- **global anycast UDP front door** — a provider service that advertises static anycast addresses at many edges and forwards UDP into private networks.
- **anycast** — one address announced from many locations; packets go to the nearest one.
- **custom-routing mode** — a front-door mode that maps each public port to one private `address:port` instead of balancing load.
- **deny-by-default** — no traffic flows to a destination until it is explicitly allowed.
- **port map** — the table from public front-door ports to private instance addresses.
- **QUIC-LB** — an IETF draft that encodes a server identifier in QUIC connection IDs for routable load balancing.
- **NAT64 / DNS64** — carrier translation that lets IPv6-only clients reach IPv4 addresses through synthesised IPv6 addresses.
