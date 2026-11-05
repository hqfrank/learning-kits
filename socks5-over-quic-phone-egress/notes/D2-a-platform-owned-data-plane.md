# D2 — A platform-owned data plane, and the later phases

**Source:** internal proposal for a unified residential-IP platform (request for comments, high-level design, a demonstration design for a second caller), internal analysis of a partner tunnelling platform, and the requirements' and design's later-phase sections, generalised; RFC 9113 §8.5 (HTTP/2 CONNECT); RFC 1929; iptables-extensions(8) `REDIRECT`; RFC 8484 (DNS over HTTPS). · **Status:** concept note. Every cost and size is illustrative.

## In one sentence
When several services need the same "exit through the user's device" capability, one platform team should own the device connections and the QUIC fleet, and offer callers a byte-stream tunnel API, because otherwise each caller rebuilds the same server, each device holds one tunnel per caller, and nobody sees the whole system; the price is one more hop and a shared component on the data path.

## What it is
The first design in this kit is **caller-owned**: one agent service runs its own QUIC server on each user instance and its own phone clients. The internal proposal asks what happens when more callers arrive: other agent services, and a product that runs unmodified Android systems in containers and needs a layer-2 path ([[D1-l3-versus-l5-tunnelling]]).

In a **platform-owned data plane**, a platform team operates:

- a **control plane**: a device registry (device class, state, which fleet instance holds it), bindings between callers and devices, health, authentication and metrics;
- **data planes**: a QUIC fleet that holds every device's single QUIC session, beside the existing packet-tunnel fleet for layer-2 callers.

Callers never run tunnel endpoints. They ask the platform for a byte stream through a named device.

## How it works
**The caller API is CONNECT-style.** A caller first **binds** a device, then opens a tunnel per target with an HTTP/2 `CONNECT` request (RFC 9113 §8.5) naming `host:port` and the binding. The platform sends a SOCKS5 `CONNECT` through the device's QUIC session and, on success, relays raw bytes. The internal proposal compares this with a structured "send me your HTTP request as JSON" API:

| Structured HTTP-over-API (rejected) | CONNECT tunnel (chosen) |
|---|---|
| the platform rebuilds HTTP from fields; header order is lost | raw bytes; nothing lost |
| binary bodies need encoding | native |
| TLS ends at the platform, which sees plaintext | end-to-end TLS from caller to site |
| large responses buffered in the platform | streamed; constant memory |
| the platform is an HTTP parser (attack surface) | the platform is a byte relay |
| one call per request | one call per tunnel; all sub-resources flow through |

The platform is, in effect, a SOCKS5 proxy exposed as an HTTP/2 `CONNECT` endpoint. For callers that already speak SOCKS5 (for example a container behind a transparent proxy), a SOCKS5 port can carry the binding ID in the RFC 1929 username field.

**Two tiers inside.** A caller's request can land on any front-tier instance behind a load balancer, but only one fleet instance holds the target device's session. A layer-4 balancer cannot route on an HTTP header. The design therefore has a stateless **tunnel-API tier** that looks up the device's fleet instance in the registry and forwards over a plain internal TCP connection with a small preamble (binding, target), and a stateful **fleet tier** that holds QUIC sessions (an illustrative 1 000 devices per instance, `fleet_devices_per_instance_illustrative`).

**Protocol selection is internal.** The device class decides the data plane: devices with a kernel packet tunnel serve layer-2 callers through the packet fleet; every device serves layer-5 callers through the QUIC fleet. Callers never choose a protocol.

**Failure modes change.** If a fleet instance dies, every device on it loses its session. QUIC migration does not help: it handles a client path change, not a server loss ([[B2-quic-for-this-job]]). Devices detect the loss by keepalive, reconnect, and re-register; the internal proposal estimates the gap (an illustrative 30 s at p99, `fleet_reconnect_gap_illustrative`). Bindings survive; open tunnels do not. Callers must retry `CONNECT` with backoff, exactly as tools retry a reset today ([[C2-limits-and-failure-handling]]).

**Cost drivers** (internal proposal, generalised; illustrative values):

- the **front door**: a fixed fee shared by everyone plus a per-gigabyte fee (`front_door_fixed_cost_illustrative`, `front_door_per_gb_illustrative`);
- **egress and processing per gigabyte**, proportional to proxied traffic;
- **per-device state** in the fleet, which scales with devices, not with callers;
- **engineering per caller**: weeks to build and operate an own tunnel versus days to call an API (an illustrative 8 weeks versus 4 days, `onboarding_effort_illustrative`).

