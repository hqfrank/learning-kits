# -*- coding: utf-8 -*-
# 02 — The agent graph as a state machine (notes 02, 03, 05): hub-and-spoke, plain-code router, FINISH.
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="02-agent-graph", w=W, h=0)

t_orc = "%s %s" % (V("orchestrator_temperature_illustrative"), T("orchestrator_temperature_illustrative"))
t_spec = "%s %s" % (V("specialist_temperature_illustrative"), T("specialist_temperature_illustrative"))
mo = V("max_output_tokens_illustrative"); mo_t = T("max_output_tokens_illustrative")
av = V("actuator_vs_screen_illustrative"); av_t = T("actuator_vs_screen_illustrative")
steps = "%s orchestrator hops %s" % (V("graph_step_limit_illustrative"), T("graph_step_limit_illustrative"))

CODE = ("#ffffff", "#666666")

BOXES = [
    title("One planner, two doers and a plain-code router: every specialist turn returns to the orchestrator until it says FINISH", W),
    box("start", 30, 263, 90, 44, "START", NOTE, rx=22, bold=True, font=12),
    box("orc", 150, 200, 290, 170,
        "ORCHESTRATOR  (planner)\nstronger, slower model tier\ntemperature %s\nmax output %s tokens %s\n\nplans ONE step, picks the next node,\nFINISHes only on visible evidence"
        % (t_orc, num(mo["orchestrator"]), mo_t), MODEL, font=12),
    box("router", 530, 245, 170, 80, "ROUTER\nplain code, not a model:\nswitch on one field", CODE, dashed=True, font=12),
    box("vis", 780, 80, 340, 140,
        "VISION SPECIALIST\nfast tier | temperature %s | max output %s %s\ntools: the computer-use tool (screenshot, left_click,\ntype, key, scroll, zoom ...)\nacts through the screen (diagram 03),\nin its own ReAct loop (diagram 04)"
        % (t_spec, num(mo["vision"]), mo_t), MODEL, font=11),
    box("fin", 780, 262, 120, 46, "FINISH", STOP, bold=True, font=12),
    box("end", 950, 262, 80, 46, "END", NOTE, rx=22, bold=True, font=12),
    text("endnote", 1040, 256, 220, 60, "then the one result report\n(diagram 01)", font=11, valign="middle"),
    box("act", 780, 350, 340, 140,
        "ACTUATOR\nfast tier | temperature %s | max output %s %s\ntools: launch_app, open_settings, go_home, go_back,\nset_volume, get_device_state  (each allow-listed)\nOS route to open an app: %s call, about %s s,\nvs %s calls, about %s s through the screen %s"
        % (t_spec, num(mo["actuator"]), mo_t, av["os_calls"], av["os_s"], av["screen_calls"], av["screen_s"], av_t),
        MODEL, font=11),

    box("state", 30, 556, 1220, 50,
        "STATE  (one shared object rides every edge):  task text  |  routing decisions + each specialist's summary  |  latest screenshot  |  step counter.  "
        "Step limit: %s stops a graph that never says FINISH. It counts steps; the watchdog (diagram 01) counts seconds; keep both." % steps,
        DEVICE, font=11, align="left"),

    box("fw", 30, 622, 610, 128,
        "WHY A HAND-WRITTEN GRAPH, NOT A PYTHON FRAMEWORK\n"
        "The device runtime is Java/Kotlin; popular agent-graph frameworks are Python-first.\n"
        "Hand-written: native, no extra interpreter | a while loop + a switch | one-language stack traces | no dependencies | nothing for free.\n"
        "Framework: embedded Python or bindings | layers per step | framework internals in the trace | a large, fast-moving dependency tree | checkpoints, streaming, interrupts provided.\n"
        "Deciding fact: this graph is small and stable. Borrow the concepts (named nodes, explicit state, conditional edges, step limit) so a later port is mechanical.",
        NOTE, align="left", valign="top", font=11),
    box("three", 655, 622, 595, 128,
        "WHY THREE AGENTS, NOT ONE\n"
        "- Separation: the planner decides what to do; the specialists only do.\n"
        "- Different model needs: planning wants the stronger tier; seeing and tapping want the fast one.\n"
        "- Per-node settings: each node has its own temperature, output cap and tool list.\n"
        "- Smaller prompts: each specialist sees only its own tools, so fewer tokens and fewer wrong-tool errors.\n"
        "Cost: every specialist turn costs one more orchestrator call. Hub-and-spoke: specialists never talk to each other.",
        NOTE, align="left", valign="top", font=11),
    box("legend", 30, 764, 1220, 36,
        "Legend:  green = node that calls the model  |  dashed white = plain code, no model  |  red = terminal decision  |  blue = shared state  |  "
        "solid arrow = router choice  |  dashed arrow = control returns to the orchestrator after EVERY specialist turn",
        WHITE, align="left", font=11),
]

EDGES = [
    dict(src="start", dst="orc", color="#666666", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="orc", dst="router", label="routing\ndecision", color="#82b366", bold=True, sx=1, sy=0.5, dx=0, dy=0.5, lpos=(485, 265), lw=70),
    dict(src="router", dst="vis", label="vision", color="#666666", sx=0.5, sy=0, dx=0, dy=0.5, points=[(615, 150)], lpos=(700, 150), lw=60),
    dict(src="router", dst="fin", label="FINISH", color="#b85450", sx=1, sy=0.5, dx=0, dy=0.5, lpos=(740, 272), lw=60),
    dict(src="router", dst="act", label="actuator", color="#666666", sx=0.5, sy=1, dx=0, dy=0.5, points=[(615, 420)], lpos=(700, 420), lw=70),
    dict(src="fin", dst="end", color="#b85450", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="vis", dst="orc", label="summary written to state; control returns", color="#82b366", dashed=True,
         sx=0.5, sy=0, dx=0.5, dy=0, points=[(950, 62), (295, 62)], lpos=(560, 62), lw=280),
    dict(src="act", dst="orc", label="summary written to state; control returns", color="#82b366", dashed=True,
         sx=0.5, sy=1, dx=0.5, dy=1, points=[(950, 525), (295, 525)], lpos=(560, 525), lw=280),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/02-the-agent-graph.md (nodes, router, state, step limit, framework comparison, three agents); notes/03-the-orchestrator.md (tier, temperature, output cap, stop on evidence); "
    "notes/05-the-actuator.md (actuator tools, OS route). Vocabulary (StateGraph, conditional edges, START/END, recursion limit): LangGraph Graph API docs, https://docs.langchain.com/oss/python/langgraph/graph-api (public)."],
    30, 814, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
