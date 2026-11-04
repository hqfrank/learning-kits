# 01 — Diagnosis map (note A0). All numbers via V() from ../constants.json; tags via Tags().
from _common import *

W = 1480
PAGE = dict(name="01-diagnosis-map", w=W, h=1060)
T = Tags()

BOXES = [title("Each service slows for its own reason: pool CPU from alone to the full stack, GPU turns from the "
               "full stack to full stack + VLA, and two of the largest full-stack numbers were our bench and a "
               "logging bug, not the platform", W, h=60, font=20)]
BOXES.append(text("sub", 22, 70, W - 44, 18,
                  "All measured values on this page are illustrative measurements: round teaching numbers that keep "
                  "the shape of each finding (class in constants.json). Pre-registered verdicts are in bold quotes.",
                  font=10.5, color="#444444"))

X = [30, 300, 700, 1100]; CW = [255, 385, 385, 350]
HY = 96; RY = 132; RH = 90; GAP = 10
heads = ["SERVICE and symptom\nalone -> full stack (-> + VLA)", "CAUSE supported by evidence (confidence)",
         "EXPERIMENT that showed it", "CORRECTION kept visible\n(first reading -> corrected)"]
for i, hd in enumerate(heads):
    BOXES.append(panel("h%d" % i, X[i], HY, CW[i], 32, hd, fill="#e6e6e6", stroke=GREY_S, font=11,
                       bold=True, align="center", valign="middle"))

# derived values (my estimates), computed from constants
ia = V("interaction_accepted_ms")
obs_share = (ia["probe_on_its_core"] - ia["probe_moved"]) / float(ia["probe_on_its_core"] - ia["alone"])
ctx_loop = V("ms_per_history_item") * V("history_items")
cg = V("cycles_growth_range")
vla_need = V("vla_gpu_ms_per_call") / 1000.0 * V("vla_offered_hz")
vla_naive = V("vla_call_ms") / 1000.0 * V("vla_offered_hz")
vla_max = V("gpu_free_next_to_stack") / (V("vla_gpu_ms_per_call") / 1000.0)
det = V("detector_frame_ms_solo_full")

