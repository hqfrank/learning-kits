# 02 — Core map and observers (notes A1, A5). Numbers via V() from ../constants.json; tags via Tags().
from _common import *

W = 1480
PAGE = dict(name="02-core-map-and-observers", w=W, h=900)
T = Tags()
OBS, OBS_S = "#ffd59e", "#c47a00"
ISO, ISO_S = "#f0f0f0", "#666666"

share = V("saturated_core_equal_share")
ia = V("interaction_accepted_ms")
pr = V("probe_receive_delay_ms")
wpb = V("pool_wait_per_busy_full")

BOXES = [title("One reserved core was saturated by three equal tenants, one of them our probe: moving the probe "
               "to a pool core freed the interaction service but cost the camera frames, so no placement is free "
               "on this layout", W, h=60, font=20)]

# ---- group frames
BOXES += [
    panel("gpool", 30, 84, 708, 262, "", fill="#f4f8fd", stroke=CPU_S),
    text("gpool_t", 40, 90, 690, 40,
         "**POOL: %s shared cores** %s, shared by most services under CFS (the camera, the object "
         "detector, audio input ...); attribution to one pool core is approximate" % (f(V("pool_cores")), T("pool_cores")),
         font=11.5),
    panel("giso", 750, 84, 700, 262, "", fill="#fafafa", stroke=ISO_S),
    text("giso_t", 760, 90, 680, 40,
         "**RESERVED: %s cores** %s, removed from the general scheduler (isolcpus), services pinned by "
         "container cpuset. Board: an Orin-class board, %s cores in all %s"
         % (f(V("reserved_cores")), T("reserved_cores"), f(V("board_cores")), T("board_cores")), font=11.5),
]
npool = V("pool_cores")
cwid = int((680 - (npool - 1) * 8) / npool)
for c in range(npool):
    x = 44 + c * (cwid + 8)
    if c == npool - 1:
        BOXES.append(dict(id="pcore%d" % c, x=x, y=148, w=cwid, h=62, fill=OBS, stroke=OBS_S, dash="5,3", sw=2,
                          label="**pool core**\nprobe moved here", font=10))
    else:
        BOXES.append(dict(id="pcore%d" % c, x=x, y=148, w=cwid, h=62, fill=CPU, stroke=CPU_S,
                          label="**pool core**", font=10.5))
BOXES.append(panel("poolstat", 44, 218, 680, 96,
                   "**Full stack, pool as a whole**\n"
                   "busy %s of the pool %s\n"
                   "run-queue wait %s s per busy s %s (camera-only row: %s %s)\n"
                   "-> a one-thread worker's CPU-second takes about %s s of wall time (%s: 1 + %s; summed wait is not "
                   "latency for parallel threads)"
                   % (f(V("pool_busy_frac_full")), T("pool_busy_frac_full"), f(wpb), T("pool_wait_per_busy_full"),
                      f(V("pool_wait_per_busy_camera_only")), T("pool_wait_per_busy_camera_only"),
                      f(1 + wpb, 0), T.est("pool_wait_per_busy_full"), f(wpb)),
                   fill="#ffffff", stroke=CPU_S, font=10.5))

