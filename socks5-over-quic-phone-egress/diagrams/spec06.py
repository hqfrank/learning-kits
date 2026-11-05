# -*- coding: utf-8 -*-
# 06 — Five threats, five layers along the path (note C1).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="06-threat-layers", w=W, h=0)

v4 = V("blocked_ranges_ipv4"); t_v4 = T("blocked_ranges_ipv4")
v6 = V("blocked_ranges_ipv6"); t_v6 = T("blocked_ranges_ipv6")
ports = V("allowed_ports_illustrative"); t_ports = T("allowed_ports_illustrative")
md = V("metadata_address"); t_md = T("metadata_address")
enc = V("metadata_address_encodings"); t_enc = T("metadata_address_encodings")
af = V("quic_amplification_factor"); t_af = T("quic_amplification_factor")
ab = V("quic_amplification_budget_one_initial"); t_ab = T("quic_amplification_budget_one_initial")
mu = V("max_unvalidated_handshakes_illustrative"); t_mu = T("max_unvalidated_handshakes_illustrative")
me = V("max_established_connections_illustrative"); t_me = T("max_established_connections_illustrative")
tl = V("token_lifetime_illustrative"); t_tl = T("token_lifetime_illustrative")
sp = V("socks_listen_port_illustrative"); t_sp = T("socks_listen_port_illustrative")
deny = [k for k, v in V("socks5_reply_codes").items() if v.startswith("connection not allowed")][0]; t_rep = T("socks5_reply_codes")

BOXES = [title("Five threats, five layers: cloud-side checks catch the common cases early, and the phone's filter on the RESOLVED "
               "address is the authoritative guard against reaching the user's own network", W, h=44)]

# --- the path strip: where each layer sits ------------------------------------------
strip = [
    ("p_tool", "agent tool\n(may be steered by a prompt injection)", CLOUD),
    ("p_lis", "listener\nlocalhost:%s %s" % (sp, t_sp), CLOUD),
    ("p_udp", "public UDP port\n(open to all sources)", EDGE),
    ("p_adm", "tunnel admission\n(handshake + stream 0)", EDGE),
    ("p_ph", "phone\nresolver + filter", PHONE),
    ("p_net", "internet\n(public web ports)", SITE),
]
SX, SW, SG, SY = 30, 175, 34, 74
for i, (id_, lab, pal) in enumerate(strip):
    BOXES.append(box(id_, SX + i * (SW + SG), SY, SW, 48, lab, pal, font=10.5, bold=True))
EDGES = [dict(src=strip[i][0], dst=strip[i + 1][0], sx=1, sy=0.5, dx=0, dy=0.5, color=DATA_C, bold=True)
         for i in range(len(strip) - 1)]
layer_at = [("5", 0), ("2", 1), ("3", 2), ("4", 3), ("1", 4)]
for n, i in layer_at:
    BOXES.append(box("lay%s" % n, SX + i * (SW + SG) + SW / 2 - 14, SY + 54, 28, 22, n, BAD, font=11, bold=True, rx=11))

