# A1 — The end-to-end picture

**Source:** internal design document (architecture, passthrough listener, browser proxy bridge, environment injection, network isolation, sequence diagrams), generalised; curl documentation on `socks5h://` (https://everything.curl.dev/usingcurl/proxies/socks.html); Chromium `net/docs/proxy.md` (proxy schemes and bypass rules). · **Status:** concept note. Latency figures are an illustrative model, not measurements.

## In one sentence
An agent tool reads `ALL_PROXY=socks5h://localhost:<port>`, speaks SOCKS5 to a local listener, the listener carries those bytes over one new QUIC stream to the phone, the phone resolves the name and opens the TCP connection from its own network, and a separate HTTPS control channel tells the phone where the tunnel is and which certificate to trust.

## What it is
The system has two independent network paths. They share no state.

| Path | Transport | Who dials | Carries |
|---|---|---|---|
| **Control channel** | HTTPS over TCP | the phone, to the assistant service's existing API (reached through an HTTPS tunnel provider for the control channel) | chat, and one call that returns the tunnel parameters |
| **Data path** | QUIC over UDP | the phone, to a global anycast UDP front door, which maps a static public port to the private instance | one QUIC connection; one QUIC stream per proxied TCP connection |

The control channel already exists for chat. The data path is new. The HTTPS tunnel provider cannot carry raw UDP, so the data path needs its own front door ([[B3-who-dials-whom]]).

## How it works
Follow one HTTPS request from a tool to a site.

1. **The tool finds the proxy.** The instance boot script writes `ALL_PROXY=socks5h://localhost:10080` (an illustrative design port, `socks_listen_port_illustrative`) and a `NO_PROXY` list into the environment of the agent runtime. Most HTTP libraries and `curl` honour these variables, so tools need no code change.
2. **The tool speaks SOCKS5.** The `h` in `socks5h` tells the client to send the host name, not a resolved address (curl documentation). The client sends a method request, receives "no authentication", then sends `CONNECT` with the domain name and port 443 ([[B1-socks5-in-ten-minutes]]).
3. **The listener checks and forwards.** The **passthrough listener** on `localhost` reads the `CONNECT` request only to apply a small server-side deny list ([[C1-threat-model]]). It then opens a new server-initiated QUIC stream to the phone and forwards the SOCKS5 bytes unchanged.
4. **The phone does the work.** The phone's SOCKS5 server resolves the name with the phone's own resolver, checks the resolved address against its destination filter, opens TCP from the phone, and returns the SOCKS5 success reply.
5. **The bytes flow.** The listener passes the reply to the tool. From now on the QUIC stream is a byte pipe. The tool sends its TLS ClientHello, the phone relays it, and the site sees the phone's address.

**Why the environment is static.** The agent runtime reads its environment file once, when its service starts. A file change during a session has no effect until a restart, and a restart interrupts the user's chat (internal design). The design therefore sets `ALL_PROXY` once at boot and keeps the listener always up. When no phone is connected, the listener makes a **direct connection** from the cloud IP. A tool cannot tell the two cases apart except by its exit address.

One ordering rule follows: the boot script writes `ALL_PROXY` only when the instance also has a front-door mapping, because only then does the listener ship with it. Otherwise proxy-aware tools would get "connection refused" from a port with no listener.

**What bypasses the proxy.** `NO_PROXY` lists destinations that must not go through the phone: `localhost`, `127.0.0.1`, `::1`, the link-local metadata address (`metadata_address`), internal suffixes such as `.internal` and `.local`, and the cloud provider's own API domains. The model API, the secrets store and the metadata service then stay on the cloud path. A test checks that no model-API request ever reaches the listener.

**The browser is a special case.** The headless browser does not read `ALL_PROXY`. It needs `--proxy-server` and `--proxy-bypass-list` flags (Chromium `proxy.md`). Two details matter:

- Chromium accepts `socks5://` and always resolves names on the proxy side; it does not recognise the `socks5h://` spelling. The launcher therefore rewrites `socks5h://` to `socks5://`, with the same remote-DNS meaning (Chromium `proxy.md`; internal design).
- A page load triggers many requests to analytics, advertising and CDN-telemetry hosts that do not block cloud addresses. Without a bypass list, each one becomes a tunnel stream. The source cut tunnel streams per page by about ten times with a bypass list (an illustrative 60 to 6, `streams_per_page_illustrative`).

## How it is measured or used
**Exit-address check.** The basic end-to-end test compares two requests to a what-is-my-address service from the instance: one through the proxy, one direct. The two answers must differ, and the proxied one must match the phone's network.

**Latency model.** The proxy adds round trips. Let RTTcp be the cloud-to-phone round trip, RTTps the phone-to-site round trip, and DNS the phone's resolver time. With illustrative Wi-Fi values (`rtt_cloud_phone_illustrative`, `rtt_phone_site_illustrative`, `phone_dns_typical_illustrative`), the time to the first response byte is (my arithmetic, `ttfb_model_illustrative`):

| Step | Cost | Wi-Fi (ms) | Cellular (ms) |
|---|---|---|---|
| SOCKS5 method request and reply | RTTcp | 50 | 120 |
| SOCKS5 `CONNECT` and reply | RTTcp + DNS + RTTps | 110 | 180 |
| TLS 1.3 handshake, tool to site | RTTcp + RTTps | 80 | 150 |
| HTTP request and response | RTTcp + RTTps | 80 | 150 |
| **Total** | | **320** | **600** |

The same request direct from the cloud costs about three cloud-to-site round trips (an illustrative 60 ms, `ttfb_model_illustrative`). The source set its latency targets above this floor (an illustrative p50 of 300 ms on Wi-Fi and 700 ms on cellular, `latency_target_illustrative`). An idea the source does not use (my explanation): the listener knows the phone always selects "no authentication", so it could send the method request and the `CONNECT` request together. That pipelining removes one RTTcp (to an illustrative 270 ms and 480 ms, `ttfb_model_illustrative`).

## Common confusions
- **"`socks5` and `socks5h` are the same."** With `socks5`, the client resolves the name in the cloud and sends an address. With `socks5h`, the proxy resolves it. Only `socks5h` gives a resolution that matches the phone's location ([[B1-socks5-in-ten-minutes]]).
- **"The listener terminates SOCKS5."** It does not. It reads the destination for one filter and then forwards the SOCKS5 bytes. The phone runs the SOCKS5 state machine.
- **"The control channel and the data path are one connection."** They are separate. The control channel is HTTPS over TCP; the data path is QUIC over UDP through a different front door.
- **"Every request costs one round trip more than direct."** It costs several: two SOCKS5 exchanges to the phone, and every later round trip of the tool travels cloud → phone → site and back.

## Why it matters for an agent service
The design asks nothing of tool authors: a standard environment variable is the whole integration. That is the reason it reaches most tools on day one. The cost is that coverage stops at tools that honour the variable, and the browser needs its own wiring. Tools that ignore proxy variables need the transparent proxy of [[D2-a-platform-owned-data-plane]].

## Terms introduced
- **`ALL_PROXY` / `HTTP_PROXY` / `HTTPS_PROXY`** — environment variables that many HTTP clients read to find a proxy.
- **`NO_PROXY`** — an environment variable listing destinations that skip the proxy.
- **`socks5h://`** — the proxy URL scheme for SOCKS5 with name resolution on the proxy side.
- **passthrough listener** — the local SOCKS5 endpoint on the instance that forwards SOCKS5 bytes to the phone without running the protocol itself.
- **direct connection** — the fallback path: the listener connects to the destination from the cloud IP.
- **control channel** — the existing authenticated HTTPS API between the phone and the assistant service.
- **data path** — the QUIC connection that carries proxied connections.
- **bypass list** — destinations a browser or client sends directly instead of through the proxy.
- **RTT (round-trip time)** — the time for a message to reach a peer and a reply to come back.
- **pipelining (SOCKS5)** — sending the next protocol message before the reply to the previous one arrives.
