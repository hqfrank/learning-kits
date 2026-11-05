# Diagrams — Giving a cloud agent the user's own IP address (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: the two paths (Part A), the protocols (Part B) and what makes the tunnel
safe and operable (Part C). Every number on every canvas is loaded from this kit's `constants.json`
by key and tagged on the canvas: `[Pn]` = public (an RFC or other public document, or my arithmetic
on one), `[In]` = illustrative (a design parameter or a round value of the right order, **never a
measurement**), `[calc]` = my arithmetic on tagged values, with the formula in the footnote. Each
canvas carries its own legend and sources block, so the exported image stands alone. A combined
6-page source, `socks5-over-quic-phone-egress.drawio`, opens all pages at once.

**Sources used:** only this kit's `notes/`, `glossary.md` and `constants.json` (already generalised).
No internal figure was copied or traced; every picture is drawn fresh from the mechanism in the notes.

**Rendering:** each page is a list of cells in `specNN.py` (helpers in `_common.py`), rendered by
`.render_local.py` two ways from the same list: an editable `.drawio`, and a standalone `.svg`
(rect + XHTML `foreignObject` label per box) rasterised to `.png` with headless Chrome at 2x. Specs
never type a number: they call `V(key)` and `T(key)`, and several pages `assert` their own
arithmetic against the constants (latency rows sum to `ttfb_model_illustrative`; close codes equal
`quic_crypto_error_base` + alert; `20 > 10 + 8`). Regenerate one page with
`python3 .render_local.py specNN.py`, then `python3 .render_local.py --combine`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-two-paths` | Two paths, both dialled by the phone: HTTPS tells it where the tunnel is and which certificate to trust; QUIC carries one stream per tool TCP connection, and the site sees the phone's address. | Notes A1, B3 (B4, B5, C1 for the phone's steps); `socks_listen_port_illustrative`, `quic_listen_port_illustrative`, `front_door_port_range_illustrative`, `phone_max_incoming_streams_illustrative`, `keepalive_illustrative`, `udp_nat_idle_assumption`, `metadata_address`, `allowed_ports_illustrative`, `documentation_addresses` |
| `02-socks5-connect-and-remote-dns` | With socks5h the phone, not the cloud, resolves the name; the cloud listener reads only the destination, forwards the SOCKS5 bytes unchanged, and after one success reply the stream is a plain byte pipe. | Notes B1, A1, C1; `socks5_version`, `socks5_methods`, `socks5_commands`, `socks5_atyp`, `socks5_message_sizes`, `socks5_reply_codes`, `socks5_domain_max_len`, `socks_listen_port_illustrative`, `allowed_ports_illustrative` |
| `03-deadlines-and-commit-point` | Every wait before the CONNECT reply has a deadline, so a dead phone becomes an invisible switch to a direct connection; after the reply reaches the tool the connection is committed and a failure is a reset. | Note C2; `stream_open_timeout_illustrative`, `method_reply_deadline_illustrative`, `connect_reply_deadline_illustrative`, `phone_dns_worst_illustrative`, `phone_connect_timeout_illustrative`, `relay_idle_timeout_illustrative`, `conn_idle_timeout_illustrative`, `phone_max_incoming_streams_illustrative`, `socks5_reply_codes` |
| `04-latency-budget` | Through the phone the first response byte costs about 5x (Wi-Fi) to 10x (cellular) the direct path, because every round trip after CONNECT travels cloud -> phone -> site and back (illustrative model). | Notes A1, B2; `rtt_cloud_phone_illustrative`, `rtt_phone_site_illustrative`, `rtt_cloud_site_illustrative`, `phone_dns_typical_illustrative`, `ttfb_model_illustrative`, `quic_handshake_round_trips` |
| `05-trust-and-admission` | Trust in the tunnel is borrowed from the app's HTTPS login: the fingerprint and a single-use token arrive over HTTPS, then the QUIC handshake must match the pin and the ALPN, and stream 0 must present the token. | Notes B4, B5, C1 (threats 3-4); `sha256_digest`, `cert_validity_illustrative`, `config_rate_limit_illustrative`, `token_*_illustrative`, `quic_min_client_initial_datagram`, `quic_amplification_factor`, `quic_amplification_budget_one_initial`, `retry_integrity_tag`, `control_*_illustrative`, `quic_first_stream_ids`, `quic_crypto_error_base`, `tls_alert_*`, `quic_close_codes_example` |
| `06-threat-layers` | Five threats, five layers: cloud-side checks catch the common cases early, and the phone's filter on the resolved address is the authoritative guard against reaching the user's own network. | Notes C1, B4, B5; `blocked_ranges_ipv4`, `blocked_ranges_ipv6`, `allowed_ports_illustrative`, `metadata_address`, `metadata_address_encodings`, `quic_amplification_factor`, `quic_amplification_budget_one_initial`, `max_unvalidated_handshakes_illustrative`, `max_established_connections_illustrative`, `token_lifetime_illustrative`, `socks_listen_port_illustrative`, `socks5_reply_codes` |

---

## Per-diagram specs (as built)

### 01-two-paths
```
Teaches: control channel (HTTPS, existing login) and data path (QUIC over UDP via an anycast port-map
         front door) are separate and both dialled by the phone; the cloud opens one stream per tool
         connection; the site sees the phone's address; no phone -> direct from the cloud address.
