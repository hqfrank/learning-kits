# 05 — GPU time-slicing vs MPS (notes B1, B3). Numbers via V() from ../constants.json; tags via Tags().
from _charts import *

W = 1440
PAGE = dict(name="05-gpu-time-slicing-vs-mps", w=W, h=840)
T = Tags()

PA, PA_S = "#b9dfb0", "#3f7f33"        # client A: green, solid border, letter A
PB, PB_S = "#fbd3ad", "#b8611a"        # client B: orange, dashed border, letter B
busy_no, busy_mps = V("mps_probe_busy_frac")
ts0, ts1 = V("timeslice_ms")
nsm = V("sm_count_orin")
cap = V("mps_cap_visible_sms")
lo = V("launch_overhead_us")

BOXES = [title("Without MPS two processes take turns on the whole GPU (each about half busy); under MPS one-SM "
               "kernels run side by side, but only for clients of one Linux user; a stack split over two users would "
               "stall", W, h=60,
               font=20)]
LINES, EDGES = [], []

# ---------------- left: two timelines ----------------
LX, LW = 20, 850
BOXES.append(panel("lpan", LX, 84, LW, 540, "", fill="none", stroke=GREY_S))
BOXES.append(text("h1", LX + 10, 92, LW - 20, 54,
                  "**No MPS: one CUDA context at a time (time-slicing).** NVIDIA: \"%s\" %s Two clients, each "
                  "launching one-SM test kernels. While B's context holds the GPU, A's kernels cannot run at all."
                  % (V("mps_no_concurrency_quote"), T("mps_no_concurrency_quote")), font=11))
TX0, TX1 = LX + 130, LX + LW - 20
BOXES.append(text("lgpu", LX + 10, 154, 115, 40, "**whole GPU**\n(%d SMs)" % nsm, font=10.5, align="right",
                  valign="middle"))
n, gap = 8, 16
sw_ = (TX1 - TX0 - gap * (n - 1)) / n
for i in range(n):
    x = TX0 + i * (sw_ + gap)
    a = (i % 2 == 0)
    BOXES.append(bar("s%d" % i, x, 154, sw_, 40, PA if a else PB, PA_S if a else PB_S, dash=None if a else "5,3",
                     label="A runs" if a else "B runs", font=10.5))
    if i < n - 1:
        LINES.append(vline(x + sw_ + gap / 2, 148, 198, "#333333", 2, dash="2,3", top=True))
BOXES.append(text("swl", TX0, 200, TX1 - TX0, 30,
                  "dotted ticks = context switch (state saved and restored, caches and TLBs refilled). A time slice "
                  "is about %s ms per context %s, priority dependent. Schematic, not to scale. Board: %d SMs %s."
                  % (rng(ts0, ts1), T("timeslice_ms"), nsm, T("sm_count_orin")), font=10, color="#444444"))
BOXES.append(dict(id="r1", x=TX0, y=236, w=TX1 - TX0, h=30, fill=GREY, stroke=GREY_S, rounded=True, font=11.5,
                  label="each client busy **%s** of the time %s — the turns halve it" % (f(busy_no),
                                                                                       T("mps_probe_busy_frac"))))

LINES.append(hline(LX + 10, LX + LW - 10, 282, GREY_S, 1, dash="6,4"))
BOXES.append(text("h2", LX + 10, 290, LW - 20, 36,
                  "**MPS: one shared context; clients submit straight to the GPU.** Each one-SM kernel gets its own "
                  "SM, so the two run at the same time.", font=11))
for i, (lab, fill, st, dash, txt) in enumerate([("SM 1", PA, PA_S, None, "A runs (whole window)"),
                                                ("SM 2", PB, PB_S, "5,3", "B runs (whole window)"),
                                                ("other SMs", "#f4f4f4", GREY_S, None,
                                                 "idle in this test")]):
    y = 332 + i * 36
    BOXES.append(text("ml%d" % i, LX + 10, y, 115, 30, "**%s**" % lab, font=10.5, align="right", valign="middle"))
    BOXES.append(bar("m%d" % i, TX0, y, TX1 - TX0, 30, fill, st, dash=dash, label=txt, font=10.5))
