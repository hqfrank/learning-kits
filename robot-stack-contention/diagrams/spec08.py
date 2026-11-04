# 08 — A full SM with a low issue rate (note B2). Public kit.
# Every number via V() from ../constants.json, tagged by key. Fill numbers are theoretical.
import re
from _charts import *

W, H = 1440, 800
PAGE = dict(name="08-full-sm-low-issue", w=W, h=H)
T = Tags()

iss = V("sm_issue_full_stack")
act = V("gpu_active_full_stack")
full_share = V("kernel_time_sms_full_share")
g0, g1 = V("gemm_warp_slot_fill")
m0, m1 = V("multiwave_share")
nsm = V("sm_count_orin")
warps = V("max_warps_per_sm")
blocks = V("max_blocks_per_sm_cc87")
regs = V("registers_per_sm")
smem = V("l1_shared_per_sm_orin_kb")
wsz = V("warp_size")
ralloc = V("register_alloc_unit_per_warp")
rmax = V("max_registers_per_thread")
# the "full" threshold (>= N % on some resource) is read from the source text of kernel_time_sms_full_share
thr_pct = int(re.search(r">=\s*(\d+)\s*%", qnote("kernel_time_sms_full_share")).group(1))
thr = thr_pct / 100.0
# worked register limit (my arithmetic): regs / warps, rounded down to the allocation unit, / warp size
per_warp = regs / float(warps)
per_warp_alloc = int(per_warp // ralloc) * ralloc
per_thread = per_warp_alloc // wsz
FULL, FULL_S = "#b9dfb0", "#3f7f33"

BOXES = [title("A low SM issue rate is not free room: about half the kernel time already fills an SM on some "
               "resource, and multi-wave kernels would be expected to gain from more SMs (illustrative, theoretical)",
               W, h=60, font=20)]
LINES, EDGES = [], []

# ---------------- left: one SM, schematic ----------------
BOXES.append(panel("smp", 20, 84, 500, 436, "", fill="none", stroke=GREY_S))
BOXES.append(text("smh", 30, 90, 480, 36, "**Two different questions about the GPU and one SM** (schematic gauges; "
                  "per-SM limits of an Orin-class board)", font=12))
GX, GW = 190, 300


def gauge(id, y, name, frac_solid, frac_dash=None, label="", fill=FULL, stroke=FULL_S, dash_fill=None,
          solid_dash=None):
    BOXES.append(text(id + "n", 30, y - 4, GX - 38, 36, name, font=10, align="right", valign="middle"))
    BOXES.append(bar(id + "bg", GX, y, GW, 28, "#ffffff", GREY_S))
    if frac_dash:
        BOXES.append(bar(id + "d", GX, y, GW * frac_dash, 28, dash_fill or "#e9f4e6", stroke, dash="4,3"))
    if frac_solid:
        BOXES.append(bar(id + "s", GX, y, GW * frac_solid, 28, fill, stroke, dash=solid_dash))
    if label:
        BOXES.append(text(id + "l", GX, y + 30, GW + 20, 28, label, font=9.5))


BOXES.append(text("q1", 30, 132, 480, 18, "**Q1. How often do the SMs issue an instruction?** (full stack)", font=11))
gauge("iss", 156, "SM issue rate", iss, act, fill=CPU2, stroke=CPU_S, dash_fill=CPU,
      label="solid: %s of peak %s; dashed: GPU has work %s of the time %s"
            % (f(iss), T("sm_issue_full_stack"), f(act), T("gpu_active_full_stack")))
BOXES.append(text("q2", 30, 222, 480, 18, "**Q2. While a big GEMM kernel runs, how full is its SM?**", font=11))
gauge("wp", 246, "warps\n(%d per SM %s)" % (warps, T("max_warps_per_sm")), g0, g1,
      label="warp-slot fill %s %s: looks mostly empty" % (rng(g0, g1), T("gemm_warp_slot_fill")))
gauge("bk", 306, "blocks\n(%d per SM %s)" % (blocks, T("max_blocks_per_sm_cc87")), 0, None,
      label="not given per kernel in this kit")
gauge("rg", 366, "registers\n(%s per SM %s)" % ("{:,}".format(regs).replace(",", " "), T("registers_per_sm")),
      thr, None, label="register-bound: at or past the \"full\" line (schematic)")
gauge("sm", 426, "shared memory\n(max %d KB per SM %s)" % (smem, T("l1_shared_per_sm_orin_kb")), thr, None,
      solid_dash="2,2", label="or shared-memory-bound instead (schematic, dotted)")
for yy in (246, 366, 426):
    LINES.append(vline(GX + GW * thr, yy - 4, yy + 32, INK, 1.5, dash="4,3", top=True))
BOXES.append(text("thl", GX + GW * thr - 210, 484, 230, 30, "dashed vertical: \"full\" = binding fill >= %d %% "
                  "%s" % (thr_pct, T("kernel_time_sms_full_share")), font=9.5, align="right"))
BOXES.append(text("ana", 30, 482, 150, 34, "Analogy: a car park full of a few wide vans.", font=9.5,
                  color="#555555"))

# ---------------- right top: kernel-time shares ----------------
TX, TW = 535, 885
BOXES.append(panel("tp", TX, 84, TW, 178, "", fill="none", stroke=GREY_S))
BOXES.append(text("th", TX + 10, 90, TW - 20, 20, "**Fractions from solo traces** (from launch configurations: theoretical; illustrative)", font=12))
BX, BW = TX + 290, 480
rows = [("SMs >= %d %% full on some resource" % thr_pct, (0, full_share), FULL, FULL_S, None,
         "about %s %s" % (f(full_share), T("kernel_time_sms_full_share"))),
        ("warp-slot fill of the large GEMM kernels (fraction of slots, not of time)", (g0, g1), "#ffffff", FULL_S, "4,3",
         "%s %s" % (rng(g0, g1), T("gemm_warp_slot_fill"))),
        ("kernel time in > 1 wave, per service", (m0, m1), CPU2, CPU_S, None,
         "%s %s" % (rng(m0, m1), T("multiwave_share")))]
for t in (0, 0.5, 1):
    LINES.append(vline(BX + BW * t, 118, 236, "#dddddd", 1))
    BOXES.append(text("tk%s" % t, BX + BW * t - 15, 238, 30, 14, f(t), font=9, align="center"))
for i, (nm, (a, bb), fill, st, dash, lab) in enumerate(rows):
    y = 122 + i * 38
    BOXES.append(text("rn%d" % i, TX + 8, y, 276, 26, "**%s**" % nm, font=10, align="right", valign="middle"))
    if a > 0:  # a range: draw the bar from 0 to the low end faint, and the range solid
        BOXES.append(bar("rl%d" % i, BX, y + 2, BW * a, 22, "#f6f6f6", GREY_S, dash="2,2", sw=1))
    BOXES.append(bar("rv%d" % i, BX + BW * a, y + 2, BW * (bb - a), 22, fill, st, dash=dash))
    BOXES.append(text("rt%d" % i, BX + BW * bb + 6, y + 5, 200, 16, lab, font=9.5))

# ---------------- right middle: the register worked example ----------------
BOXES.append(dict(id="reg", x=TX, y=272, w=TW, h=86, fill=NOTE, stroke=NOTE_S, rounded=True, font=10.5,
                  align="left", valign="top",
                  label="**Why a GEMM fills an SM with few warps (worked register limit).** To fill all %d warp "
                        "slots a kernel may use at most about %d registers per thread: %s ÷ %d = %s per warp, rounded "
                        "down to a multiple of %d = %d, ÷ %d threads = %d (%s). A GEMM kernel often uses far more, up "
                        "to %d per thread %s, so its SM is full by registers with only a few warps resident."
                        % (warps, per_thread, "{:,}".format(regs).replace(",", " "), warps, f(round(per_warp, 1)),
                           ralloc, per_warp_alloc, wsz, per_thread,
                           T.est("registers_per_sm", "max_warps_per_sm", "warp_size",
                                 "register_alloc_unit_per_warp"), rmax, T("max_registers_per_thread"))))

# ---------------- right lower: waves strip ----------------
WY = 368
BOXES.append(panel("wp2", TX, WY, TW, 152, "", fill="none", stroke=GREY_S))
BOXES.append(text("wh", TX + 10, WY + 4, TW - 20, 34,
                  "**Waves** (schematic): waves = ⌈blocks ÷ (SMs × blocks per SM)⌉. Below, one block per SM for "
                  "clarity: a kernel with blocks for two full rounds and a partial third on the %d SMs %s."
                  % (nsm, T("sm_count_orin")), font=10.5))
sq = 14
for wv, frac in enumerate([1, 1, 0.5]):
    for i in range(nsm):
        on = i < nsm * frac
        BOXES.append(bar("w%d_%d" % (wv, i), TX + 20 + i * (sq + 2), WY + 48 + wv * (sq + 6), sq, sq,
                         CPU2 if on else "#ffffff", CPU_S if on else GREY_S, dash=None if on else "2,2", sw=1))
    BOXES.append(text("wl%d" % wv, TX + 20 + nsm * (sq + 2) + 4, WY + 46 + wv * (sq + 6), 120, 16,
                      "wave %d%s" % (wv + 1, " (partial)" if frac < 1 else ""), font=9.5))
BOXES.append(text("wt", TX + 400, WY + 44, TW - 410, 104,
                  "More SMs -> fewer waves: roughly in proportion for kernels with many waves; in steps, possibly "
                  "none, for kernels with only a few waves, because the last wave rounds up; no gain where a kernel is "
                  "limited by DRAM bandwidth, L2 or memory latency (not measured per kernel). **An expectation, not a "
                  "measurement.**", font=10))

# ---------------- bottom ----------------
BOXES += [
    dict(id="corr", x=20, y=532, w=500, h=84, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Two corrections kept visible**\n• \"A low issue rate means room for MPS\": wrong. A register-bound "
               "GEMM fills its SMs with few warps, so issue is low while no other block fits.\n• \"More SMs mostly "
               "add idle SMs\": wrong for multi-wave kernels."),
    dict(id="mps", x=532, y=532, w=440, h=84, fill="#ffffff", stroke=INK, rounded=True, font=10.5, align="left",
         valign="top",
         label="**What it means for MPS (hypothesis, page 05).** In the rest of the kernel time (small grids, partial "
               "last waves, kernels below %d %% on every resource) kernels of two processes could overlap. During "
               "full kernels MPS mainly lets the other process's blocks start as SM resources free up, instead of "
               "after a whole time slice and a context switch." % thr_pct),
    dict(id="cav", x=984, y=532, w=436, h=84, fill="#ffffff", stroke="#333333", rounded=True, font=10,
         align="left", valign="top",
         label="**Caveats.** Fill numbers are **theoretical**, from launch configurations in solo traces; achieved "
               "occupancy, stall reasons and co-residency under MPS were not measured, nor why issue is low. Traces "
               "had limits (a different VLA model version; a replay-fed detector; an empty people-perception scene). "
               "The gauges on the left are a schematic."),
]
leg = ("**Legend**\ngreen solid bar = share with SMs full; white bar, dashed green = warp-slot fill\n"
       "blue bar = share in > 1 wave; blue squares = SMs busy in a wave\nfaint dotted bar = below the low end of a range\n"
       "gauges: solid = value or range low end; dashed = range high end or GPU-active share\n"
       "dashed vertical line = the \"full\" definition; purple dashed = a correction")
BOXES.append(panel("legend", 20, 628, 500, 92, leg, font=10))
src, sh = sources_panel("src", 532, 628, 888, T,
                        "Note B2. Occupancy and issue rate: ../../nvidia-gpu-anatomy/ (note 03); board limits: "
                        "../../jetson-orin-thor-metrics/. The \"full\" threshold is read from the source text of "
                        "kernel_time_sms_full_share.", font=9.5)
sh = int(sh * 0.8)  # the helper's line estimate runs high for this renderer
src["h"] = sh
BOXES.append(src)
PAGE["h"] = max(628 + 92, 628 + sh) + 12