# reserved cores
BOXES += [
    dict(id="rA", x=762, y=148, w=130, h=150, fill=ISO, stroke=ISO_S, font=10.5, valign="top",
         label="**reserved core A**\nmiddleware router (on every message path)\n\nprobe arm planned, **not run**"),
    dict(id="rB", x=902, y=148, w=270, h=150, fill="#fff3f0", stroke="#b85450", sw=2.5, font=10.5,
         valign="top", label="**reserved core B, full stack: saturated**\nthree groups, equal CFS shares = "
                             "**caps, not demands**"),
    dict(id="iaB", x=910, y=196, w=82, h=64, fill="#ffffff", stroke=ISO_S, font=10,
         label="**interaction service**\n%s cores" % f(share)),
    dict(id="wbcB", x=996, y=196, w=82, h=64, fill="#ffffff", stroke=ISO_S, font=10,
         label="**a controller service**\n%s cores" % f(share)),
    dict(id="probeB", x=1082, y=196, w=82, h=64, fill=OBS, stroke=OBS_S, font=10, sw=2,
         label="**measurement probe** (ours)\n%s cores" % f(share)),
    text("cBcap", 910, 264, 256, 30, "%s each" % T("saturated_core_equal_share"), font=9.5, color="#555555"),
    dict(id="rC", x=1182, y=148, w=126, h=150, fill=ISO, stroke="#333333", sw=2, font=10.5, valign="top",
         label="**reserved core C**\nthe motor-control services (their own threads already queue)\n\n"
               "**never observers**"),
    dict(id="rD", x=1318, y=148, w=126, h=150, fill=ISO, stroke="#333333", sw=2, font=10.5, valign="top",
         label="**reserved core D**\nthe motor-control services' fast real-time bus loop\n\n**never observers**"),
    panel("cluster", 762, 306, 682, 30,
          "reserved cores A, C and D share the motor-control services' CPU cluster (shared cluster L3; page 04). "
          "Some late loops already on cores C-D.", fill="#ffffff", stroke="#333333", dash="4,3",
          font=10.5, align="center", valign="middle"),
]
EDGES = [dict(src="probeB", dst="pcore%d" % (npool - 1), sx=1, sy=0.3, dx=0.5, dy=0,
              pts=[(1177, 215), (1177, 139), (44 + (npool - 1) * (cwid + 8) + cwid / 2, 139)],
              color=OBS_S, sw=2.5, dash="7,4", top=True)]
BOXES.append(dict(id="movelbl", x=905, y=120, w=260, h=17, fill="none", stroke="none", font=10.5,
                  bold=True, fontcolor=OBS_S, label="probe move: reserved core B -> a pool core", rounded=False, pad=1))

# ---- comparison table
TY = 368
cx = [30, 300, 560, 790]; cw = [266, 256, 226, 120]
hdr = ["Quantity", "Probe on reserved core B\n(the service's core)", "Probe on a pool core\n(moved)", "Alone"]
for i, t in enumerate(hdr):
    BOXES.append(panel("th%d" % i, cx[i], TY, cw[i], 40, t, fill="#e6e6e6", stroke=GREY_S, bold=True,
                       align="center", valign="middle", font=11))
rows = [
    ("Interaction service, request accepted p50 %s" % T("interaction_accepted_ms"),
     "%s ms" % f(ia["probe_on_its_core"]), "%s ms" % f(ia["probe_moved"]), "%s ms" % f(ia["alone"]), False),
    ("Reserved core B", "saturated", "no longer saturated", "—", False),
    ("Interaction service's main thread, run-queue wait", "high", "much lower", "—", False),
    ("Interaction service CPU", "%s cores (a cap)" % f(share), "more than its full-stack share", "—", False),
    ("Probe receive delay p50 / p99 %s" % T("probe_receive_delay_ms"), "%s / %s ms" % (f(pr[0]), f(pr[1])),
     "p50 falls, p99 stays high", "—", False),
    ("Probe CPU %s" % T("probe_cores_wanted"), "%s cores (a cap)" % f(share),
     "wants about %s cores, still waits" % f(V("probe_cores_wanted")), "—", True),
    ("Depth camera service, rate %s" % T("probe_on_pool_camera_cost_hz"), "reference",
     "loses about %s Hz" % f(V("probe_on_pool_camera_cost_hz")), "—", True),
]
RHt = 46
for r, (q, a, b, c, cost) in enumerate(rows):
    y = TY + 44 + r * (RHt + 4)
    BOXES.append(panel("q%d" % r, cx[0], y, cw[0], RHt, "**%s**" % q, fill="#ffffff",
                       stroke=GREY_S, font=10, valign="middle"))
    BOXES.append(panel("a%d" % r, cx[1], y, cw[1], RHt, a, fill="#fff3f0", stroke="#b85450", font=11,
                       align="center", valign="middle"))
    BOXES.append(panel("b%d" % r, cx[2], y, cw[2], RHt, b, fill=(OBS if cost else "#f1f8ee"),
                       stroke=(OBS_S if cost else GPU_S), font=11, align="center", valign="middle",
                       dash=("5,3" if cost else None)))
    BOXES.append(panel("c%d" % r, cx[3], y, cw[3], RHt, c, fill="#ffffff", stroke=GREY_S, font=11,
                       align="center", valign="middle"))