BOXES.append(dict(id="r2", x=TX0, y=444, w=TX1 - TX0, h=30, fill=GREY, stroke=GREY_S, rounded=True, font=11.5,
                  label="each client busy **%s** of the time %s — as fast as alone"
                        % (f(busy_mps), T("mps_probe_busy_frac"))))
BOXES.append(text("capl", LX + 10, 486, 115, 40, "**thread cap**\n(one client)", font=10.5, align="right",
                  valign="middle"))
cw = int((TX1 - TX0 - 4 * (nsm - 1)) / nsm) if nsm * 30 > (TX1 - TX0) else 26
for i in range(nsm):
    on = i < cap
    BOXES.append(bar("c%d" % i, TX0 + i * (cw + 4), 492, cw, 28, PA if on else "#ffffff", PA_S if on else GREY_S,
                     dash=None if on else "3,3", label="", font=9))
BOXES.append(text("capt", TX0, 522, TX1 - TX0, 32,
                  "%s (%s) set to a quarter -> %d of %d SMs visible %s (%s: %d ÷ %d = %s). An MPS feature: a share "
                  "of SMs, not of time." % (V("mps_thread_percentage_env"), T("mps_thread_percentage_env"), cap, nsm,
                                            T("mps_cap_visible_sms"), T.est("mps_cap_visible_sms", "sm_count_orin"),
                                            cap, nsm, pct(cap / float(nsm), 0, sign=False)), font=10))
BOXES.append(text("lo", LX + 10, 562, LW - 20, 56,
                  "**Launch cost:** MPS minus no MPS %s µs, against %s µs for an empty kernel launched and "
                  "synchronised each time and %s µs queued %s. NVIDIA: \"%s\" %s"
                  % (f(lo["mps_difference"]), f(lo["sync_each"]), f(lo["queued"]), T("launch_overhead_us"),
                     V("mps_launch_path_quote"), T("mps_launch_path_quote")), font=10.5))

# ---------------- right: the one-user catch ----------------
RX, RW = 885, 535
BOXES.append(panel("rpan", RX, 84, RW, 540, "", fill=BENCH, stroke=BENCH_S))
BOXES.append(text("rh", RX + 10, 92, RW - 20, 56,
                  "**The catch for the stack: Linux users.** Single-user MPS: %s %s. Suppose the stack runs its "
                  "services as two Linux users, with its GPU services split between them:"
                  % (V("mps_one_user"), T("mps_one_user")), font=11))
BOXES.append(dict(id="u1", x=RX + 20, y=160, w=190, h=100, fill="#ffffff", stroke=INK, rounded=True, font=11,
                  align="left", valign="top", label="**Linux user 1**\n• some of the GPU services"))
BOXES.append(dict(id="u2", x=RX + RW - 210, y=160, w=190, h=100, fill="#ffffff", stroke=INK, dash="5,3",
                  rounded=True, font=11, align="left", valign="top",
                  label="**Linux user 2**\n• the other GPU services"))
BOXES.append(text("stall", RX + 210, 158, RW - 420, 50, "**stall**", font=11, align="center", valign="middle",
                  color=BENCH_S))
LINES.append(dict(pts=[(RX + 214, 206), (RX + RW - 216, 206)], color=BENCH_S, sw=2.5, arrow="end", top=True))
LINES.append(dict(pts=[(RX + RW - 214, 222), (RX + 216, 222)], color=BENCH_S, sw=2.5, arrow="end", top=True))
BOXES.append(text("stall2", RX + 210, 226, RW - 420, 34, "each queued behind the other", font=9.5,
                  align="center", color=BENCH_S))
