# -*- coding: utf-8 -*-
# 04 — Time to first response byte, through the phone vs direct (note A1 latency model).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="04-latency-budget", w=W, h=0)

rcp = V("rtt_cloud_phone_illustrative"); t_rcp = T("rtt_cloud_phone_illustrative")
rps = V("rtt_phone_site_illustrative"); t_rps = T("rtt_phone_site_illustrative")
rcs = V("rtt_cloud_site_illustrative"); t_rcs = T("rtt_cloud_site_illustrative")
dns = V("phone_dns_typical_illustrative"); t_dns = T("phone_dns_typical_illustrative")
model = V("ttfb_model_illustrative"); t_model = T("ttfb_model_illustrative")
hs = V("quic_handshake_round_trips"); t_hs = T("quic_handshake_round_trips")


def parts(net, pipelined=False):
    c = rcp[net]
    p = [] if pipelined else [("SOCKS5 method", c, "RTTcp")]
    p += [("CONNECT", c + dns + rps, "RTTcp + DNS + RTTps"),
          ("TLS 1.3", c + rps, "RTTcp + RTTps"),
          ("HTTP req/resp", c + rps, "RTTcp + RTTps")]
    return p


rows = [("direct from the cloud (no phone)", [("TCP", rcs, "RTTcs"), ("TLS 1.3", rcs, "RTTcs"), ("HTTP", rcs, "RTTcs")], "direct_from_cloud"),
        ("via phone, Wi-Fi", parts("wifi"), "wifi"),
        ("via phone, Wi-Fi, pipelined (not used by the source)", parts("wifi", True), "wifi_pipelined"),
        ("via phone, cellular", parts("cellular"), "cellular"),
        ("via phone, cellular, pipelined (not used by the source)", parts("cellular", True), "cellular_pipelined")]
# the diagram's own arithmetic must reproduce the kit's model
for _, p, k in rows:
    assert sum(x[1] for x in p) == model[k], (k, sum(x[1] for x in p), model[k])
ratio_w = model["wifi"] / float(model["direct_from_cloud"])
ratio_c = model["cellular"] / float(model["direct_from_cloud"])
assert hs["tcp_plus_tls13"] == 2   # direct path: TCP + TLS 1.3 handshakes = 2 RTT before HTTP

BOXES = [title("Through the phone the first response byte costs about %.0fx (Wi-Fi) to %.0fx (cellular) [calc] the direct path, "
               "because every round trip after CONNECT travels cloud -> phone -> site and back (illustrative model)" % (ratio_w, ratio_c), W, h=44)]

X0, PX = 420, 1.25       # x of 0 ms, px per ms
Y0, RH = 108, 62
PAL = {"SOCKS5 method": EDGE, "CONNECT": PHONE, "TLS 1.3": CLOUD, "HTTP req/resp": WHITE,
       "TCP": NOTE, "HTTP": WHITE}
BOXES.append(text("hdr", 30, Y0 - 26, 1220, 20,
                  "Time to first response byte, server time excluded. Bar length to scale: %s px per ms. Segment labels give the cost of each step." % num(PX),
                  bold=True, font=12))
LINES = []
for i, (lab, p, k) in enumerate(rows):
    y = Y0 + i * RH
    BOXES.append(text("l%d" % i, 30, y, 380, RH - 12, "%s\ntotal %s ms %s" % (lab, model[k], t_model), font=11, valign="middle",
                      bold=(i in (0, 1, 3))))
    x = X0
    for j, (name, ms, f) in enumerate(p):
        w = int(round(ms * PX))
        BOXES.append(box("b%d_%d" % (i, j), x, y + 4, w, RH - 20, ("%s\n%s = %s" % (name, f, ms) if w > 90 else "%s\n%s" % (name, ms)) if w > 60 else "",
                         PAL[name], rounded=False, font=9.5, dashed=("pipelined" in k)))
        x += w
    if k == "direct_from_cloud":
        BOXES.append(text("dlab", x + 10, y + 4, 600, RH - 20,
                          " + ".join("%s %s" % (n, ms) for n, ms, _ in p) + "  (each one RTTcs: the cloud talks to the site directly)",
                          font=10.5, valign="middle"))
LINES.append(dict(x1=X0, y1=Y0 - 4, x2=X0, y2=Y0 + len(rows) * RH, color="#333333", sw=1.2))
yax = Y0 + len(rows) * RH
LINES.append(dict(x1=X0, y1=yax, x2=X0 + 650 * PX, y2=yax, color="#333333", sw=1.2))
for ms in range(0, 651, 100):
    LINES.append(dict(x1=X0 + ms * PX, y1=yax, x2=X0 + ms * PX, y2=yax + 5, color="#333333", sw=1.2))
    BOXES.append(text("t%d" % ms, X0 + ms * PX - 25, yax + 6, 50, 16, "%d ms" % ms, font=10, align="center"))

yi = yax + 34
BOXES.append(box("inputs", 30, yi, 600, 80,
                 "INPUTS (all illustrative round values)\n"
                 "RTTcp cloud<->phone: Wi-Fi %s ms, cellular %s ms %s\nRTTps phone<->site: %s ms %s\nDNS on the phone: %s ms %s\nRTTcs cloud<->site: %s ms %s"
                 % (rcp["wifi"], rcp["cellular"], t_rcp, rps, t_rps, dns, t_dns, rcs, t_rcs),
                 NOTE, font=10.5, align="left", valign="top"))
BOXES.append(box("why", 650, yi, 600, 80,
                 "READING IT\n"
                 "- The two SOCKS5 exchanges add RTTcp each; DNS moves to the phone.\n"
                 "- Direct = TCP + TLS 1.3 handshakes (%d round trips %s) + one HTTP exchange.\n"
                 "- Pipelining: the phone always picks 'no auth', so the listener could send method request and CONNECT together and save one RTTcp (dashed bars; an idea the source does not use)."
                 % (hs["tcp_plus_tls13"], t_hs),
                 NOTE, font=10.5, align="left", valign="top"))
BOXES.append(box("legend", 30, yi + 92, 1220, 26,
                 "Legend: amber = SOCKS5 method exchange | green = CONNECT (includes phone DNS and the phone's TCP connect) | blue = TLS 1.3 handshake | white = HTTP exchange | grey = direct TCP | dashed = pipelined variant.",
                 WHITE, font=10.5, align="left"))
EDGES = []

src_box, bottom = footer_box(T, [
    "Mechanism: notes/A1-the-end-to-end-picture.md (latency model table, pipelining idea); notes/B2-quic-for-this-job.md (handshake round trips). "
    "[calc]: segment costs from the inputs; each row sum is asserted equal to ttfb_model_illustrative; ratios %s / %s = %.1f and %s / %s = %.1f. "
    "The kit's latency targets (latency_target_illustrative) are not drawn: the illustrative Wi-Fi p50 target sits below this modelled floor, so the two illustrative values do not agree."
    % (model["wifi"], model["direct_from_cloud"], ratio_w, model["cellular"], model["direct_from_cloud"], ratio_c)],
    30, yi + 132, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
