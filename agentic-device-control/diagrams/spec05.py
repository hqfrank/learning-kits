# -*- coding: utf-8 -*-
# 05 — Cost and latency (note 07): where one illustrative task's time goes, and what caching saves
# on one vision call. Both bars are drawn to scale from constants.json values.
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="05-cost-and-caching", w=W, h=0)

t_recv = V("receive_lock_latency_illustrative"); g_recv = T("receive_lock_latency_illustrative")
t_orc = V("orchestrator_call_latency_illustrative"); g_orc = T("orchestrator_call_latency_illustrative")
t_cap = V("capture_resize_latency_illustrative"); g_cap = T("capture_resize_latency_illustrative")
t_vis = V("vision_call_latency_illustrative"); g_vis = T("vision_call_latency_illustrative")
t_set = V("settle_delay_illustrative"); g_set = T("settle_delay_illustrative")
tok_o = V("orchestrator_call_tokens_illustrative"); g_tok_o = T("orchestrator_call_tokens_illustrative")
vt = V("vision_call_tokens_illustrative"); g_vt = T("vision_call_tokens_illustrative")
task_s = V("task_wall_time_illustrative"); g_task_s = T("task_wall_time_illustrative")
calls = V("task_model_calls_illustrative"); g_calls = T("task_model_calls_illustrative")
task_tok = V("task_input_tokens_illustrative"); g_task_tok = T("task_input_tokens_illustrative")
w5 = V("cache_write_5m_multiplier"); g_w5 = T("cache_write_5m_multiplier")
w1h = V("cache_write_1h_multiplier"); g_w1h = T("cache_write_1h_multiplier")
rd = V("cache_read_multiplier"); g_rd = T("cache_read_multiplier")
bp = V("cache_max_breakpoints"); g_bp = T("cache_max_breakpoints")
ttl = V("cache_ttl_default"); g_ttl = T("cache_ttl_default")
ttl_l = V("cache_ttl_long"); g_ttl_l = T("cache_ttl_long")
keep = V("cu_screenshots_kept"); g_keep = T("cu_screenshots_kept")
prune = V("cu_prune_interval"); g_prune = T("cu_prune_interval")
tier = V("price_tier_pair_input"); g_tier = T("price_tier_pair_input")
o2i = V("price_output_to_input_ratio"); g_o2i = T("price_output_to_input_ratio")
spt = V("cu_tokens_per_screenshot"); g_spt = T("cu_tokens_per_screenshot")

# the illustrative budget (note 07 table): (label, seconds, is_model_call, calls, tokens per call)
SEG = [
    ("receive, validate, lock", t_recv, False, 0, 0, g_recv),
    ("orchestrator: route to vision", t_orc, True, 1, tok_o, g_orc),
    ("capture + resize", t_cap, False, 0, 0, g_cap),
    ("vision: find icon, tap", t_vis[0], True, 1, vt["total"], g_vis),
    ("settle", t_set, False, 0, 0, g_set),
    ("capture", t_cap, False, 0, 0, g_cap),
    ("vision: confirm, tap again if needed", t_vis[1], True, 2, vt["total"], g_vis),
    ("orchestrator: FINISH", t_orc, True, 1, tok_o, g_orc),
]
tot_s = sum(s[1] for s in SEG)
model_s = sum(s[1] for s in SEG if s[2])
dev_s = tot_s - model_s
n_calls = sum(s[3] for s in SEG)
tot_tok = sum(s[3] * s[4] for s in SEG)
assert n_calls == calls

# caching arithmetic for one vision call (my arithmetic, public multipliers)
read_tok = vt["stable_prefix"] + vt["history"]
cached = read_tok * rd + vt["new_screenshot"] * w5
frac = cached / vt["total"]

BOXES = [title("Model calls take about %d s [calc] of an illustrative %d s %s task and carry all its tokens; caching cuts a repeat vision call to about %d %% [calc]"
               % (model_s, task_s, g_task_s, round(frac * 100)), W)]

