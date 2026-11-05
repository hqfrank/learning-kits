# A0 — Why a cloud agent needs the user's own IP address

**Source:** internal requirements and design documents (problem statement, goals, non-goals, later-phase list), generalised; see [`../SOURCES.md`](../SOURCES.md). Public background: RFC 1928 (SOCKS5), RFC 9000 (QUIC). · **Status:** concept note. Every product number is illustrative.

## In one sentence
A cloud-hosted agent that acts for a user on the web is often blocked because websites distrust cloud IP addresses, and the cheapest trustworthy exit is the user's own phone, which already has a residential or mobile IP address and is already online while the user talks to the agent.

## What it is
An **agent service** runs a large-model agent on a cloud instance for each user. The agent uses **tools**: web research, a headless browser, calendar and mail clients. Every tool request leaves the cloud instance from a **cloud IP address**, an address that belongs to a data-centre range.

Many websites score each incoming connection by its source address. This is **IP reputation**. A data-centre address scores badly, because most automated abuse comes from data centres. The site then answers with one of four reactions:

1. a CAPTCHA or another bot challenge;
2. an outright block;
3. a slow or degraded response;
4. content for the wrong place, because the cloud region is far from the user (**geo-fencing**).

Ride-hailing, food-delivery, airline and banking sites are the usual examples. They use the strictest bot detection, and they are also the sites where users most want an agent to act for them.

**Phone egress** is the answer this kit studies. **Egress** is the point where traffic leaves for the internet. In phone egress, the agent's TCP connections leave from the user's phone, so the site sees the phone's home Wi-Fi or cellular address.

## How it works
The design has four parts. Each part has its own note.

1. A **SOCKS5 proxy** on the cloud instance accepts the agent's connections. Tools find it through the standard `ALL_PROXY` environment variable ([[A1-the-end-to-end-picture]], [[B1-socks5-in-ten-minutes]]).
2. A **QUIC tunnel** carries each proxied connection to the phone as one QUIC stream ([[B2-quic-for-this-job]]).
3. The **phone app** runs a small SOCKS5 server. It resolves the name, opens the TCP connection from the phone, and relays bytes ([[C3-the-two-client-stacks]]).
4. A separate **control channel**, the existing authenticated HTTPS API, tells the phone where to connect and which certificate to trust ([[B4-trust-without-a-ca]], [[B5-the-control-stream]]).

**Why the phone and not a vendor.** Commercial **residential-proxy vendors** sell exit traffic from other people's home connections. Three arguments favour the user's own phone (internal requirements, generalised):

- **Cost.** A vendor charges per gigabyte (an illustrative 8 USD/GB, `residential_proxy_price_illustrative`). The phone path costs a small shared fixed fee plus a small per-gigabyte fee (an illustrative 20 USD/month and 0.02 USD/GB, `front_door_fixed_cost_illustrative`, `front_door_per_gb_illustrative`). See [[D2-a-platform-owned-data-plane]].
- **Identity consistency.** A vendor address belongs to a stranger in a random place. The phone address is the user's own. It matches the user's location, the user's earlier logins, and the user's payment country.
- **No extra install.** The phone app already runs during every chat session. The user installs no VPN and grants no VPN permission.

**Caution:** the phone path also makes the user the party that sites blame for abuse. Part C is mostly about that cost ([[C1-threat-model]], [[C4-observability-without-user-data]]).

**First release versus later phases.** The source scopes a first release (minimum viable product, **MVP**) and defers the rest:

| In the first release | Deferred |
|---|---|
| TCP only, through SOCKS5 `CONNECT` | UDP relay (SOCKS5 `UDP ASSOCIATE`) |
| One active device per user instance (last writer wins) | Several devices at the same time, each with its own route |
| Tools that honour `ALL_PROXY` / `HTTP_PROXY` | A **transparent proxy** that captures all TCP with `iptables REDIRECT` ([[D2-a-platform-owned-data-plane]]) |
| Server certificate pinned by fingerprint | Client certificates (mutual TLS) |
| No SOCKS5 username/password | RFC 1929 credentials that carry a session ID |
| A fixed port allowlist (HTTP and HTTPS only, `allowed_ports_illustrative`) | A wider allowlist |

## How it is measured or used
The problem is measured as a **failure rate on bot-protected sites from a cloud IP**. The source reports it as a large minority of tasks (an illustrative 30%, `cloud_ip_task_failure_illustrative`). That is high enough to block the product, because a user stops trusting an agent that fails one task in three.

The fix is measured by three launch metrics (illustrative targets, `success_targets_illustrative`):

- the **tunnel attach rate**: the fraction of active chat sessions with a connected tunnel (an illustrative 0.85);
- the **proxied fraction**: the fraction of the agent's web requests that leave through the phone (an illustrative 0.75);
- a **non-regression** check: the agent's overall web success rate must not fall below its pre-launch baseline.

The third metric matters most. A tunnel that is up but slow or flaky can make the agent worse than the cloud IP did.

## Common confusions
- **"This is a VPN."** A VPN carries every IP packet of a device. This design carries only the TCP connections that the agent sends to a SOCKS5 proxy, one connection per QUIC stream. It is an application-level proxy, not a network-level tunnel ([[D1-l3-versus-l5-tunnelling]]).
- **"The phone can read the agent's traffic."** The agent's HTTPS is end-to-end TLS from the agent to the site. The phone sees the destination name and port in the SOCKS5 request, and encrypted bytes after that.
- **"If the phone is away, the agent breaks."** The proxy falls back to a direct connection from the cloud IP. The agent keeps working; only the success rate on strict sites drops ([[C2-limits-and-failure-handling]]).
- **"A residential proxy vendor is the same thing."** A vendor gives a residential address, but not the user's own address. Sites that bind a session to an address, a location, or a device history still see a stranger.

## Why it matters for an agent service
An agent that acts for a person must look like that person to the sites it visits. The network address is the first thing a site checks. Every later choice in this kit (the proxy protocol, the transport, the trust model, the filters) follows from one decision: lend the agent the user's own address, and do it without exposing the user's home network or the user's reputation.

## Terms introduced
- **agent service** — a cloud service that runs an agent for each user and lets it act through tools.
- **tool** — a program the agent calls to act, for example a web fetcher or a headless browser.
- **cloud IP address** — a source address in a data-centre range.
- **IP reputation** — a site's score of how trustworthy a source address is.
- **geo-fencing** — serving or refusing content by the apparent location of the source address.
- **egress** — the point where traffic leaves for the internet.
- **phone egress** — routing an agent's connections so that they leave from the user's phone.
- **residential-proxy vendor** — a company that sells exit traffic from home connections.
- **MVP (minimum viable product)** — the first release, with deliberately limited scope.
- **transparent proxy** — a proxy that captures connections without the application's knowledge.
