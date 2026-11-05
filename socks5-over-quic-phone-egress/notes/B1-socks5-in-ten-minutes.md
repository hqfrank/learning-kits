# B1 — SOCKS5 in ten minutes

**Source:** RFC 1928 (SOCKS Protocol Version 5); RFC 1929 (username/password authentication, a non-goal here); curl documentation on `socks5h://`; internal design and implementation (SOCKS5 encoder/decoder, phone-side handler, passthrough listener), generalised. · **Status:** concept note. Every protocol number is from RFC 1928.

## In one sentence
SOCKS5 is a two-exchange protocol in front of a TCP byte stream: the client picks an authentication method, then asks the proxy to `CONNECT` to an IPv4 address, an IPv6 address or a domain name, and after one success reply the proxy relays raw bytes in both directions.

## What it is
**SOCKS5** (RFC 1928) is a proxy protocol at the session layer. The client opens a TCP connection to the proxy and sends a short binary request. The proxy opens a second connection to the destination and joins the two. After that the proxy does not parse the data. The service is conventionally on TCP port 1080 (`socks5_conventional_port`, RFC 1928 §3).

Every message starts with the version byte `0x05` (`socks5_version`).

## How it works
**Exchange 1: method negotiation** (RFC 1928 §3).

```
client → proxy   VER=05  NMETHODS=01  METHODS=00          (3 bytes)
proxy  → client  VER=05  METHOD=00                        (2 bytes)
```

The method codes are `0x00` no authentication, `0x01` GSSAPI, `0x02` username/password, and `0xFF` "no acceptable methods" (`socks5_methods`). This design accepts only `0x00`. A client that does not offer it gets `0xFF` and the connection closes.

**Exchange 2: the request** (RFC 1928 §4–5).

```
client → proxy   VER=05  CMD  RSV=00  ATYP  DST.ADDR  DST.PORT(2 bytes, big-endian)
```

- **CMD** is `0x01` CONNECT, `0x02` BIND or `0x03` UDP ASSOCIATE (`socks5_commands`). This design supports CONNECT only. BIND and UDP ASSOCIATE get reply `0x07` "command not supported".
- **ATYP** (address type) is `0x01` IPv4 (4 bytes), `0x03` domain name (a one-byte length, then up to 255 bytes, `socks5_domain_max_len`), or `0x04` IPv6 (16 bytes) (`socks5_atyp`).

A CONNECT to an IPv4 address is 10 bytes, to an IPv6 address 22 bytes, and to a domain of length L it is 7 + L bytes (my arithmetic, `socks5_message_sizes`).

**The reply** (RFC 1928 §6) has the same layout, with **REP** in place of CMD:

| REP | Meaning (RFC 1928) | When the phone sends it in this design |
|---|---|---|
| `0x00` | succeeded | TCP connect to the destination worked |
| `0x01` | general failure | an internal error; also the listener's answer when the tunnel has no free stream |
| `0x02` | connection not allowed by ruleset | the destination filter refused the address or the port |
| `0x04` | host unreachable | name resolution failed |
| `0x05` | connection refused | the destination refused the TCP connection |
| `0x07` | command not supported | BIND or UDP ASSOCIATE |

The full table is `socks5_reply_codes`. The reply's BND.ADDR and BND.PORT fields report the proxy's local address. This design sends zeros, so a minimal reply is 10 bytes (`socks5_message_sizes`).

**After the reply,** the proxy copies bytes in both directions until either side closes. For HTTPS, those bytes are the client's TLS session with the site.

**`socks5` versus `socks5h`.** RFC 1928 lets the client send either an address or a name. Client software chooses (curl documentation):

| Client URL | Who resolves the name | What the proxy receives |
|---|---|---|
| `socks5://` | the client, in the cloud | ATYP `0x01` or `0x04` with an address |
| `socks5h://` | the proxy, on the phone | ATYP `0x03` with the name |

**Remote DNS** (the `h` form) gives **geo-consistent resolution**. Large sites use DNS to steer a client to a nearby server. If the cloud resolves the name, the phone connects to a server picked for the cloud region, far from the user. If the phone resolves it, the phone gets the server a local user would get. Remote DNS also removes the need for a separate DNS proxy. A DNS-over-HTTPS relay (RFC 8484) was the alternative not chosen (internal requirements).

**Passthrough.** On the cloud side, the listener does not run this state machine. It reads the method request, answers it, reads the CONNECT request, and parses only the destination for one filter ([[C1-threat-model]]). Then it forwards the original bytes to the phone and waits for the phone's reply. The phone runs the full state machine. The listener stays small, and the protocol logic lives in one place.

**Authentication is a non-goal.** RFC 1929 adds a username/password sub-negotiation (method `0x02`, each field up to 255 bytes, `rfc1929_field_max`). The first release relies on the listener being bound to `localhost`. A later phase may use the username field to carry a session ID, so that one listener can route each request to a different device ([[D2-a-platform-owned-data-plane]]).

## How it is measured or used
The encoder and decoder are pure functions with no input/output, so table-driven unit tests cover them fully (internal test plan, generalised):

- build and parse every message type for all three address types;
- round-trip tests: build a request, parse it, and compare the fields;
- truncated input, wrong version byte (`0x04`), unsupported command, unsupported address type;
- big-endian port encoding: port 4433 encodes as `0x11 0x51` (my arithmetic: 4433 = 17 × 256 + 81).

## Common confusions
- **"SOCKS5 encrypts."** It does not. Here the encryption comes from QUIC between cloud and phone, and from the tool's own TLS to the site.
- **"`socks5h` is a different protocol."** It is the same protocol. The `h` is a client convention that selects ATYP `0x03`.
- **"The proxy can see the HTTPS content."** It sees the destination name and port in the request. After the reply it sees only TLS records.
- **"REP `0x02` means the site refused."** `0x02` is the proxy's own policy. A site that refuses gives `0x05`.

## Why it matters for an agent service
SOCKS5 is small enough to implement and test in an afternoon on each platform, and almost every HTTP client already speaks it. Remote DNS is the detail that makes phone egress believable to a site: the phone's address and the server the phone picked agree with each other.

## Terms introduced
- **SOCKS5** — the RFC 1928 proxy protocol: method negotiation, one request, one reply, then a byte relay.
- **method negotiation** — the first SOCKS5 exchange, which selects the authentication method.
- **CONNECT** — the SOCKS5 command that asks the proxy to open a TCP connection to a destination.
- **ATYP** — the SOCKS5 address-type byte: IPv4, domain name, or IPv6.
- **REP** — the SOCKS5 reply-code byte.
- **remote DNS** — name resolution done by the proxy, selected by `socks5h://`.
- **geo-consistent resolution** — DNS answers that match the location of the exit address.
- **passthrough** — forwarding SOCKS5 bytes without running the protocol state machine.
