# Story 1 spec — The house line

**Question (the learner's words):** My agent runs in the cloud and websites keep blocking it. How can
it borrow my own address through my phone, without exposing my home network or trusting a stranger?

**Headline:** To look like you, the agent calls through your house: a helper at home looks up the shop
and dials it on your line, so the shop sees your number.
(Engineer view: a cloud agent borrows the user's IP address by sending each TCP connection over one
QUIC connection to the user's phone, which resolves the name and connects from its own network.)
Hedges follow A0: websites *often* distrust cloud addresses; the tunnel lends the user's address and
makes the user the party that sites hold responsible.

**Hero picture:** left, a far office (the cloud instance) with the assistant at a desk and a
receptionist (the passthrough listener). Centre, a front desk with numbered extensions (the anycast
front door). Right of centre, your house with a helper at a home switchboard (the phone app) and a
wall intercom with a "no" sign (the home network). Far right, a shop with a caller-ID screen. A thick
sky-blue trunk line runs house → front desk → office, with small call tokens moving on it. A leaf line
runs house → shop; the screen reads "your home ✓". A dashed coral line runs straight from the office
to the shop; its screen reads "office number ✗ — prove you are human". A plum letter travels on the
usual line (office → house) carrying the voiceprint and a one-time ticket. A row of five tickets under
the picture names the five ideas with their notes (B1, B2, B3, B4/B5, C1).

## Why this metaphor (not the brief's courier)

The brief proposes a courier who posts letters from your home. Letters are packets; they suggest a
layer-3 tunnel, which this design is not (D1). The design relays **connections**: open a line to a
named place, hear "you're connected", then pass a conversation through. A **telephone exchange** has
that shape built in, and several mechanisms map one to one:

- caller ID ↔ the source IP address that sites score;
- looking the shop up in the **local** directory ↔ remote DNS (`socks5h`) and geo-consistent
  resolution (a chain shop's local branch);
- "you're connected" ↔ SOCKS5 REP `0x00`, and the commit point after it;
- one trunk line with many channels ↔ one QUIC connection with one stream per TCP connection;
- you cannot ring into a house, the helper rings out ↔ NAT, the phone dials;
- a front desk with a public number and extensions ↔ the port map to private instances;
- a click on an idle line so the exchange does not forget it ↔ keepalive under the NAT timeout;
- the house intercom ↔ the home network (private ranges), refused by the helper.

The brief's two checks stay: the voiceprint sent over the trusted usual line is the pinned
fingerprint, and the one-time ticket is the token (the brief's doorman). I considered the courier and
a pneumatic tube; both lose "you're connected" and the commit point.

Risk: the real helper *is* a phone. In house view the helper works a home switchboard on "your home
line"; engineer view says "the phone app". The word "phone" in house view only means a handset.

## Cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| the far office | the cloud instance | far from you, its number is known to be an office | it is one private instance per user, not a building of staff |
| the assistant | the agent and its tools | it makes the calls | it reads `ALL_PROXY` once at boot |
| the receptionist | the passthrough listener on localhost | takes the assistant's request, puts it on a channel unchanged, can dial direct from the office instead | it reads the destination only for one filter |
| the trunk line, its channels | the QUIC connection, its streams | one line, many independent calls | it is UDP packets, not a circuit; lost packets are re-sent |
| the front desk, extensions | the anycast UDP front door, port map | one public number, one extension per private office | it checks nobody; the handshake is the gate |
| the helper at home | the phone app's SOCKS5 server | looks up, checks, dials, holds the two handsets together | software, runs only while the chat is open |
| the local directory | the phone's resolver (remote DNS) | gives the branch near you | — |
| caller ID | the source IP address | the shop screens calls by it | sites score reputation, not only the number |
| the usual line | the HTTPS control channel | already trusted for chat | separate path, TCP |
| the voiceprint | the pinned SHA-256 certificate fingerprint | public, yet cannot be imitated | a real voice can be imitated; a fingerprint cannot without the key |
| the one-time ticket | the single-use, short-lived, device-bound token | read out once on channel 0 | — |
| the intercom | the home network and other private ranges | rooms inside the house | also includes the cloud's link-local metadata address |
| the shop | the website | answers or screens the caller | — |

## Scenes

| # | Claim | Beat | Figure | What moves, what it means | Interaction | Note | Numbers |
|---|---|---|---|---|---|---|---|
| 1 | Calls from an office get screened; calls from your home do not | (question) | scene player, 4 steps | a call token runs office → shop, screen turns ✗; then house → shop, ✓; a rented stranger's line costs per GB | step | A0 | `cloud_ip_task_failure_illustrative`, `residential_proxy_price_illustrative`, `front_door_per_gb_illustrative`, `traffic_per_instance_illustrative` |
| 2 | One call, end to end; the helper looks the shop up at home | therefore | predict (who looks it up?) → scene player, 6 steps → live figure (scheme, destination, port) | request bytes ride a channel; the directory lights at the house; the "connected" chip returns; the last step shows every later round trip going the long way | predict, step, select | A1, B1 | `socks_listen_port_illustrative`, `socks5_message_sizes`, `socks5_atyp`, `socks5_reply_codes`, `ttfb_model_illustrative`, `documentation_addresses`, `story_directory` |
| 3 | One trunk, many channels: a crackle stalls only its own call | but (many calls) | predict (how many wait?) → scene player, 4 steps | six call tokens; a crackle mark on one; shared line freezes all six, trunk freezes one; the 65th call gets "busy" at once | predict, step | B2, C2 | `quic_handshake_round_trips`, `phone_max_incoming_streams_illustrative`, `heavy_page_concurrency_illustrative`, `socks5_reply_codes`, `story_crackle` |
| 4 | The helper rings out; a front desk with extensions finds the office; a click keeps the line remembered | but (who dials?) | scene player, 4 steps → live figure (keepalive, idle timeout) | the dial-out token runs house → desk → office; the extension lights; clicks tick on a timeline and the exchange's memory bar fills or gaps | step, two sliders | B3, B2 | `story_port_map`, `quic_listen_port_illustrative`, `front_door_port_range_illustrative`, `udp_nat_idle_assumption`, `keepalive_illustrative`, `conn_idle_timeout_illustrative` |
| 5 | Trust without a notary: a voiceprint from the usual line, a one-time ticket on channel 0 | therefore (the desk checks nobody) | predict (a stranger knows the voiceprint) → scene player, 5 steps | the letter rides the usual line; the voiceprint is compared, match ✓; an impostor's print ✗ hang up; a scanner in the wrong language; the ticket is read and torn | predict, step | B4, B5 | `sha256_digest`, `token_bits_illustrative`, `token_lifetime_illustrative`, `token_grace_illustrative`, `tls_alert_no_application_protocol`, `quic_close_codes_example` |
| 6 | The helper never puts a call through to the intercom, and four other guards | therefore (the line is open to the world) | flip cards, 5 | — | flip | C1 | `blocked_ranges_ipv4`, `metadata_address`, `metadata_address_encodings`, `allowed_ports_illustrative`, `quic_amplification_factor`, `quic_min_client_initial_datagram`, `quic_amplification_budget_one_initial`, `max_unvalidated_handshakes_illustrative` |
| 7 | Before "you're connected" the receptionist can quietly dial direct; after it, a drop is a click and a redial | but (the helper goes away) | predict (switch mid-call?) → scene player, 5 steps | deadline clocks fill; the receptionist's direct line lights; after the commit point a reset mark and a redial | predict, step | C2 | `stream_open_timeout_illustrative`, `method_reply_deadline_illustrative`, `connect_reply_deadline_illustrative`, `phone_dns_worst_illustrative`, `phone_connect_timeout_illustrative`, `relay_idle_timeout_illustrative` |
| — | Your turn | — | link cards | — | — | — | — |

Totals: 4 predicts, 6 scene players, 2 live figures, 5 flip cards.

**Live figure A (scene 2).** Inputs: scheme (`socks5h` / `socks5`), destination (a shop name, a name
that resolves to the home router, `192.168.1.1`, `::ffff:192.168.1.1`, the metadata address in hex,
the metadata short form `169.254.43518`), port (443 / 80 / 22). Pure model: who looks up, ATYP and
request size, the office check, the helper check after lookup, the reply, what the shop sees. It
follows explorer 01's rules (C1: the office list misses the short form; the helper's check after the
lookup catches it). Self-tests reproduce those claims.

**Live figure B (scene 4).** Inputs: keepalive interval, QUIC idle timeout. The home exchange is
assumed to forget an idle line after `udp_nat_idle_assumption` (RFC 9308 §3.2 says applications can
assume this). Outputs: whether the trunk survives, how many seconds in each interval the office cannot
reach the helper, clicks per minute (RFC 9308 warns that pings more often than every 30 s cost mobile
power). Follows explorer 03's ordering (keepalive < NAT, keepalive ≤ ⅓ idle). Self-tests: the design
values are reachable; keepalive ≥ idle closes; keepalive > NAT < idle leaves gaps.

**Story-only values** (class illustrative, in `#params-story`): `story_directory` (the shop's branch
addresses from the RFC 5737 documentation ranges, one for the office's directory and one for yours),
`story_crackle` (six calls, the crackle on call 3), `story_port_map` (the B3 example mapping).

## Palette meaning

leaf = your home and its number (the user's address, accepted) · coral = screened, refused, an attack ·
sky = the trunk line and its channels (QUIC) · sun = the directory (DNS) and deadlines · plum = trust
(the usual line, voiceprint, ticket) · stone = the office and people.

## Where the house line breaks (footer)

1. A call carries voice; here each call is a TCP byte stream, and the conversation is end-to-end TLS
   that the helper relays but cannot read.
2. The trunk is not a circuit: it is UDP packets; a lost packet is re-sent, and only its own channel
   waits.
3. The front desk checks no caller. Anyone can dial the extension; the handshake (voiceprint, ALPN,
   ticket) is the only gate.
4. A voice can be imitated. A certificate fingerprint cannot be answered without the private key.
5. The helper is software on the phone, running only while the chat is open in the foreground; and
   the "intercom" also includes the cloud's own metadata address, not only rooms in your house.
