# -*- coding: utf-8 -*-
# 05 — Trust without a CA, and admission to the tunnel (notes B4, B5, C1 threat 3-4).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="05-trust-and-admission", w=W, h=0)

sha = V("sha256_digest"); t_sha = T("sha256_digest")
cv = V("cert_validity_illustrative"); t_cv = T("cert_validity_illustrative")
rl = V("config_rate_limit_illustrative"); t_rl = T("config_rate_limit_illustrative")
tb = V("token_bits_illustrative"); t_tb = T("token_bits_illustrative")
tl = V("token_lifetime_illustrative"); t_tl = T("token_lifetime_illustrative")
tg = V("token_grace_illustrative"); t_tg = T("token_grace_illustrative")
mi = V("quic_min_client_initial_datagram"); t_mi = T("quic_min_client_initial_datagram")
af = V("quic_amplification_factor"); t_af = T("quic_amplification_factor")
ab = V("quic_amplification_budget_one_initial"); t_ab = T("quic_amplification_budget_one_initial")
assert ab == af * mi
rit = V("retry_integrity_tag"); t_rit = T("retry_integrity_tag")
lp = V("control_length_prefix_illustrative"); t_lp = T("control_length_prefix_illustrative")
cm = V("control_msg_max_illustrative"); t_cm = T("control_msg_max_illustrative")
ct = V("control_payload_timeout_illustrative"); t_ct = T("control_payload_timeout_illustrative")
sp = V("socks_listen_port_illustrative"); t_sp = T("socks_listen_port_illustrative")
ids = V("quic_first_stream_ids", "client_bidi"); t_ids = T("quic_first_stream_ids")
cb = V("quic_crypto_error_base"); t_cb = T("quic_crypto_error_base")
a40 = V("tls_alert_handshake_failure"); t_a40 = T("tls_alert_handshake_failure")
a120 = V("tls_alert_no_application_protocol"); t_a120 = T("tls_alert_no_application_protocol")
cc = V("quic_close_codes_example"); t_cc = T("quic_close_codes_example")
base = int(cb, 16)
assert "0x%04X" % (base + a40) == cc["handshake_failure"].upper().replace("0X", "0x")
assert "0x%04X" % (base + a120) == cc["no_application_protocol"].upper().replace("0X", "0x")

BOXES = [title("Trust in the tunnel is borrowed from the app's HTTPS login: the certificate fingerprint and a single-use token "
               "arrive over HTTPS, then the QUIC handshake must match the pin and the ALPN, and stream %d must present the token" % ids[0], W, h=44)]

LANES = [("srv", 170, "CLOUD INSTANCE\nQUIC server", CLOUD),
         ("api", 500, "ASSISTANT SERVICE API\n(HTTPS, user login)", CTRL),
         ("ph", 830, "PHONE APP", PHONE)]
X = {k: x for k, x, _, _ in LANES}
TOP = 66
LINES = []
for k, x, lab, pal in LANES:
    BOXES.append(box("h_" + k, x - 110, TOP, 220, 42, lab, pal, bold=True, font=11))

# boot box on the server lane
BOXES.append(box("boot", 30, 120, 300, 74,
                 "AT FIRST BOOT\nnew ECDSA P-256 key in a pre-created mode-600 file; self-signed certificate, validity %s years %s; "
                 "SHA-256 fingerprint (%d bytes, %d hex chars %s) stored for the config endpoint"
                 % (cv, t_cv, sha["bytes"], sha["hex_chars"], t_sha), CLOUD, font=10, align="left", valign="top"))
