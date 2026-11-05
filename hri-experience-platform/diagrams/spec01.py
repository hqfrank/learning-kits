# -*- coding: utf-8 -*-
# 01 — The two roles and the one boundary (notes A0, A1, B6; effect list from B3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="01-roles-and-the-boundary", w=W, h=0)

turns = V("chat_turns_illustrative"); t_turns = T("chat_turns_illustrative")
tb = V("chat_turn_budget_s_illustrative"); t_tb = T("chat_turn_budget_s_illustrative")
sb = V("chat_session_bound_s_illustrative"); t_sb = T("chat_session_bound_s_illustrative")
old = V("old_effect_kinds_illustrative"); t_old = T("old_effect_kinds_illustrative")
turn_total = turns * tb                     # my arithmetic
assert turn_total < sb                      # the design's relation: turn budgets fit in the session

BOXES = [title("The reasoner proposes, only the coordinator invokes: one shared kernel owns every authority, "
               "and each experience owns only its story, reached through one small effect vocabulary", W, h=48)]

# left: visitor and reasoner
BOXES += [
    box("visitor", 30, 190, 110, 90, "VISITOR\nat a public\ndemo stand", NOTE, bold=True, font=12),
    box("reasoner", 170, 80, 250, 310,
        "THE REASONER\n(a realtime speech-to-speech LLM session)\n\n"
        "OWNS everything said inside a phase: wording, tone, empathy, small detours\n\n"
        "MAY propose a physical act, as a typed intent from a closed list (its one tool)\n\n"
        "GETS a small per-phase context, e.g. 'this is the greeting; a wave is available'. "
        "It is never told it is bounded.\n\n"
        "RETURNS a turn result: typed intent + terminal speech status\n\n"
        "CHAT = bounded turns: %s turns %s x %s s %s = %d s [calc] inside a %s s session bound %s; "
        "one speech-output lease per turn" % (turns, t_turns, tb, t_tb, turn_total, sb, t_sb),
        REASON, font=11, align="left", valign="top"),
]

# middle: the coordinator frame = kernel + experience
BOXES += [
    box("coord", 500, 72, 480, 362, "", KERNEL, fill="none", dashed=True, sw=2),
    text("coord_t", 510, 76, 460, 34,
         "THE COORDINATOR = kernel + the selected experience. Deterministic code, one worker, one "
         "authoritative transition at a time. Only it invokes anything.", bold=True, font=11, align="center"),
    box("kernel", 515, 116, 450, 130,
        "COORDINATOR KERNEL  (shared by every experience)\n\n"
        "owns: event admission and ordering | correlation | participant authority (who the visitor is) | "
        "safety preemption | command authority, leases and the visitor-audio permit | timer mechanics | "
        "cleanup and the proof that every store is clean | the lifecycle | evidence",
        KERNEL, font=11, valign="top"),
    box("effects", 603, 262, 280, 56,
        "EFFECT VOCABULARY - the only way out:\ninvoke primitive | cancel primitive | start / cancel timer | "
        "request completion cleanup | report to operator", WHITE, font=10, bold=False),
    box("exper", 515, 334, 450, 86,
        "SELECTED EXPERIENCE  (one per coordinator process)\n"
        "pure reducer: (local state, read-only envelope, event) -> (next local state, ordered effects)\n"
        "owns: its local story state, transition matrix, story invariants, and its own timeout, retry "
        "and participant POLICY choices", EXPER, font=11, valign="top"),
]

# right: ports and adapters
BOXES += [
    box("pcat", 1010, 116, 240, 70, "PRIMITIVE CATALOG (out)\nevery behaviour, speech act, gaze request and session service an experience may invoke", WORLD, font=10),
    box("icat", 1010, 200, 240, 70, "INPUT CATALOG (in)\nevery input: ingress kind, payload, correlation, privacy, replay policy", WORLD, font=10),
    box("adapt", 1010, 290, 240, 62, "PER-TARGET CONTRACTS\nadapters (for primitives) and producers (for inputs), one per named target", WORLD, font=10),
    box("tgt", 1010, 374, 240, 46, "TARGETS\nsimulation | physical robot", WORLD, bold=True, font=11),
]

