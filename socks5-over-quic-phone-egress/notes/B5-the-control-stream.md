# B5 — The config call and the control stream

**Source:** internal design (control-stream protocol, control-channel API, token lifecycle, device-swap behaviour, UX states), QUIC server implementation, end-to-end test plan (known behaviours), generalised; RFC 9000 §2.1 (stream IDs). · **Status:** concept note. All limits are illustrative design parameters.

## In one sentence
Before each connection the phone fetches a short-lived single-use token over HTTPS, then opens stream 0 and sends a tiny length-prefixed JSON hello with its device ID and that token, and the server answers with the SOCKS5 port or with one of four error codes, keeping exactly one device active and refusing to swap devices while the current tunnel is busy.

## What it is
Two messages set a tunnel up:

1. **The config call** on the control channel (HTTPS). It tells the phone where the tunnel is, what to trust, and gives it a token.
2. **The control hello** on the data path (QUIC stream 0). It tells the server which device this is and proves that the phone just made the config call.

## How it works
**The config call.** The phone sends `GET` to the config endpoint with its device ID in a request header. The source puts the ID in a header, not a query parameter, because query strings end up in proxy and access logs. The answer is:

```json
{ "enabled": true, "host": "203.0.113.10", "port": "20147",
  "certFingerprint": "sha256:…", "alpn": "socks5-over-quic", "connectionToken": "…" }
```

- `enabled` is false when the instance has no certificate, no front-door mapping, or the user is not in the feature flag ([[C6-rollout-and-migration]]). The phone then does nothing, and the agent uses the cloud IP.
- `port` is a JSON string, not a number. The source calls this a known wart: the value passes through unchanged from the parameter store, and changing it later would break existing app versions. Clients parse it (my note: decide wire types at the first release, because they freeze).
- The endpoint is rate-limited per user (an illustrative 1 request per 10 s, `config_rate_limit_illustrative`).

**The token.** The **connection token** is 256 random bits from a cryptographic source (`token_bits_illustrative`; 64 hex characters, `token_256bit_hex_chars`). It is:

- **single-use** — consumed the first time it is shown on a control stream, even if that connection later drops;
- **short-lived** — valid for an illustrative 30 s (`token_lifetime_illustrative`);
- **device-bound** — accepted only together with the device ID it was issued to;
- **one generation deep** — each config call demotes the previous token to a **grace period** of an illustrative 5 s (`token_grace_illustrative`), so at most two tokens per user are valid (`tokens_valid_max_illustrative`). The grace window covers the race where a retry fetches a new token while a handshake with the old one is in flight. A grace token keeps its device binding.

The token is a bearer credential held only in memory. **Caution:** the token and the device ID travel in the same HTTPS response. Anyone who can read that response gets both. Device binding stops casual reuse of a leaked token; it does not stop interception of the control channel. The source names mutual TLS as the real fix ([[C1-threat-model]]).

**The control stream.** After the handshake the phone opens its first client-initiated bidirectional stream, stream 0 (RFC 9000 §2.1, `quic_first_stream_ids`). Each message is a 4-byte big-endian length (`control_length_prefix_illustrative`) followed by UTF-8 JSON. The server closes the stream if the length exceeds an illustrative 512 bytes (`control_msg_max_illustrative`), if the payload does not arrive within an illustrative 3 s (`control_payload_timeout_illustrative`), or if the JSON does not parse. In the example below, the port is an illustrative design port (`socks_listen_port_illustrative`). A length prefix and a cap stop a peer from making the server buffer without limit (my explanation).

```
phone → server   {"deviceId": "…", "platform": "ios", "token": "…"}
server → phone   {"socksPort": 10080}
          or     {"error": "device_active", "message": "…"}
```

The server checks the token and the device binding **before** it attaches the connection to the listener. The port is fixed in the first release; the server still reports it, so a later multi-device release can assign different ports without a protocol change.

