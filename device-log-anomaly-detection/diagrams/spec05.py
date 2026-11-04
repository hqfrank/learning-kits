# 05 — From anomaly to root cause: partition by thread, mine transitions, compare with the golden path (B5, C4).
# Type: swimlane-ish stream -> partitions, plus a workflow / state-machine graph with two anomaly kinds.
from _common import *

S = Src()
W = 1280
B, E, L = [], [], []
B.append(title("Root cause starts where the sequence leaves the normal path: partition the log by "
               "thread, count transitions, and compare them with the golden sequence mined from many "
               "devices", W))

# ---------- A: interleaved stream ----------
B.append(text("ha", 20, 78, 600, 18, "**A. One interleaved stream, two threads** [A1, B5] (toy lines)",
              font=12))
rows = [("10:00:01.100", "845", "scan start", 0), ("10:00:01.100", "901", "dhcp renew", 1),
        ("10:00:01.230", "845", "assoc start", 0), ("10:00:01.231", "901", "dhcp ack", 1),
        ("10:00:01.480", "845", "auth ok", 0), ("10:00:01.480", "845", "connected", 0),
        ("10:00:05.010", "845", "disconnected reason=%s" %
         fmt(raw("ieee80211_reason_4way_handshake_timeout")), 0),
        ("10:00:05.020", "845", "network bounce", 0)]
S.tag("ieee80211_reason_4way_handshake_timeout")
for i, (t, tid, tpl, th) in enumerate(rows):
    B.append(box("r%d" % i, 20, 100 + i * 24, 300, 22, "%s   tid %s   %s" % (t, tid, tpl),
                 BLUE if th == 0 else PURPLE, BLUE_S if th == 0 else PURPLE_S, rounded=False,
                 align="left", font=10.5, sw=1))
B.append(text("tie", 20, 296, 300, 32,
              "same timestamp on two lines (ms resolution): true order unknown", font=10,
              color="#555555"))

# partitions
B.append(box("p1", 360, 100, 260, 60,
             "**thread 845, sorted by time**\nscan start -> assoc start -> auth ok -> connected "
             "-> disconnected -> network bounce", BLUE, BLUE_S, align="left", valign="top",
             font=10.5))
B.append(box("p2", 360, 180, 260, 44, "**thread 901**\ndhcp renew -> dhcp ack", PURPLE,
             PURPLE_S, align="left", valign="top", font=10.5))
B.append(box("bad", 360, 232, 260, 76,
             "**trap: sort the whole log by time**\nscan start -> dhcp renew -> assoc start -> "
             "dhcp ack ... gives edges that never happen in the code. Partition by pid/tid first.",
             RED, RED_S, align="left", valign="top", font=10.5, dash="6,4"))
L.append(dict(pts=[(320, 136), (360, 136)], color=BLUE_S, sw=2, arrow="end"))
L.append(dict(pts=[(320, 200), (360, 200)], color=PURPLE_S, sw=2, arrow="end"))
B.append(box("mat", 20, 336, 600, 60,
             "**Transition count matrix A (N x N templates)** [B5]: for each consecutive pair (i, j) "
             "inside one thread, A[i][j] += 1. Skip the edge into a task-start template so one task's "
             "end is not linked to the next. Drop impossible timestamps (cache replayed after a "
             "reboot). Ties average out over many windows.", GREEN, GREEN_S, align="left",
             valign="top", font=10.5))

# ---------- B: workflow graph ----------
B.append(text("hb", 650, 78, 610, 18,
              "**B. Workflow (empirical control-flow graph) from many healthy devices** [B5]", font=12))
gx, gy, gw, gh = [650, 805, 960, 1115], 104, 140, 40
for i, lab in enumerate(["scanning", "associating", "authenticating", "connected"]):
    B.append(box("g%d" % i, gx[i], gy, gw, gh, lab, GREEN, GREEN_S, font=11, bold=True, sw=2))
    if i:
        E.append(dict(src="g%d" % (i - 1), dst="g%d" % i, sx=1, sy=0.5, dx=0, dy=0.5,
                      color=GREEN_S, sw=2.5))
B.append(text("gold", 650, 148, 610, 18,
              "golden sequence (green): the normal order for the task, shown next to the anomalous one",
              font=10, color=GREEN_S))
