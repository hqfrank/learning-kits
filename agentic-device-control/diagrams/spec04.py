# -*- coding: utf-8 -*-
# 04 — The ReAct loop inside three nested limits (notes 06, 09).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="04-react-loop-and-limits", w=W, h=0)

it = "%s %s" % (V("react_iteration_limit_illustrative"), T("react_iteration_limit_illustrative"))
st = "%s %s" % (V("graph_step_limit_illustrative"), T("graph_step_limit_illustrative"))
wd = "%s min %s" % (V("watchdog_timeout_illustrative"), T("watchdog_timeout_illustrative"))
settle = "%s s %s" % (V("settle_delay_illustrative"), T("settle_delay_illustrative"))
p = V("per_step_success_illustrative"); t_p = T("per_step_success_illustrative")
n = V("steps_without_recovery_illustrative"); t_n = T("steps_without_recovery_illustrative")
pn = p ** n  # my arithmetic
alf = "+%s pp %s" % (V("react_alfworld_gain_pp"), T("react_alfworld_gain_pp"))
web = "+%s pp %s" % (V("react_webshop_gain_pp"), T("react_webshop_gain_pp"))
ex = V("react_in_context_examples"); t_ex = T("react_in_context_examples")

BOXES = [
    title("Three nested limits bound one task: %s ReAct iterations per specialist turn, inside %s graph hops, inside a %s watchdog" % (it, st, wd), W),
    box("wd", 30, 64, 820, 580, "WATCHDOG: whole task, %s wall clock  ->  catches a slow model or network" % wd, STOP,
        fill="none", dashed=True, valign="top", bold=True, font=12, sw=2),
    box("gs", 50, 100, 780, 528, "GRAPH STEP LIMIT: %s orchestrator -> specialist hops  ->  catches ping-pong between nodes" % st, GUARD,
        fill="none", dashed=True, valign="top", bold=True, font=12, sw=2),
    box("orc", 80, 140, 220, 56, "ORCHESTRATOR\nroutes to a specialist (diagram 02)", MODEL, font=11),
    box("turn", 70, 226, 740, 386, "ONE SPECIALIST TURN: ReAct iteration limit %s  ->  catches a stuck inner loop" % it, MODEL,
        fill="none", dashed=True, valign="top", bold=True, font=12, sw=2),

    box("th", 110, 300, 210, 96, "THOUGHT\nthe model reasons about the\nlatest screenshot + history", MODEL, font=12),
    box("ac", 410, 300, 210, 96, "ACTION\na tool call, e.g. left_click;\ndevice code executes it", DEVICE, font=12),
    box("ob", 410, 444, 210, 96, "OBSERVATION\nwait the settle delay %s,\ncapture, return the screenshot\nas the tool result" % settle, DEVICE, font=11),
    box("err", 100, 544, 300, 56, "Action failed on the device? Return an ERROR RESULT as the observation; the model reads it and re-plans. An exception would end the loop instead.",
        STOP, fill="#fff7f7", font=10, align="left"),

    box("exA", 650, 262, 150, 92, "EXIT 1\nreply with NO tool call:\nsub-goal believed done\n(orchestrator still checks)", MODEL, font=10, fill="#ffffff"),
    box("exB", 650, 444, 150, 96, "EXIT 2  loop detection\nsame action repeated,\nscreen unchanged:\nstop, report \"stuck\"", GUARD, font=10),

    box("lim", 870, 64, 380, 150,
        "WHAT EACH LIMIT CATCHES\n"
        "- iteration limit %s: a stuck inner loop\n"
        "- graph step limit %s: ping-pong between nodes\n"
        "- watchdog %s: a slow model or network (a slow step can use up time without using up steps)\n"
        "Size each from the step-count distribution of SUCCESSFUL runs, plus headroom. Too low fails healthy long tasks; too high lets a stuck loop burn tokens." % (it, st, wd),
        GUARD, align="left", valign="top", font=11),
    box("rec", 870, 228, 380, 124,
        "WHY THE LOOP MATTERS: RECOVERY\n"
        "Without recovery, per-step reliability compounds: p = %s %s per step, n = %s %s steps, so the task succeeds with p^n = %s^%s ≈ %.2f [calc].\n"
        "The observe-and-retry loop breaks this product: a wrong click shows in the next observation and is undone (go_back, close a dialog, scroll)." % (p, t_p, n, t_n, p, n, pn),
        MODEL, align="left", valign="top", font=11),
    box("pub", 870, 366, 380, 108,
        "PUBLIC EVIDENCE FOR THE PATTERN\n"
        "ReAct (Yao et al. 2022): %s absolute success on ALFWorld and %s on WebShop over imitation / RL baselines, with only %s-%s %s in-context examples.\n"
        "Their benchmarks, not yours: measure on your own devices and apps." % (alf, web, ex[0], ex[1], t_ex),
        NOTE, align="left", valign="top", font=11),
    box("legend", 30, 658, 1220, 36,
        "Legend:  dashed frames = limits, each wraps everything inside it (red watchdog, amber step limit, green iteration limit)  |  green = model call  |  blue = device code  |  "
        "amber = check in code  |  red = error result  |  solid arrows = one ReAct iteration; exits leave the turn and return to the orchestrator",
        WHITE, align="left", font=11),
]

EDGES = [
    dict(src="orc", dst="turn", label="route", color="#82b366", sx=0.5, sy=1, dx=0.162, dy=0, lpos=(222, 212), lw=50),
    dict(src="th", dst="ac", label="tool call", color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="ac", dst="ob", label="executed", color="#666666", bold=True, sx=0.5, sy=1, dx=0.5, dy=0, lpos=(515, 420), lw=70),
    dict(src="ob", dst="th", label="next iteration", color="#666666", bold=True, sx=0, sy=0.5, dx=0.5, dy=1,
         points=[(215, 492)], lpos=(312, 492), lw=100),
    dict(src="th", dst="exA", label="no tool call", color="#82b366", sx=0.5, sy=0, dx=0, dy=0.13,
         points=[(215, 274), (650, 274)], lpos=(470, 274), lw=90),
    dict(src="ob", dst="exB", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="exA", dst="orc", label="summary to state; control returns", color="#82b366", dashed=True,
         sx=0.93, sy=0, dx=1, dy=0.5, points=[(790, 168)], lpos=(510, 168), lw=230),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/06-the-react-loop.md (loop, two loop exits, three nested limits, error results, loop detection, limit sizing); notes/09-evaluation.md (compounding per-step reliability). "
    "Vendor reference loop and error handling: computer-use tool documentation, 'Understand the agent loop', 'Handle errors'. ReAct: Yao et al. 2022, https://arxiv.org/abs/2210.03629, abstract."],
    30, 708, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