# --- the five columns ---------------------------------------------------------------
v4_txt = ", ".join(v4.keys())
v6_txt = ", ".join(k for k in v6.keys())
cols = [
    ("1  SSRF INTO THE USER'S NETWORK",
     "Anything that can send CONNECT makes the phone open TCP: router admin page, home NAS, office intranet. DNS rebinding: a public name that resolves to a private address.",
     "Phone-side destination filter, applied AFTER resolution and BEFORE connect, on the exact address it then dials. Refused with REP %s %s.\nIPv4 %s %s\nIPv6 %s %s (IPv4-mapped: apply the IPv4 rules)\nPorts %s only %s."
     % (deny, t_rep, v4_txt, t_v4, v6_txt, t_v6, "/".join(map(str, ports)), t_ports),
     "Public web ports on public addresses stay reachable: that is the product."),
    ("2  CLOUD METADATA CREDENTIALS",
     "A request that reaches the link-local metadata service %s %s through some path could leak instance credentials." % (md, t_md),
     "Defence in depth in the listener, before any stream opens: refuse 169.254/16, fe80::/10, known metadata names, and other spellings of the address (decimal %s, hex %s, dotted octal %s ... %s). The direct-fallback dialer repeats the post-resolution check. NO_PROXY keeps legitimate metadata traffic off the proxy."
     % (enc["decimal"], enc["hex"], enc["dotted_octal"], t_enc),
     "Short forms and names that resolve to the address pass this check; the phone's filter (1) is the authoritative guard."),
    ("3  THE OPEN UDP PORT",
     "Amplification: spoofed small Initials make the server flood a victim. Handshake exhaustion: a flood of Initials burns public-key CPU.",
     "Address validation on every new connection (Retry before crypto work); the server sends at most %s x what it received %s, %s bytes for one Initial %s. Caps: %s unvalidated handshakes %s, %s connections %s. 0-RTT off (no replay)."
     % (af, t_af, ab, t_ab, mu, t_mu, me, t_me),
     "One extra round trip per new connection; the phone connects rarely, so it is cheap."),
    ("4  ADMISSION TO THE TUNNEL",
     "An attacker who learns the address tries to attach as the user's phone, or to impersonate the server to the phone.",
     "Server to phone: pinned certificate fingerprint. Protocol: private ALPN (stops scanners, authenticates no one). Phone to server: single-use, device-bound token valid %s s %s, checked before attach." % (tl, t_tl),
     "Whoever reads the HTTPS config response gets a token and its device ID; mutual TLS is the named fix. A stolen fingerprint alone gives nothing: it is public."),
    ("5  A PROCESS ON THE INSTANCE",
     "The listener has no SOCKS5 authentication. A manipulated tool can push traffic through the phone, and can read the QUIC private key (same user account).",
     "Bind the listener to localhost only, so only the instance's own processes reach it; the phone filter (1) and port allowlist bound what they can reach.",
     "Accepted in a single-user instance; a separate service account for the QUIC server is listed as hardening. A fully compromised instance can do anything the agent can."),
]
CW, CG, CY = 236, 10, 170
rows_h = [40, 66, 166, 70]
heads = ["THREAT", "HOW IT REACHES", "CONTROL", "WHAT REMAINS"]
for j, (head, how, ctrl, rem) in enumerate(cols):
    x = 30 + j * (CW + CG)
    y = CY
    for r, (txt, pal, bold) in enumerate([(head, BAD, True), (how, NOTE, False), (ctrl, PHONE if j == 0 else CLOUD, False), (rem, WHITE, False)]):
        BOXES.append(box("c%d_%d" % (j, r), x, y, CW, rows_h[r], txt, pal, font=10 if r else 11, bold=bold,
                         align="left", valign="top" if r else "middle", dashed=(r == 3)))
        y += rows_h[r] + 6
yb = CY + sum(rows_h) + 6 * 4

BOXES.append(box("legend", 30, yb, 1220, 42,
                 "Legend: top strip = the path a proxied connection takes; red circles = where each layer sits. Columns: red = threat | grey = how it reaches its target | "
                 "green = the authoritative control (on the phone) | blue = cloud-side controls | dashed = residual risk the design accepts. "
                 "What the user still carries: sites attribute the agent's traffic to the user's address; per-user kill switches and attribution counters answer that (C4, C6).",
                 WHITE, font=10.5, align="left"))
LINES = []

src_box, bottom = footer_box(T, [
    "Mechanism: notes/C1-threat-model.md (five threats, phone-side filter after DNS, metadata filter and its encodings and limits, amplification and Retry, handshake caps, admission table, localhost bind, accepted risks); "
    "notes/B4-trust-without-a-ca.md and B5-the-control-stream.md (pin, ALPN, token). Address encodings: the classic SSRF filter bypasses in the OWASP SSRF prevention cheat sheet."],
    30, yb + 54, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