obs_share = (ia["probe_on_its_core"] - ia["probe_moved"]) / float(ia["probe_on_its_core"] - ia["alone"])
BOXES += [
    dict(id="verdict", x=930, y=TY, w=520, h=126, fill=BENCH, stroke=BENCH_S, rounded=True, font=11,
         align="left", valign="top",
         label="**The interaction service's full-stack latency was an observer effect.** About 90 %% of the "
               "excess over alone came from the bench (%s: (%s − %s) ÷ (%s − %s) ≈ %s). The service waited for "
               "its core behind our probe. The instrument (the request driver) did not wait, so the full-stack "
               "value was measured correctly; it was caused by us.\nPre-registered: core no longer saturated, met; "
               "p50 near alone, met; refutation rule not met."
               % (T.est("interaction_accepted_ms"), f(ia["probe_on_its_core"]), f(ia["probe_moved"]),
                  f(ia["probe_on_its_core"]), f(ia["alone"]), f(obs_share, 2))),
    dict(id="nofree", x=930, y=TY + 136, w=520, h=124, fill="#ffffff", stroke="#333333", rounded=True, font=11,
         align="left", valign="top",
         label="**No placement is free on this layout**\n"
               "reserved core B -> starves the interaction service (left column)\n"
               "a pool core -> the camera loses frames (amber cells)\n"
               "reserved cores C-D -> would compete with the motor loop at every wake-up (reasoning, not measured)\n"
               "reserved core A -> middleware router + the motor cluster; not tested\n"
               "**Real fix: a lighter probe** (not measured)."),
    dict(id="base", x=930, y=TY + 270, w=520, h=80, fill=GPU, stroke=GPU_S, rounded=True, font=11,
         align="left", valign="middle",
         label="**New full-stack baseline, both bench fixes** (probe on a pool core + the dialogue engine's log "
               "filter, note A4): interaction service p50 %s ms %s; transcript p50 %s ms %s; the camera pays "
               "about %s Hz for the observers on the pool."
               % (f(ia["probe_moved"]), T("interaction_accepted_ms", field="probe_moved"),
                  f(V("transcript_latency_ms", "full_filtered")), T("transcript_latency_ms", field="full_filtered"),
                  f(V("probe_on_pool_camera_cost_hz")))),
]

ly = max(TY + 44 + len(rows) * (RHt + 4), TY + 270 + 80) + 14
legend = ("**Legend**  blue = pool core; grey = reserved core (thick dark border = motor-control services, never "
          "observers); amber dashed = our observers and what moving them costs; red-bordered column = probe on "
          "the service's core; green cells = what the move fixed.\nEqual shares on a saturated core are what CFS "
          "gives groups that all want more: **caps, not demands** (the interaction service used more once its "
          "core had room). Every full-stack probe latency carries the probe's own receive delay, so it is an "
          "upper bound. Core letters A-D are labels, not core numbers.")
src, hs = sources_panel("src", 680, ly, 770, T,
                        "Numbers loaded from ../constants.json by spec02.py; key in brackets. Note A1 (pool, "
                        "reserved cores, equal shares); note A5 (probe placement, new baseline, the untested "
                        "core). Two windows per arm. Background on the observer effect: "
                        "../../robot-workload-benchmarking/notes/B4 and C7.", font=9.5)
hl = int(est_lines(legend, 640, 10.5) * 13.2 + 16)
BOXES.append(panel("legend", 30, ly, 640, max(hs, hl), legend, font=10.5))
BOXES.append(src)
PAGE["h"] = ly + max(hs, hl) + 16