EDGES = []
msgs = [
    ("ph", "api", "1  GET config, device ID in a header (rate limit %s per %s s %s)" % (rl["requests"], rl["per_seconds"], t_rl), CTRL_C, False, None),
    ("api", "ph", "2  {enabled, host, port, certFingerprint, alpn, connectionToken}\ntoken: %s random bits %s, single use, %s s %s, device-bound" % (tb, t_tb, tl, t_tl), CTRL_C, True, None),
    ("ph", "srv", "3  QUIC Initial, at least %s bytes %s (via the front door)" % (mi, t_mi), DATA_C, False, None),
    ("srv", "ph", "4  Retry + address-validation token (%s-bit integrity tag %s): no crypto work yet; reply budget %s x %s = %s bytes %s%s"
     % (rit, t_rit, af, mi, ab, t_af, t_ab), EDGE[1], False, None),
    ("ph", "srv", "5  Initial again, returning the Retry token -> TLS 1.3 handshake, ALPN socks5-over-quic", DATA_C, True, None),
    ("srv", "ph", "6  certificate -> phone hashes the leaf DER and compares with the pin from step 2", DATA_C, True, None),
    ("ph", "srv", "7  stream %d %s: %s-byte length %s + JSON {deviceId, platform, token}  (max %s bytes %s, within %s s %s)"
     % (ids[0], t_ids, lp, t_lp, cm, t_cm, ct, t_ct), DATA_C, True, None),
    ("srv", "ph", "8  token + device checked BEFORE attach -> {socksPort: %s} %s, or an error code" % (sp, t_sp), DATA_C, True, None),
]
y = 140
for i, (a, b, lab, col, bold, _) in enumerate(msgs):
    if i == 2:
        y = 260
    BOXES.append(anchor("m%da" % i, X[a], y))
    BOXES.append(anchor("m%db" % i, X[b], y))
    lo, hi = min(X[a], X[b]), max(X[a], X[b])
    nl = lab.count("\n")
    EDGES.append(dict(src="m%da" % i, dst="m%db" % i, sx=0.5, sy=0.5, dx=0.5, dy=0.5, color=col, bold=bold,
                      label=lab, lpos=((lo + hi) / 2.0, y - 11 - 7 * nl), lw=hi - lo - 10, font=10))
    y += 50 + 8 * nl
BOT = y - 20
for k, x, _, _ in LANES:
    y1 = 108 if k != "srv" else 194
    LINES.append(dict(x1=x, y1=y1, x2=x, y2=BOT, color="#999999", dashed=True, sw=1.2))
LINES.append(dict(x1=X["srv"], y1=108, x2=X["srv"], y2=120, color="#999999", dashed=True, sw=1.2))

# right panel: how each check fails
PX0 = 960
BOXES.append(box("fails", PX0, 120, 290, 330,
                 "HOW EACH CHECK FAILS\n\n"
                 "Wrong certificate (stale front-door mapping, man in the middle): fingerprint mismatch -> handshake fails; the phone shows 'failed', no traffic flows.\n\n"
                 "Wrong ALPN (a scanner offering h3): TLS alert %s %s -> QUIC close %s = %s + %s %s%s\n\n"
                 "Unsupported certificate algorithm (Ed25519 with one native phone stack): alert %s %s -> close %s; fix: ECDSA P-256.\n\n"
                 "Spoofed source address: never answers the Retry from that address -> no handshake state, at most %s bytes sent %s.\n\n"
                 "Token reused, expired, unknown or wrong device: stream %d answer invalid_token -> fetch a new config. "
                 "Previous token keeps a %s s grace %s for an in-flight retry."
                 % (a120, t_a120, cc["no_application_protocol"], cb, a120, t_cb, t_cc, a40, t_a40, cc["handshake_failure"],
                    ab, t_ab, ids[0], tg, t_tg),
                 BAD, font=10, align="left", valign="top"))

yl = BOT + 14
BOXES.append(box("legend", 30, yl, 1220, 42,
                 "Legend: purple = control channel (HTTPS over TCP) | green = QUIC data path | amber = address validation (Retry) | red panel = failure modes. "
                 "Bold steps carry the two things the phone must match (pin, ALPN) and the one thing the server must check (token). "
                 "The pin authenticates the server to the phone; the token authenticates the phone to the server.",
                 WHITE, font=10.5, align="left"))

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B4-trust-without-a-ca.md (boot-time certificate, pinning, ALPN gate, close-code decoding, rotation); notes/B5-the-control-stream.md "
    "(config call, token rules, length-prefixed hello, error codes); notes/C1-threat-model.md threats 3-4 (Retry, amplification limit, admission table). "
    "[calc]: close codes asserted equal to quic_crypto_error_base + alert; %s x %s = %s." % (af, mi, ab)],
    30, yl + 54, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