EDGES = [
    dict(src="visitor", dst="reasoner", label="speech", color="#666666", sx=1, sy=0.3, dx=0, dy=(217 - 80) / 310.0, lpos=(155, 205), lw=50),
    dict(src="reasoner", dst="visitor", label="speech", color="#666666", sx=0, sy=(253 - 80) / 310.0, dx=1, dy=0.7, lpos=(155, 266), lw=50),
    dict(src="reasoner", dst="kernel", label="typed intent\n(a proposal,\nnever a command)", color="#9673a6", bold=True,
         sx=1, sy=(160 - 80) / 310.0, dx=0, dy=(160 - 116) / 130.0, lpos=(462, 136), lw=84, font=9),
    dict(src="kernel", dst="reasoner", label="phase context;\n'not now'", color="#d79b00",
         sx=0, sy=(220 - 116) / 130.0, dx=1, dy=(220 - 80) / 310.0, lpos=(462, 200), lw=84, font=9),
    dict(src="kernel", dst="exper", label="admitted,\nordered event", color="#d79b00", bold=True,
         sx=30 / 450.0, sy=1, dx=30 / 450.0, dy=0, lpos=(560, 290), lw=72, font=9),
    dict(src="exper", dst="kernel", label="effects\n(validated\nbefore commit)", color="#82b366", bold=True,
         sx=420 / 450.0, sy=0, dx=420 / 450.0, dy=1, lpos=(922, 290), lw=72, font=9),
    dict(src="kernel", dst="pcat", label="dispatch\n(after commit)", color="#d79b00", bold=True,
         sx=1, sy=(150 - 116) / 130.0, dx=0, dy=(150 - 116) / 70.0, lpos=(988, 136), lw=60, font=9),
    dict(src="icat", dst="kernel", label="events", color="#6c8ebf", bold=True,
         sx=0, sy=25 / 70.0, dx=1, dy=(225 - 116) / 130.0, lpos=(988, 212), lw=50, font=9),
    dict(src="pcat", dst="adapt", color="#6c8ebf", sx=1, sy=0.5, dx=1, dy=0.5, points=[(1266, 151), (1266, 321)]),
    dict(src="adapt", dst="icat", label="", color="#6c8ebf", sx=0.3, sy=0, dx=0.3, dy=1),
    dict(src="adapt", dst="tgt", label="commands out, observations in", color="#6c8ebf", sx=0.5, sy=1, dx=0.5, dy=0, lpos=(1130, 363), lw=200, font=9),
]

# bottom: what each side may never do; the vocabulary shrink; rejected alternatives
BOXES += [
    box("never", 30, 448, 600, 72,
        "WHAT EACH SIDE MAY NEVER DO\n"
        "An experience cannot call the robot middleware, the behaviour library, the browser, a model, the clock, "
        "the file system or the network (A0).\n"
        "The reasoner has no motion tool; its tool, context and ability sets are empty and it gets no camera "
        "images; its output never selects an experience, a state, a primitive or a command (A1, B6).",
        BAD, font=11, align="left", valign="top"),
    box("shrink", 650, 448, 600, 72,
        "WHAT THE KERNEL BUYS\n"
        "A single-experience coordinator named story actions directly: an effect list of about %s kinds %s. "
        "The kernel replaces it with the handful of generic effects above plus the two catalogs. "
        "A new experience that recombines registered parts is an authoring task, with no kernel change (A0)."
        % (old, t_old), EXPER, font=11, align="left", valign="top"),
    box("alts", 30, 532, 1220, 48,
        "REJECTED ALTERNATIVES (A0):  one coordinator process per experience (safety and cleanup diverge)  |  "
        "one large reducer with configuration branches (one matrix for unrelated stories)  |  a workflow language "
        "(validation becomes an interpreter)  |  runtime plug-ins (weakens pinning and review)  |  an LLM that "
        "orchestrates at run time (model output cannot own safety, cleanup, identity or physical authority)",
        NOTE, font=11, align="left"),
    box("legend", 30, 592, 1220, 40,
        "Legend:  purple = the reasoner  |  amber = the kernel and its authority  |  green = the experience "
        "(story only)  |  blue = catalogs, per-target contracts, targets  |  red = never allowed  |  "
        "dashed frame = the coordinator. Thick arrows = the path of one proposed act.",
        WHITE, font=11, align="left"),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/A0-one-experience-versus-many.md (kernel concerns, rejected alternatives, vocabulary shrink); "
    "A1-the-reasoner-and-the-coordinator.md (ownership table, proposal path); B1 (reducer signature); "
    "B3-the-effect-vocabulary.md (effect table); B5 (catalogs, targets); B6-conversation-and-model-boundaries.md "
    "(capability and output boundaries, bounded turns). "
    "[calc]: %d s = %s turns x %s s; it fits inside the %s s session bound." % (turn_total, turns, tb, sb)],
    30, 644, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
