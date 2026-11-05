# -*- coding: utf-8 -*-
# 03 — Deadlines in the handshake phase and the commit point (note C2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="03-deadlines-and-commit-point", w=W, h=0)

so = V("stream_open_timeout_illustrative"); t_so = T("stream_open_timeout_illustrative")
mr = V("method_reply_deadline_illustrative"); t_mr = T("method_reply_deadline_illustrative")
cr = V("connect_reply_deadline_illustrative"); t_cr = T("connect_reply_deadline_illustrative")
dns = V("phone_dns_worst_illustrative"); t_dns = T("phone_dns_worst_illustrative")
pc = V("phone_connect_timeout_illustrative"); t_pc = T("phone_connect_timeout_illustrative")
ri = V("relay_idle_timeout_illustrative"); t_ri = T("relay_idle_timeout_illustrative")
gen = [k for k, v in V("socks5_reply_codes").items() if v.startswith("general")][0]; t_rep = T("socks5_reply_codes")
cap = V("phone_max_incoming_streams_illustrative"); t_cap = T("phone_max_incoming_streams_illustrative")
idle = V("conn_idle_timeout_illustrative"); t_idle = T("conn_idle_timeout_illustrative")
need = dns + pc                                    # my arithmetic
assert cr > need, "connect deadline must exceed DNS + connect"

BOXES = [title("Every wait before the CONNECT reply has a deadline, so a dead phone becomes an invisible switch to a direct connection; "
               "after the reply reaches the tool the connection is committed and a failure is a reset (illustrative deadlines)", W, h=44)]

# --- chart: deadline lengths to scale -----------------------------------------
X0, PX = 470, 30            # x of 0 s, px per second
AX_MAX = 24
Y0 = 120
ROWH = 54
BOXES.append(text("axis_h", 30, Y0 - 34, 1220, 20,
                  "LISTENER STEPS FOR ONE TOOL CONNECTION. Bars are the longest wait allowed at each step, to scale (%d px per second); they are maxima, not a typical timeline."
                  % PX, bold=True, font=12))
rows = [
    ("r1", "steps 1-4  read method request, answer 'no auth', read CONNECT, cloud deny list, tunnel present?",
     None, "no wait: no tunnel -> direct connection now"),
    ("r5", "step 5  open a stream to the phone %s" % t_so, so,
     "stream cap %s %s reached -> REP %s at once, no queue %s" % (cap, t_cap, gen, t_rep)),
    ("r6", "step 6  forward method request, wait for the phone's method reply (answered from memory) %s" % t_mr, mr, ""),
    ("r7", "step 7  forward CONNECT, wait for the phone's reply %s" % t_cr, cr, ""),
]
LINES = []
for i, (id_, lab, secs, note) in enumerate(rows):
    y = Y0 + i * ROWH
    BOXES.append(text(id_ + "_l", 30, y, 430, ROWH - 8, lab, font=11, valign="middle"))
    if secs:
        BOXES.append(box(id_, X0, y + 8, int(secs * PX), ROWH - 22, "%s s" % secs, CLOUD, rounded=False, bold=True, font=11))
    if note:
        nx = X0 + (int(secs * PX) + 12 if secs else 0)
        BOXES.append(text(id_ + "_n", nx, y, 1250 - nx, ROWH - 8, note, font=10.5, valign="middle", fontcolor="#555555"))
# what the 20 s must cover: DNS worst + connect timeout, stacked under row 7
y7 = Y0 + 3 * ROWH + ROWH - 10
BOXES.append(box("dns", X0, y7, int(dns * PX), 26, "phone DNS worst %s s %s" % (dns, t_dns), PHONE, rounded=False, font=10))
BOXES.append(box("pcon", X0 + int(dns * PX), y7, int(pc * PX), 26, "phone TCP connect %s s %s" % (pc, t_pc), PHONE, rounded=False, font=10))
BOXES.append(text("sum", X0 + int(need * PX) + 10, y7 - 2, 1250 - X0 - int(need * PX) - 10, 30,
                  "%s + %s = %s s [calc], under the %s s deadline: a slow but live phone is not cut off" % (dns, pc, need, cr),
                  font=10.5, valign="middle"))
yax = y7 + 40
LINES.append(dict(x1=X0, y1=Y0 - 6, x2=X0, y2=yax, color="#333333", sw=1.2))
LINES.append(dict(x1=X0, y1=yax, x2=X0 + AX_MAX * PX, y2=yax, color="#333333", sw=1.2))
for s in range(0, AX_MAX + 1, 4):
    LINES.append(dict(x1=X0 + s * PX, y1=yax, x2=X0 + s * PX, y2=yax + 5, color="#333333", sw=1.2))
    BOXES.append(text("tk%d" % s, X0 + s * PX - 20, yax + 6, 40, 16, "%d s" % s, font=10, align="center"))

# --- the two zones ---------------------------------------------------------------
yz = yax + 66
BOXES.append(box("zone_a", 30, yz, 600, 112,
                 "HANDSHAKE PHASE (steps 1-7): fallback is INVISIBLE\n\n"
                 "The tool has received only the 'no auth' reply and is still waiting for its CONNECT reply. If any deadline fires, "
                 "the listener closes the phone stream and opens a DIRECT connection from the cloud address instead. "
                 "The tool cannot tell, except by its exit address.\n\nWithout these deadlines a dead phone would block each read until the "
                 "QUIC idle timeout (%s s %s)." % (idle, t_idle),
                 CLOUD, font=11, align="left", valign="top"))
BOXES.append(box("zone_b", 650, yz, 600, 112,
                 "RELAY (step 8): COMMITTED, failure is a RESET\n\n"
                 "After the CONNECT reply the tool starts TLS through the phone; its TLS session is bound to the phone's TCP "
                 "connection to the site, so no fallback is possible. An idle relay closes after %s s %s; an active transfer "
                 "that loses the phone gets a partial response and a reset. The tool's HTTP client retries on a new connection, "
                 "which goes direct if the tunnel is gone." % (ri, t_ri),
                 BAD, font=11, align="left", valign="top"))
EDGES = [dict(src="zone_a", dst="zone_b", sx=1, sy=0.5, dx=0, dy=0.5, color="#333333", bold=True)]
BOXES.append(box("commit", 545, yz - 36, 190, 30, "COMMIT POINT: CONNECT reply sent to the tool", EDGE, bold=True, font=10))

BOXES.append(box("legend", 30, yz + 126, 1220, 26,
                 "Legend: blue bars = listener deadlines (cloud side) | green bars = the phone-side work the CONNECT deadline must cover | blue panel = invisible fallback zone | red panel = committed zone.",
                 WHITE, font=10.5, align="left"))

src_box, bottom = footer_box(T, [
    "Mechanism: notes/C2-limits-and-failure-handling.md (handshake-phase table, the invariant, deadlines matched to the work, what the tool sees, fail fast on stream exhaustion). "
    "[calc]: %s + %s = %s s." % (dns, pc, need)],
    30, yz + 166, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