The proposal is honest about small numbers: with very few callers, the platform's fixed cost (fleet redundancy, control plane, private endpoints) exceeds self-hosting; the illustrative break-even is about 4 callers (`platform_breakeven_callers_illustrative`). Below that, the argument is operational: one operator for the device fleet, protocol upgrades done once, and device sharing between callers without coordination.

**Why not a control-plane-only platform** (internal proposal, generalised): if each caller owns its data plane, a device used by N callers holds N tunnels, which costs a phone battery and bandwidth; callers that want the same device depend on each other's infrastructure; every caller repeats the operations work; and the platform cannot see end-to-end health. The accepted trade-off is one extra hop inside the region and a platform component on the data path.

**When the platform is wrong.** A single caller with no plans to share devices gains little. A caller that needs layer 2 keeps its packet path.

**The later phases of the caller-owned design** (requirements and design, generalised):

- **Several devices per user.** The blocker is the agent runtime, not the tunnel: all tool calls run as one operating-system user with one process environment, and setting an environment variable is process-wide and racy across concurrent tools. Options: start each tool as a subprocess with its own environment; an HTTP-client shim that picks the proxy from the request's context; or SOCKS5 usernames that carry a session ID so that one listener routes each connection to the right device's tunnel.
- **A transparent proxy for tools that ignore proxy variables.** A dummy interface and `nat OUTPUT` `REDIRECT` rules send outbound TCP to a local port (iptables-extensions(8)); the receiver reads `SO_ORIGINAL_DST` and opens SOCKS5 to the listener. DNS needs its own path: redirect UDP port 53 to a small DNS-over-HTTPS relay (RFC 8484) that runs through the same SOCKS5 chain. The QUIC server's own outbound UDP must be marked and exempted, or the proxy would capture its own tunnel. Private and local destinations must be excluded **before** the `REDIRECT` rule, because the phone filter would refuse them anyway (demonstration design).
- **Keep firewall layers apart.** The host firewall lives in the `filter` table's `INPUT` chain (inbound); the transparent proxy lives in the `nat` table's `OUTPUT` chain (outbound). Named custom chains per component make each set of rules auditable on its own.
- **Networks that block UDP.** A TCP or WebSocket fallback relay on the same endpoint (the WebSocket option of [[B2-quic-for-this-job]]).
- **Client certificates** for the phone, replacing the bearer token ([[B5-the-control-stream]]).

## How it is measured or used
The proposal's success criteria (generalised): a second caller onboards in days through the API; one device serves two callers at once over one QUIC session; tunnel latency, throughput, failure rate and device health come from one set of platform metrics; and a fleet-instance loss recovers within the stated gap.

## Common confusions
- **"Platform-owned is always cheaper."** At small caller counts it costs more; it is chosen for operations and sharing.
- **"The extra hop doubles latency."** It is a hop inside one region, once per tunnel set-up; the phone round trips dominate ([[A1-the-end-to-end-picture]]).
- **"A shared fleet means shared trust."** Callers are isolated by bindings and authentication; each caller's TLS still runs end to end to the site.
- **"Multi-device needs a new tunnel protocol."** It needs the agent runtime to tell the proxy which session a connection belongs to.

## Why it matters for an agent service
The first caller proves the idea with pragmatic shortcuts. The second and third callers decide whether those shortcuts become a platform or get copied. Planning the boundary (a byte-stream API, device bindings, one session per device) early keeps the first implementation from becoming every team's private fork.

## Terms introduced
- **caller-owned data plane** — each calling service runs its own tunnel endpoints and device connections.
- **platform-owned data plane** — one platform team runs the device connections and offers callers an API.
- **control plane** — the components that decide (registry, bindings, health, auth), as opposed to those that carry bytes.
- **binding** — a platform record that lets one caller use one device.
- **HTTP/2 CONNECT** — the HTTP method that turns a request stream into a byte tunnel to `host:port`.
- **tunnel-API tier / fleet tier** — the stateless front tier and the stateful tier that holds device sessions.
- **device registry** — the table of devices, their class, state and fleet instance.
- **DNS-over-HTTPS relay** — a component that forwards DNS queries over HTTPS (RFC 8484).
