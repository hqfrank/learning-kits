# -*- coding: utf-8 -*-
# 02 — One SOCKS5 CONNECT, byte by byte, and where DNS happens (notes B1, A1, C1).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="02-socks5-connect-and-remote-dns", w=W, h=0)

ver = V("socks5_version"); t_ver = T("socks5_version")
noauth = V("socks5_methods", "no_auth"); t_m = T("socks5_methods")
conn = V("socks5_commands", "connect"); t_cmd = T("socks5_commands")
at_dom = V("socks5_atyp", "domain"); at4 = V("socks5_atyp", "ipv4"); at6 = V("socks5_atyp", "ipv6"); t_at = T("socks5_atyp")
sz = V("socks5_message_sizes"); t_sz = T("socks5_message_sizes")
rep = V("socks5_reply_codes"); t_rep = T("socks5_reply_codes")
dmax = V("socks5_domain_max_len"); t_dmax = T("socks5_domain_max_len")
sp = V("socks_listen_port_illustrative"); t_sp = T("socks_listen_port_illustrative")
ports = V("allowed_ports_illustrative"); t_ports = T("allowed_ports_illustrative")
vhex = "0x%02X" % ver
ok_code = [k for k, v in rep.items() if v == "succeeded"][0]
deny_code = [k for k, v in rep.items() if v.startswith("connection not allowed")][0]
host_code = [k for k, v in rep.items() if v == "host unreachable"][0]
refused_code = [k for k, v in rep.items() if v == "connection refused"][0]
gen_code = [k for k, v in rep.items() if v.startswith("general")][0]

BOXES = [title("With socks5h the phone, not the cloud, resolves the name: the cloud listener reads only the destination, "
               "forwards the SOCKS5 bytes unchanged, and after one success reply the stream is a plain byte pipe", W, h=44)]

LANES = [("tool", 140, "AGENT TOOL\n(SOCKS5 client)", CLOUD),
         ("lis", 470, "PASSTHROUGH LISTENER\nlocalhost:%s %s" % (sp, t_sp), CLOUD),
         ("ph", 820, "PHONE\n(SOCKS5 server + resolver)", PHONE),
         ("site", 1132, "WEB SITE", SITE)]
X = {k: x for k, x, _, _ in LANES}
TOP, BOT = 70, 640
LINES = []
for k, x, lab, pal in LANES:
    BOXES.append(box("h_" + k, x - 110, TOP, 220, 46, lab, pal, bold=True, font=11))
    LINES.append(dict(x1=x, y1=TOP + 46, x2=x, y2=BOT, color="#999999", dashed=True, sw=1.2))

# cloud | phone boundary band label
BOXES.append(text("cloud_lab", 30, 122, 300, 18, "cloud instance", font=10, fontcolor=CLOUD[1], bold=True))
BOXES.append(text("phone_lab", 660, 122, 300, 18, "user's network", font=10, fontcolor=PHONE[1], bold=True))
LINES.append(dict(x1=645, y1=120, x2=645, y2=BOT, color=PHONE[1], sw=2))

EDGES = []
msgs = [
    ("tool", "lis", "1  method request  %s 01 %s  (%d bytes) %s%s%s" % (vhex, noauth, sz["method_request_one_method"], t_ver, t_m, t_sz), DATA_C, False),
    ("lis", "tool", "2  method reply  %s %s  (%d bytes): the listener answers this itself" % (vhex, noauth, sz["method_reply"]), DATA_C, False),
    ("tool", "lis", "3  CONNECT  %s %s 00 ATYP %s len name port  (%s bytes) %s%s"
     % (vhex, conn, at_dom, sz["connect_domain"].split(" (")[0], t_cmd, t_at), DATA_C, True),
    ("lis", "ph", "4  open a new QUIC stream; forward the original method request", DATA_C, False),
    ("ph", "lis", "5  method reply %s %s" % (vhex, noauth), DATA_C, False),
    ("lis", "ph", "6  forward the original CONNECT bytes unchanged (still the NAME)", DATA_C, True),
    ("ph", "site", "8  TCP connect from the phone's address", DATA_C, True),
    ("ph", "lis", "9  reply REP %s succeeded (%d bytes) %s" % (ok_code, sz["reply_ipv4"], t_rep), DATA_C, False),
    ("lis", "tool", "10  reply passed to the tool unchanged", DATA_C, False),
]
y = 160
ys = {}
for i, (a, b, lab, col, bold) in enumerate(msgs):
    if i == 3:
        y += 34   # room for the listener note
    if i == 6:
        y += 70   # leave room for the phone's DNS + filter note (step 7)
    BOXES.append(anchor("m%da" % i, X[a], y))
    BOXES.append(anchor("m%db" % i, X[b], y))
    mid = (X[a] + X[b]) / 2.0
    EDGES.append(dict(src="m%da" % i, dst="m%db" % i, sx=0.5, sy=0.5, dx=0.5, dy=0.5, color=col,
                      bold=bold, label=lab, lpos=(mid, y - 11), lw=max(abs(X[a] - X[b]) - 16, 440 if i == 2 else 0), font=10))
    ys[i] = y
    y += 42