rows = [
    dict(svc="**The depth camera service**, frame rate\n%s Hz alone %s; loses %s Hz in the full stack %s"
             % (f(V("camera_hz_alone")), T("camera_hz_alone"), f(V("camera_full_stack_loss_hz")),
                T("camera_full_stack_loss_hz")),
         kind="cpu",
         cause="**[CPU]** Pool CPU load + the full stack's extra topic demand (fan-out); provisional.\n"
               "GPU sharing alone costs %s Hz with an idle pool %s.\nConfidence: medium"
               % (f(V("camera_gpu_only_loss_hz")), T("camera_gpu_only_loss_hz")),
         exp="**One load per window:** GPU minor; pool **\"undecided at dose\"**; fan-out a minor share "
             "(%s of %s Hz %s).\n**Weight arm:** cpu.weight %s -> %s %s: verdict **\"split\"**."
             % (f(V("camera_fanout_loss_hz")), f(V("camera_full_stack_loss_hz")), T("camera_fanout_loss_hz"),
                f(V("cpu_weight_default")), f(V("weight_raised")), T("cpu_weight_default", "weight_raised")),
         corr="\"The camera is GPU-bound\" -> weakened: GPU load alone cost it no frames; GPU + pool load "
              "together not tested.\n\"nice on its threads tests priority\" -> invalid test: each container is "
              "its own cgroup (note A3)."),
    dict(svc="**The object detector**, frame time\n%s -> %s ms per frame %s"
             % (f(det[0]), f(det[1]), T("detector_frame_ms_solo_full")),
         kind="split",
         cause="**[CPU]** alone -> full stack: run-queue wait is the largest added term, plus the same work "
               "running slower (medium-high).\n**[GPU]** full stack -> + VLA: GPU time-slicing between processes "
               "(medium-high in a camera-plus-detector row; expected, not tested, in the full stack).",
         exp="**Inventory:** per-frame wait / run / blocked split (page 03).\n**Counters:** same instructions, "
             "more cycles (page 04).\n**Dose series:** **\"dose explains\"**; the full stack placed on the "
             "curve is post-hoc (note B1).",
         corr="\"CPU changes full stack -> + VLA are within spread\" -> withdrawn: with voice on in both, pool "
              "wait rises.\n\"SM contention\" -> time-slicing (no MPS, no overlap; page 05).\n"
              "\"neither alone\" -> the low end of a convex curve."),
    dict(svc="**Voice chain** (the speech recognizer -> the dialogue engine), transcript p50\n%s -> %s ms %s"
             % (f(V("transcript_latency_ms", "alone")), f(V("transcript_latency_ms", "full")),
                T("transcript_latency_ms", field="alone, full")),
         kind="bench",
         cause="**[BUG]** A logging cost in the dialogue engine that grows with conversation history, on its "
               "asyncio thread: one INFO line per history item.\nConfidence: high for alone -> full stack",
         exp="**Log filter** in the full stack: context loop about %s ms (%s) -> %s ms %s; transcript p50 %s "
             "ms %s, near alone."
             % (f(ctx_loop), T.est("ms_per_history_item", "history_items"), f(V("context_build_ms_filtered")),
                T("context_build_ms_filtered"), f(V("transcript_latency_ms", "full_filtered")),
                T("transcript_latency_ms", field="full_filtered")),
         corr="Not the platform: the largest voice number was our own software's logging loop, "
              "O(history) (note A4)."),
    dict(svc="**The interaction service**, request accepted p50\n%s -> %s ms %s"
             % (f(ia["alone"]), f(ia["probe_on_its_core"]), T("interaction_accepted_ms", field="alone, probe_on_its_core")),
         kind="bench",
         cause="**[BENCH]** Mostly our measurement probe on the same reserved core: about 90 %% of the rise "
               "(%s: (%s − %s) ÷ (%s − %s) ≈ %s).\nConfidence: high"
               % (T.est("interaction_accepted_ms"), f(ia["probe_on_its_core"]), f(ia["probe_moved"]),
                  f(ia["probe_on_its_core"]), f(ia["alone"]), f(obs_share, 2)),
         exp="**Probe move** to a pool core: accepted p50 %s ms %s.\nPredicted near alone: met; refutation "
             "rule not met." % (f(ia["probe_moved"]), T("interaction_accepted_ms", field="probe_moved")),
         corr="\"The platform is loaded, so the service's latency rises\" -> about 90 % of the rise was our "
              "probe on the service's core (page 02)."),
    dict(svc="**The motor-control services**, cycles for the same work\n%s× to %s× the alone cycles %s"
             % (f(1 + cg[0]), f(1 + cg[1]), T("cycles_growth_range")),
         kind="cpu",
         cause="**[CPU]** Same work, more cycles (IPC loss), no run-queue wait. Moving their cluster-mates away "
               "removes about two thirds (f = %s %s); path not isolated.\nConfidence: medium"
               % (f(V("cluster_move_recovered")), T("cluster_move_recovered")),
         exp="**Counters:** instructions per unit growth %s %s; cycles %s to %s %s.\n**Cluster move:** "
             "**\"most (or less board traffic)\"**, f above the %s line %s."
             % (f(V("instr_growth"), 1), T("instr_growth"), pct(cg[0]), pct(cg[1]), T("cycles_growth_range"),
                f(V("cluster_move_class_line")), T("cluster_move_class_line")),
         corr="Predicted \"part\" (f below the line) -> measured above it but close to it. Read as \"about two "
              "thirds\", not a clean \"most\" (page 04)."),
    dict(svc="**The VLA**, offered %s Hz %s\ncall %s ms alone %s"
             % (f(V("vla_offered_hz")), T("vla_offered_hz"), f(V("vla_call_ms")), T("vla_call_ms")),
         kind="gpu",
         cause="**[GPU]** GPU-time-bound: it needs %s s of GPU time per s, the stack leaves %s %s (%s).\n"
               "Confidence: medium"
               % (f(vla_need, 1), f(V("gpu_free_next_to_stack")), T("gpu_free_next_to_stack"),
                  T.est("vla_gpu_ms_per_call", "vla_offered_hz")),
         exp="**Budget** (not a pre-registered test): %s ms GPU work per call %s; the free time supports at most "
             "about %s calls per s (%s)."
             % (f(V("vla_gpu_ms_per_call")), T("vla_gpu_ms_per_call"), f(vla_max, 1),
                T.est("gpu_free_next_to_stack", "vla_gpu_ms_per_call")),
         corr="\"GPU need = call time × rate\" (%s s per s, %s) -> no: a call contains CPU-side time; "
              "budget the GPU time per call (note C1)." % (f(vla_naive, 2), T.est("vla_call_ms", "vla_offered_hz"))),
]