# ---------- Panel A: time bar ----------
BOXES.append(text("a_h", 30, 58, 1220, 22, "A   WHERE ONE ILLUSTRATIVE TASK'S TIME GOES  (bar lengths to scale, %d px per second)" % 55, font=13, bold=True))
X0, PX, BY, BH = 60, 55, 120, 64
x = X0
for i, (lab, s, model, nc, tk, g) in enumerate(SEG):
    w = max(3, round(s * PX))
    pal = MODEL if model else DEVICE
    inside = "%s\n%g s %s" % (lab, s, g) if w > 100 else ("%g s\n%s" % (s, g) if w > 40 else "")
    BOXES.append(box("seg%d" % i, x, BY, w, BH, inside, pal, rounded=False, font=10, bold=model))
    if w <= 100:  # label above the narrow segment
        if w < 10:
            BOXES.append(text("segl%d" % i, x - 4, BY - 20, 200, 18, "%s %g s %s" % (lab, s, g), font=10, valign="bottom"))
        else:
            BOXES.append(text("segl%d" % i, x - 20, BY - 20, w + 40, 18, lab, font=10, align="center", valign="bottom"))
    if model:
        BOXES.append(text("tok%d" % i, x, BY + BH + 2, w, 30,
                          ("%d call x %s tok %s" if nc == 1 else "%d calls x %s tok %s") % (nc, num(tk), g_tok_o if tk == tok_o else g_vt),
                          font=10, align="center"))
    x += w
for sec in range(0, int(tot_s) + 1, 5):
    BOXES.append(text("tick%d" % sec, X0 + sec * PX - 20, BY + BH + 30, 40, 16, "%d s" % sec, font=10, align="center", fontcolor="#666666"))
    BOXES.append(box("tickm%d" % sec, X0 + sec * PX, BY + BH + 26, 1, 5, "", NOTE, rounded=False))
BOXES.append(box("a_sum", 60, 232, 1190, 44,
    "Model calls: %d %s calls, %s s = %g s [calc]   |   device side: %s s = %g s [calc]   |   total %g s [calc], about %d s %s\n"
    "Input tokens: %s = %s [calc], about %s %s   ->  latency work starts with FEWER CALLS (e.g. the actuator's one OS call, diagram 02), not faster ones."
    % (calls, g_calls, " + ".join("%g" % s[1] for s in SEG if s[2]), model_s,
       " + ".join("%g" % s[1] for s in SEG if not s[2]), dev_s, tot_s, task_s, g_task_s,
       " + ".join(("%d x %s" % (s[3], num(s[4])) if s[3] > 1 else num(s[4])) for s in SEG if s[2]), num(tot_tok), num(task_tok), g_task_tok),
    NOTE, align="left", font=11))

# ---------- Panel B: caching bars ----------
BOXES.append(text("b_h", 30, 292, 1220, 22, "B   ONE VISION CALL IN BASE-INPUT-TOKEN UNITS  (bar lengths to scale)   split %s" % g_vt, font=13, bold=True))
BX, U = 210, 0.13
UNC = ("#e6e6e6", "#888888"); READ = ("#d5e8d4", "#82b366"); WRITE = ("#ffe6cc", "#d79b00")
y1, y2, bh = 334, 420, 46
parts = [("stable prefix: tools + system", vt["stable_prefix"]), ("earlier history", vt["history"]),
         ("new screenshot", vt["new_screenshot"])]
BOXES.append(text("r1l", 30, y1, 175, bh, "NO CACHING\n%s units" % num(vt["total"]), font=12, bold=True, valign="middle", align="right"))
x = BX
bps = []
for i, (lab, t) in enumerate(parts):
    w = round(t * U)
    BOXES.append(box("u%d" % i, x, y1, w, bh, "%s\n%s tok" % (lab, num(t)), UNC, rounded=False, font=10))
    x += w
    if i < 2:
        bps.append(x)
for i, bx in enumerate(bps):
    BOXES.append(box("bp%d" % i, bx - 2, y1 - 8, 4, bh + 16, "", STOP, rounded=False, fill="#b85450"))
    BOXES.append(text("bpl%d" % i, bx - 50, y1 - 26, 100, 16, "breakpoint %d" % (i + 1), font=10, align="center", fontcolor="#b85450", bold=True))
BOXES.append(text("spt", x - 330, y1 + bh + 2, 330, 18, "(one screenshot costs %d-%d input tokens %s)" % (spt[0], spt[1], g_spt), font=10, align="right"))