Type:    Block diagram, three frames (cloud side / public edge / user's network) plus the site.
Elements: agent tool + ALL_PROXY; NO_PROXY list; passthrough listener; QUIC server; assistant
         service API; site reached direct; front door; HTTPS tunnel provider; NAT; phone app; site.
Colour:  green bold = data path, purple = control channel, grey dashed = direct fallback.
Left out: the byte-level exchange (02), deadlines (03), trust (05).
```

### 02-socks5-connect-and-remote-dns
```
Teaches: the two SOCKS5 exchanges byte by byte; the listener answers the method request itself, then
         replays the original bytes to the phone; the phone resolves the name (socks5h), filters the
         resolved address, connects; then a plain byte pipe for TLS.
Type:    Sequence diagram, four lanes (tool / listener / phone / site), plus a socks5 vs socks5h panel
         and the failure reply codes.
Left out: BIND / UDP ASSOCIATE (replied 0x07; listed in the footnote table).
```

### 03-deadlines-and-commit-point
```
Teaches: each handshake-phase wait has a deadline matched to the work behind it; the CONNECT deadline
         exceeds DNS worst + connect timeout; before the reply fallback is invisible, after it a
         failure is a reset.
Type:    Bars to scale (30 px per second; maxima, not a timeline) + two zone panels and a commit badge.
```

### 04-latency-budget
```
Teaches: the proxy adds round trips: SOCKS5 method + CONNECT, and every later round trip goes
         cloud -> phone -> site; pipelining would remove one cloud-phone round trip.
Type:    Stacked bars to scale (1.25 px per ms); segment costs computed from the RTT inputs.
Left out: latency targets (latency_target_illustrative). The illustrative Wi-Fi p50 target is below
         the modelled Wi-Fi floor, so the two illustrative values disagree; noted in the footnote
         rather than drawn.
```

### 05-trust-and-admission
```
Teaches: pin + token travel over HTTPS; Retry validates the address before crypto work; the phone
         checks fingerprint and ALPN; stream 0 carries the length-prefixed hello; how each check fails.
Type:    Sequence diagram (instance / API / phone) + failure-mode panel with decoded close codes.
```

### 06-threat-layers
```
Teaches: where each of the five defences sits on the path, what it stops, and what risk remains.
Type:    Path strip with layer markers + five columns (threat / how it reaches / control / residual).
Colour:  green = the authoritative control (phone), blue = cloud-side controls, dashed = accepted risk.
```

**Public-safety:** generic roles only ("the assistant service", "the phone app", "an anycast UDP
front door", "an HTTPS tunnel provider"); public open-source names and RFCs only; the front-door
address shown is from a documentation range. `tools/public-scan.sh` was run over this kit before
hand-off.