BOXES.append(text("stt", RX + 10, 270, RW - 20, 66,
                  "**Test step:** a client of a second user next to a client of the daemon's user, under MPS: both "
                  "hung until the daemon was stopped. As deployed, MPS would likely stall the services rather than "
                  "share, which is worse than time-slicing (interpretation; not tested with the services).",
                  font=10.5))
BOXES.append(dict(id="tegra", x=RX + 10, y=344, w=RW - 20, h=96, fill="#ffffff", stroke=BENCH_S, rounded=True,
                  font=10.5, align="left", valign="top",
                  label="**Tegra limits** (NVIDIA docs): not supported: %s %s. Dynamic parallelism: %s %s.\n"
                        "Supported on Tegra Linux since %s %s. A fatal GPU fault in one client reaches every client."
                        % (V("mps_tegra_unsupported"), T("mps_tegra_unsupported"), V("mps_dynamic_parallelism"),
                           T("mps_dynamic_parallelism"), V("mps_tegra_since"), T("mps_tegra_since"))))
BOXES.append(dict(id="dep", x=RX + 10, y=450, w=RW - 20, h=164, fill="#ffffff", stroke=BENCH_S, rounded=True,
                  font=10.5, align="left", valign="top",
                  label="**Is a stack process ready for MPS?** (note B3)\n**Code: yes** — the CUDA driver attaches a "
                        "process as a client when CUDA_MPS_PIPE_DIRECTORY points to a running daemon.\n"
                        "**Libraries: not verified** — the camera SDK, TensorRT, PyTorch, ONNX Runtime.\n"
                        "**Deployment: not ready** — (1) one Linux user for all GPU services, (2) the pipe directory "
                        "in every GPU container, (3) the daemon started first, (4) fault handling in service "
                        "supervision."))

# ---------------- bottom ----------------
BOXES += [
    dict(id="cav", x=20, y=636, w=640, h=80, fill="#ffffff", stroke="#333333", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Caveats.** Every result on this page is from synthetic test kernels: one block (one SM), "
               "spinning on the GPU clock, no memory traffic, board idle. The real services never ran under MPS. "
               "About half the services' kernel time already fills the SMs (%s %s, theoretical; note B2), so for "
               "them MPS mainly lets the other process start sooner. **The gain for real services is a "
               "hypothesis**; under MPS, SM contention between processes appears for the first time."
               % (f(V("kernel_time_sms_full_share")), T("kernel_time_sms_full_share"))),
    dict(id="next", x=672, y=636, w=748, h=80, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Correction kept visible (B1).** An earlier reading listed \"SM contention\" between the object "
               "detector and the VLA. None of the dose tests ran MPS, so that cannot apply: without MPS the only "
               "sharing is turns.\n**Deciding test, not run:** the depth camera service + the object detector + "
               "the VLA without MPS, with MPS, and with the VLA capped at two SM fractions; success = the "
               "detector's blocked time next to the VLA falls and no library fails."),
]
ly = 728
legend = ("**Legend**\ngreen, solid border, \"A\" = client A; orange, dashed border, \"B\" = client B\ndotted tick = "
          "context switch; grey band = the test result\nsmall squares = the board's SMs; filled = visible under "
          "the cap\namber panel = deployment / software constraint (not the hardware)\npurple dashed = a correction")
src, hs = sources_panel("src", 532, ly, 888, T,
                        "Numbers and quotes loaded from ../constants.json by spec05.py; key in brackets. Notes B1, "
                        "B3. Contexts, streams, time-slicing, MPS and MIG are taught in "
                        "../../nvidia-gpu-anatomy/notes/07-sharing-the-gpu.md.", font=9.5)
hl = int(est_lines(legend, 500, 10.5) * 13.2 + 16)
BOXES.append(panel("legend", 20, ly, 500, max(hs, hl), legend, font=10.5))
BOXES.append(src)
PAGE["h"] = ly + max(hs, hl) + 16