BOXES.append(text("r2l", 30, y2, 175, bh, "CACHED\n%s units [calc]" % num(cached), font=12, bold=True, valign="middle", align="right"))
x = BX
cp = [(vt["stable_prefix"] * rd, READ), (vt["history"] * rd, READ), (vt["new_screenshot"] * w5, WRITE)]
for i, (u, pal) in enumerate(cp):
    w = round(u * U)
    BOXES.append(box("c%d" % i, x, y2, w, bh, "" if w < 120 else "new screenshot WRITTEN\n%s x %s = %s" % (num(vt["new_screenshot"]), w5, num(u)), pal, rounded=False, font=10))
    x += w
BOXES.append(text("c_read_l", BX, y2 + bh + 2, 300, 34,
    "first %s tok READ from the cache:\n%s x %s %s = %s units" % (num(read_tok), num(read_tok), rd, g_rd, num(read_tok * rd)), font=10, fontcolor="#3d6b2a"))
BOXES.append(text("c_w_l", BX + 250, y2 + bh + 2, 300, 34,
    "write multiplier %s %s (5 min lifetime)" % (w5, g_w5), font=10, fontcolor="#9a6b00"))
BOXES.append(box("c_res", x + 30, y2 - 4, 1250 - x - 30, bh + 8,
    "%s ÷ %s = %d %% of the uncached call [calc]. The first call of a task pays the %sx write on the whole prefix; caching pays back from the second call on."
    % (num(cached), num(vt["total"]), round(frac * 100), w5), MODEL, align="left", font=11, bold=False))

# ---------- Panel C: rules ----------
CY, CH = 512, 124
BOXES += [
    box("c1", 30, CY, 400, CH,
        "C1  THE CACHING RULES (public docs)\n"
        "- The prefix order is fixed: tools -> system -> messages.\n"
        "- Up to %d breakpoints %s per request: one after tools + system, the rest on the latest tool results, advanced each turn.\n"
        "- Lifetime %d min %s by default, refreshed by each use; %d h %s optional, written at %sx %s.\n"
        "- Any change at or before a breakpoint misses everything after it." % (bp, g_bp, ttl, g_ttl, ttl_l, g_ttl_l, w1h, g_w1h),
        NOTE, align="left", valign="top", font=11),
    box("c2", 440, CY, 400, CH,
        "C2  WHY PRUNING BREAKS CACHING, AND THE FIX\n"
        "Dropping the oldest screenshot edits an EARLY block, so every later block misses.\n"
        "Fix: prune in batches. Keep the last %d %s screenshots and prune every %d %s turns, so the prefix stays byte-identical between prunes.\n"
        "A %d s %s task fits easily in the %d min %s lifetime; long gaps between tasks let it expire." % (keep, g_keep, prune, g_prune, task_s, g_task_s, ttl, g_ttl),
        GUARD, align="left", valign="top", font=11),
    box("c3", 850, CY, 400, CH,
        "C3  MODEL TIERS PER ROLE\n"
        "One same-generation pair: fast tier $%s, stronger tier $%s per million input tokens %s. Output price = %dx input %s.\n"
        "Strong tier on the orchestrator only (a wrong route wastes a whole turn); fast tier on the many specialist calls.\n"
        "Outputs here are short tool calls, so input tokens dominate: caching matters more than reply length." % (tier["fast"], tier["strong"], g_tier, o2i, g_o2i),
        MODEL, align="left", valign="top", font=11),
    box("legend", 30, CY + CH + 14, 1220, 36,
        "Legend:  green bar = model-call time  |  blue bar = device-side time  |  grey = uncached input tokens  |  light green = cache read  |  amber = cache write  |  "
        "red tick = cache breakpoint.  Units in B = tokens x price multiplier, i.e. cost relative to base input price.",
        WHITE, align="left", font=11),
]
EDGES = []

src_box, bottom = footer_box(T, [
    "Mechanism: notes/07-cost-and-latency.md (illustrative budget table, caching arithmetic, tiers). Public rules and multipliers: prompt-caching documentation "
    "(prefix order, breakpoints, lifetimes, price table read 2026-11 - prices change, multipliers are the durable part); computer-use tool documentation, 'Manage screenshot history'."],
    30, CY + CH + 64, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