The control stream stays open for the life of the connection. If it closes, the server tears the tunnel down. One client stack sends with an "is complete" flag that half-closes the stream; the phone code must send with that flag off, or the server sees a close and drops the tunnel (internal design).

**Error codes.** The phone must handle all four and move to "failed", never loop in "connecting" (internal design):

| Code | Meaning | Phone behaviour |
|---|---|---|
| `device_replaced` | another device of the same user took the tunnel | failed; short notice to the user; retry with backoff |
| `device_active` | the current tunnel is busy; swap refused | failed; short notice; **no** automatic retry |
| `invalid_token` | expired, reused, unknown, or wrong device | failed; no notice; fetch a new config and retry |
| `internal_error` | server fault | failed; retry with backoff |

An unknown code is treated as `internal_error`.

**One device at a time.** The first release keeps one active tunnel per instance. A new device replaces the old one: **last writer wins**. Two phones of one user that are both online can then thrash: A connects, B replaces A, A reconnects and replaces B. The source stops this with an **activity guard**. The server records the time of the last relayed byte on the active tunnel, updated on every read in either direction, and initialised to the connection time. A new device is refused with `device_active` while that time is less than an illustrative 20 s old (`activity_guard_illustrative`). During active use this inverts the rule to "first writer keeps it". The kicked device backs off (an illustrative 1, 2, 4 … s, `backoff_illustrative`), and its next attempt meets the guard on the new tunnel and stops.

Two details made the guard correct (internal test plan): the timestamp must be updated by a wrapper around **both** relay directions, because a one-way download would otherwise look idle; and it must start at connection time, so that a fresh tunnel with no traffic yet is also protected.

**What a swap breaks.** All relay streams on the old tunnel close at once, with no drain. Tools see a reset and retry. Sites that bind a login session to an address may then see the same cookie from a new address and ask for re-authentication. The source accepts this in the first release.

**Device identity.** The device ID is the app's existing install-scoped ID, the same one used for push registration. The source rejects a new identifier, a vendor ID that resets on reinstall, and a hardware ID with privacy-policy implications.

**A client stack quirk.** One phone QUIC stack opened an internal bidirectional stream before the app's own control stream. A server that reads only the first incoming stream waits on an empty stream and times out. The fix: try up to an illustrative 3 incoming streams (`control_accept_attempts_illustrative`) and take the first that carries a valid hello (internal implementation and end-to-end notes).

## How it is measured or used
Unit tests in the source cover: valid hellos from each platform; a missing device ID, token or field; empty, malformed and oversized messages; a slow payload; a valid, a random, an expired and a reused token (both reused concurrently and reused after a disconnect); a token presented with the wrong device ID; grace-period acceptance and expiry; and the activity guard in all three cases (busy, idle, fresh) and in both relay directions.

## Common confusions
- **"The token authenticates the user."** The HTTPS session authenticates the user. The token proves that this QUIC connection comes from a client that just held that session.
- **"Stream 0 is special in QUIC."** It is only the first client-initiated bidirectional stream. The application gives it its role.
- **"Last writer wins is enough."** Without a guard, two online devices swap for ever.
- **"`device_active` should retry."** Automatic retry would recreate the thrash the guard prevents.

## Why it matters for an agent service
The control stream is where the tunnel decides who it serves. A few hundred bytes of protocol carry identity, freshness and the one-device policy. Keeping it small and strictly framed is what makes it testable.

## Terms introduced
- **config call** — the HTTPS request that returns the tunnel parameters and a token.
- **connection token** — a short-lived, single-use, device-bound random value that admits one QUIC connection.
- **grace period (token)** — the short time a demoted token remains valid.
- **bearer credential** — a credential that works for whoever holds it.
- **control hello** — the phone's first message on the control stream.
- **length-prefixed framing** — each message preceded by its byte length.
- **last writer wins** — a newer device replaces the active one.
- **activity guard** — refusing a device swap while the active tunnel carried traffic recently.
- **thrash** — two devices repeatedly replacing each other.
- **install-scoped device ID** — an app-generated identifier that lives as long as the app installation.