fills = dict(cpu=(CPU, CPU_S), gpu=(GPU, GPU_S), bench=(BENCH, BENCH_S), split=("#e3f0ea", "#5f8f9e"))
for r, row in enumerate(rows):
    y = RY + r * (RH + GAP)
    BOXES.append(panel("s%d" % r, X[0], y, CW[0], RH, row["svc"], fill="#ffffff", stroke=GREY_S, font=11,
                       valign="middle"))
    fl, st = fills[row["kind"]]
    BOXES.append(dict(id="c%d" % r, x=X[1], y=y, w=CW[1], h=RH, label=row["cause"], fill=fl, stroke=st,
                      font=10.5, align="left", valign="middle", rounded=True))
    BOXES.append(panel("x%d" % r, X[2], y, CW[2], RH, row["exp"], fill="#ffffff", stroke=GREY_S, font=10.5,
                       valign="middle"))
    BOXES.append(dict(id="k%d" % r, x=X[3], y=y, w=CW[3], h=RH, label=row["corr"], fill=CORR, stroke=CORR_S,
                      font=10.5, align="left", valign="middle", dash="6,4", rounded=True))

EDGES = []
for r in range(len(rows)):
    EDGES.append(dict(src="s%d" % r, dst="c%d" % r, sx=1, sy=0.5, dx=0, dy=0.5, color="#777777"))
    EDGES.append(dict(src="c%d" % r, dst="x%d" % r, sx=1, sy=0.5, dx=0, dy=0.5, color="#777777"))

vf = V("vision_compute_form_ms")
yb = RY + len(rows) * (RH + GAP) + 6
BOXES.append(dict(id="kgen", x=30, y=yb, w=1420, h=76, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True,
                  font=10.5, align="left", valign="middle",
                  label="**Corrections not tied to one service:**  \"A low SM issue rate means free room\" -> about "
                        "half the kernel time (%s %s) already fills the SMs on some resource, by launch configuration "
                        "(**theoretical**; note B2).   \"More GPU compute would not help\" -> multi-wave kernels would "
                        "run in fewer waves on more SMs (expectation, not measured).   \"The vision encoder is several "
                        "times slower than predicted\" -> the prediction used the bandwidth form, %s ms %s, on a board "
                        "where vision is compute-bound; the compute form gives %s ms %s (note B4)."
                        % (f(V("kernel_time_sms_full_share")), T("kernel_time_sms_full_share"),
                           f(V("vision_pred_bandwidth_form_ms")), T("vision_pred_bandwidth_form_ms"),
                           rng(*vf), T("vision_compute_form_ms"))))

yl = yb + 88
legend = ("**Legend**\nCause fill + tag: blue **[CPU]** = shared CPU pool / caches; green **[GPU]** = GPU "
          "time-slicing; teal = both (one per step); amber **[BENCH]** / **[BUG]** = our bench or our software, "
          "not the platform.\nPurple dashed box = a correction: the first reading and what replaced it.\n"
          "**Bold quoted verdicts** = pre-registered classes, unchanged.\nLoad levels: alone = one service; full "
          "stack = every module on, about %s services %s; + VLA = full stack plus a VLA (vision-language-action "
          "model) at its offered rate." % (f(V("stack_services")), T("stack_services")))
src, hs = sources_panel("src", 620, yl, 830, T,
                        "Every number is loaded from ../constants.json by spec01.py; its key is in brackets. "
                        "Notes A0 (diagnosis map, corrections table), A1–A5, B1–B4, C1. Probe rates in the full "
                        "stack are lower bounds; probe latencies are upper bounds (notes A1, A5).", font=9.5)
hl = int(est_lines(legend, 575, 10.5) * 13.2 + 16)
BOXES.append(panel("legend", 30, yl, 575, max(hs, hl), legend, font=10.5))
BOXES.append(src)
PAGE["h"] = yl + max(hs, hl) + 16