# sequence anomaly ghost
B.append(box("ghost", 805, 196, 160, 44, "association complete\n(expected child)", "#ffffff",
             RED_S, font=10.5, dash="6,4", sw=2))
L.append(dict(pts=[(875, 168), (875, 196)], color=RED_S, sw=1.5, dash="5,3", arrow="end"))
B.append(text("seqa", 650, 246, 300, 48,
              "**sequence anomaly**: an expected child does not appear within its usual lag after "
              "its parent (missing in thread 845)", font=10.5, color=RED_S))
# disconnect branch
B.append(box("disc", 1115, 210, 140, 40, "disconnected", AMBER, AMBER_S, font=11, bold=True,
             sw=2))
E.append(dict(src="g3", dst="disc", sx=0.5, sy=1, dx=0.5, dy=0, color=AMBER_S, sw=2))
B.append(text("par", 945, 160, 166, 40,
              "parameter: reason %s = 4-way handshake timeout" %
              S.v("ieee80211_reason_4way_handshake_timeout", u="", tag=False) + " %s" %
              S.tag("ieee80211_reason_4way_handshake_timeout"), font=10, color=AMBER_S,
              align="right"))
B.append(box("rec", 1115, 320, 140, 40, "reconnect success", GREEN, GREEN_S, font=11, bold=True,
             sw=2))
B.append(box("bnc", 960, 320, 140, 40, "network bounce", RED, RED_S, font=11, bold=True, sw=2,
             dash="6,4"))
E.append(dict(src="disc", dst="rec", sx=0.5, sy=1, dx=0.5, dy=0, color=GREEN_S, sw=4))
E.append(dict(src="disc", dst="bnc", sx=0.2, sy=1, dx=0.6, dy=0, color=RED_S, sw=1.5, dash="6,4"))
B.append(text("dista", 650, 300, 300, 60,
              "**distribution anomaly**: the probability of an edge changes. After 'disconnected' "
              "the share to 'reconnect success' (thick) falls, the share to 'network bounce' rises.",
              font=10.5, color=RED_S))
B.append(text("obs", 650, 368, 610, 46,
              "The graph is the OBSERVED graph, not the code's: paths the code allows but healthy "
              "devices never take are absent, so their appearance is itself a signal. Normal "
              "transition statistics need many devices over long periods.", font=10, color="#444444"))

# ---------- bottom row: what the engineer gets ----------
YB = 420
B.append(box("ctx", 20, YB, 400, 72,
             "**1 Narrow the search (cascade)** [B5]: the metric says which devices, roughly when, "
             "and what (e.g. disconnects with reason %s). Traps: metrics aggregated hourly or daily; "
             "device logs in local time, metrics in UTC." %
             S.v("ieee80211_reason_4way_handshake_timeout", u="", tag=False), BLUE, BLUE_S,
             align="left", valign="top", font=10.5))
B.append(box("tools", 440, YB, 400, 72,
             "**2 Show the departure** [B5]: golden sequence beside the anomalous one; state-machine "
             "search (ordered events + max time span -> every match with raw lines); a chosen "
             "parameter over time; replay through the print statements if templates map to code.",
             GREEN, GREEN_S, align="left", valign="top", font=10.5))
B.append(box("hum", 860, YB, 400, 72,
             "**3 Hypothesis, not verdict** [B5, C4]: the anomalous template is often a symptom "
             "downstream of the cause in another component (DHCP, time sync, a kernel driver). Output "
             "= top windows, top templates, the departing edge, the raw lines.", AMBER, AMBER_S,
             align="left", valign="top", font=10.5))
E.append(dict(src="ctx", dst="tools", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))
E.append(dict(src="tools", dst="hum", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))

B.append(panel("legend", 20, YB + 84, 1240, 30,
               "**Legend** — blue / purple = lines of two threads; green = normal workflow and golden "
               "sequence (edge thickness = share of transitions); red dashed = anomaly (missing child, "
               "shifted edge, wrong sort); amber = the triggering event and the human step. Toy lines, "
               "no data.", font=10.5))
n = S.footnote_lines()
sy = YB + 124
sh = int(12.5 * n + 22)
B.append(sources(S, 20, sy, 1240, sh, extra="Workflow idea: Du et al., DeepLog, CCS 2017, §4.4."))
PAGE = dict(name="05-anomaly-to-root-cause", w=W, h=sy + sh + 14)
BOXES, EDGES, LINES = B, E, L