# listener note between 3 and 4
BOXES.append(box("n_lis", X["lis"] - 160, ys[2] + 12, 320, 34,
                 "the listener parses the destination only, for the cloud deny list (C1); the name is up to %d octets %s" % (dmax, t_dmax), NOTE, font=9.5))
# phone DNS + filter note (step 7)
BOXES.append(box("n_ph", X["ph"] - 150, ys[5] + 14, 300, 62,
                 "7  RESOLVES THE NAME with the phone's own resolver -> the server a local user would get; "
                 "destination filter on the RESOLVED address (no private ranges, ports %s %s), then connects to that exact address"
                 % ("/".join(map(str, ports)), t_ports),
                 PHONE, font=9.5, align="left", bold=False))
# byte pipe
yp = ys[8] + 44
BOXES.append(anchor("pipe_a", X["tool"], yp))
BOXES.append(anchor("pipe_b", X["site"], yp))
EDGES.append(dict(src="pipe_a", dst="pipe_b", sx=0.5, sy=0.5, dx=0.5, dy=0.5, color="#333333", bold=True,
                  label="11  TLS 1.3 + HTTP, end to end between tool and site: the QUIC stream is now a byte pipe; listener and phone see only TLS records",
                  lpos=((X["tool"] + X["site"]) / 2.0, yp - 11), lw=960, font=10))
BOT2 = yp + 20
for l in LINES:
    if l["y2"] == BOT:
        l["y2"] = BOT2
# break the cloud-side and phone lifelines around the notes they would cross
nb = [b for b in BOXES if b["id"] in ("n_lis", "n_ph")]
for b, lane in zip(nb, ("lis", "ph")):
    for l in list(LINES):
        if l["x1"] == X[lane] and l["y1"] < b["y"] and l["y2"] > b["y"] + b["h"]:
            LINES.append(dict(l, y1=b["y"] + b["h"]))
            l["y2"] = b["y"]

# comparison panel: socks5 vs socks5h
yc = BOT2 + 16
BOXES.append(text("cmp_h", 30, yc, 1220, 20, "THE ONE LETTER THAT MATTERS: the client URL decides who resolves the name (curl documentation; RFC 1928 allows both)",
                  bold=True, font=12))
yc += 24
BOXES.append(box("c5", 30, yc, 600, 62,
                 "socks5://  -  the CLIENT resolves, in the cloud\nCONNECT carries ATYP %s IPv4 (%d bytes) or %s IPv6 (%d bytes) with an address. "
                 "The DNS answer was picked for the cloud region, so the phone connects to a server far from the user: "
                 "exit address and server choice disagree." % (at4, sz["connect_ipv4"], at6, sz["connect_ipv6"]),
                 BAD, font=10.5, align="left", valign="top"))
BOXES.append(box("c5h", 650, yc, 600, 62,
                 "socks5h://  -  the PROXY resolves, on the phone (chosen)\nCONNECT carries ATYP %s with the name. The phone's resolver picks the server a local user gets: "
                 "exit address and server choice agree, and no separate DNS proxy is needed. The browser spells this socks5:// (it always resolves on the proxy side)."
                 % at_dom, PHONE, font=10.5, align="left", valign="top"))
yc += 74
BOXES.append(box("fail", 30, yc, 1220, 40,
                 "Failure replies from the phone %s:  %s = filter refused (the proxy's own policy, not the site)  |  %s = name did not resolve  |  %s = the site refused TCP  |  "
                 "%s = general failure (also the listener's answer when the tunnel has no free stream)."
                 % (t_rep, deny_code, host_code, refused_code, gen_code), WHITE, font=10.5, align="left"))
yc += 52
BOXES.append(box("legend", 30, yc, 1220, 26,
                 "Legend: bold arrows carry the destination NAME or open a connection | green = cloud->phone path | blue lanes = cloud instance | green lanes = user's network | grey = notes. Bytes shown as hex.",
                 WHITE, font=10.5, align="left"))

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B1-socks5-in-ten-minutes.md (two exchanges, field layouts, reply codes, socks5 vs socks5h, passthrough); notes/A1-the-end-to-end-picture.md "
    "(one request end to end; browser socks5:// spelling); notes/C1-threat-model.md (filter after DNS, on the exact address). "
    "In 1 the '01' is NMETHODS = 1 and the '00' in 3 is RSV; L = name length."],
    30, yc + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
