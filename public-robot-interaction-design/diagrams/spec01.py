# -*- coding: utf-8 -*-
# 01 — The visit as a state machine: one offer hub, invariants, recovery to a bounded end (note A1).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="01-visit-state-machine", w=W, h=0)

n_off = V("offerings_illustrative"); t_off = T("offerings_illustrative")
assert n_off == 3, "the drawing shows three offerings"

BOXES = [title("A visit is a small state machine: every offering hangs off one hub and is offered at most once, "
               "so every visit provably ends; the language model only supplies the words inside each state "
               "(%s illustrative offerings %s)" % (n_off, t_off), W, h=46)]

Y = 70
# --- the machine (left) ------------------------------------------------------------
BOXES += [
    box("chat", 380, Y + 20, 125, 58, "CHAT\noffering 1", BODY, bold=True, font=11),
    box("gift", 520, Y + 20, 125, 58, "A SMALL GIFT\noffering 2 (self-serve)", BODY, bold=True, font=11),
    box("photo", 660, Y + 20, 125, 58, "A PHOTO\noffering 3 (visitor's phone)", BODY, bold=True, font=11),
    box("waiting", 30, Y + 185, 135, 64, "WAITING\n(attract posture)", VISIT, bold=True, font=11),
    box("arrival", 205, Y + 170, 190, 94,
        "ARRIVAL\ngeneric hello, never the last word: always followed by one specific thing",
        VISIT, font=11, bold=False),
    box("hub", 450, Y + 170, 200, 94,
        "OFFER HUB\nthe robot raises ONE offering, or the visitor asks for one; all offerings are equals",
        VISIT, font=11),
    box("celebrate", 700, Y + 185, 160, 70,
        "CELEBRATE\na reaction, brief; only with something safe now, else skip silently",
        GATE, font=10.5),
    box("noans", 450, Y + 320, 200, 70,
        "NO ANSWER\nname one SPECIFIC thing (never an open 'what would you like?')",
        GATE, font=10.5),
    box("talk", 690, Y + 320, 170, 70,
        "JUST TALKING\nrepeated decline or 'I'm fine': offering stops, the robot stays warm",
        VISIT, font=10.5),
    box("closing", 450, Y + 450, 200, 58, "CLOSING\ngoodbye; every offering mentioned at least once", VISIT, font=10.5),
    box("reset", 205, Y + 440, 190, 78,
        "RESET (close the visit)\nconfirmed stop of speech and motion, then delete ALL per-visit state",
        VISIT, font=10.5, bold=False),
    box("staff", 30, Y + 445, 135, 68, "NEEDS STAFF\nreset could not be confirmed: no new visit on top", BAD, font=10.5),
]
BOXES.append(text("arr_note", 205, Y + 270, 190, 60,
                  "Steps out of view and returns within a short window = the SAME visit: no fresh hello, no repeated offers.",
                  font=10, fontcolor="#444444"))
BOXES.append(text("hub_note", 380, Y + 2, 420, 18,
                  "each offering returns to the hub; offerings never connect to each other",
                  font=10, fontcolor="#444444", align="center"))

EDGES = [
    dict(src="waiting", dst="arrival", sx=1, sy=0.5, dx=0, dy=0.5, label="someone arrives", color=BLUE_C,
         lpos=(185, Y + 160), lw=60),
    dict(src="arrival", dst="hub", sx=1, sy=0.5, dx=0, dy=0.5, color=BLUE_C),
    # hub <-> offerings
    dict(src="hub", dst="chat", sx=0.12, sy=0, dx=0.45, dy=1, color=GREEN_C),
    dict(src="chat", dst="hub", sx=0.85, sy=1, dx=0.3, dy=0, color=GREEN_C, dashed=True),
    dict(src="hub", dst="gift", sx=0.45, sy=0, dx=0.3, dy=1, color=GREEN_C),
    dict(src="gift", dst="hub", sx=0.7, sy=1, dx=0.62, dy=0, color=GREEN_C, dashed=True),
    dict(src="hub", dst="photo", sx=0.82, sy=0, dx=0.2, dy=1, color=GREEN_C),
    dict(src="photo", dst="hub", sx=0.55, sy=1, dx=0.95, dy=0, color=GREEN_C, dashed=True),
    # hub -> celebrate and back
    dict(src="hub", dst="celebrate", sx=1, sy=0.35, dx=0, dy=0.3, color=AMBER_C, label="it landed", lw=60,
         lpos=(675, Y + 182)),
    dict(src="celebrate", dst="hub", sx=0, dy=0.75, dx=1, sy=0.8, color=AMBER_C, dashed=True),
    # silence / decline
    dict(src="hub", dst="noans", sx=0.35, sy=1, dx=0.35, dy=0, color=AMBER_C, label="silence", lw=50,
         lpos=(495, Y + 292)),
    dict(src="noans", dst="hub", sx=0.7, sy=0, dx=0.7, dy=1, color=AMBER_C, dashed=True, label="answers", lw=55,
         lpos=(610, Y + 292)),
    dict(src="hub", dst="talk", sx=1, sy=0.92, dx=0.3, dy=0, color=BLUE_C, label="repeated decline", lw=90,
         lpos=(720, Y + 290)),
    dict(src="noans", dst="closing", sx=0.5, sy=1, dx=0.5, dy=0, color=AMBER_C, label="still nothing: close gently",
         lw=140, lpos=(550, Y + 420)),
    dict(src="talk", dst="closing", sx=0.5, sy=1, dx=1, dy=0.5, color=BLUE_C, points=[(775, Y + 479)],
         label="visitor done", lw=70, lpos=(775, Y + 420)),
    dict(src="closing", dst="reset", sx=0, sy=0.5, dx=1, dy=0.5, color=BLUE_C),
    dict(src="reset", dst="waiting", sx=0.12, sy=0, dx=0.6, dy=1, color=BLUE_C, label="confirmed", lw=60,
         lpos=(150, Y + 340)),
    dict(src="reset", dst="staff", sx=0, sy=0.5, dx=1, dy=0.5, color=RED_C, dashed=True),
]

# global transitions, drawn once
yg = Y + 540
BOXES.append(box("g_walk", 30, yg, 405, 44,
                 "GLOBAL: the visitor walks away -> CLOSING, from any state. A silence is not a departure; a departure is never answered as a silence.",
                 NOTE, font=10.5, align="left"))
BOXES.append(box("g_safe", 450, yg, 410, 44,
                 "GLOBAL: SAFETY PAUSE pre-empts every state and stays stopped until staff clear it; the hardware power cut is never a software call.",
                 BAD, font=10.5, align="left"))

# --- invariants (right) -------------------------------------------------------------
inv = [
    "1  The robot offers first: the visit never depends on the visitor knowing what to ask.",
    "2  Silence never strands the visit: name one specific thing.",
    "3  One thing at a time: one offering per turn, never a list (unless asked 'what can you do?').",
    "4  A no is a no: a declined offering is not raised again; a repeated decline stops all offering.",
    "5  Nothing stays a secret: every offering is MENTIONED once before goodbye (unless the visitor left, declined or asked to stop).",
    "6  Offering always runs out: each offering is OFFERED at most once, so the visit terminates.",
    "7  Celebration is a reaction, never a request, and never reopens what 4 or 6 closed.",
    "8  The robot never claims to remember anyone: after the reset a returning person is a stranger.",
]
BOXES.append(box("inv_h", 885, Y, 365, 28, "THE RULES THAT MUST ALWAYS HOLD (invariants)", BAD, bold=True, font=11.5))
BOXES.append(box("inv", 885, Y + 28, 365, 222, "\n".join(inv), WHITE, font=10.5, align="left", valign="top",
                 rounded=False))
BOXES.append(box("mention", 885, Y + 264, 365, 92,
                 "MENTION vs OFFER: two flags, never one.\nA mention says a thing exists and expects no answer; an offer names it and waits for yes or no. "
                 "Rule 5 is discharged by a mention; rule 6 caps offers. Merge the flags and one of the two rules breaks.",
                 GATE, font=10.5, align="left", valign="top"))
BOXES.append(box("track", 885, Y + 370, 365, 100,
                 "THE HUB TRACKS, per visit (all deleted by the reset): offerings available now, mentioned, offered, declined; "
                 "consecutive unanswered offers; whether offering is still permitted; whether a celebration is possible; "
                 "the offering completed last (never offered next). A celebration changes none of these.",
                 NOTE, font=10.5, align="left", valign="top"))

ylg = Y + 600
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: blue = visit states | green = offerings (solid arrow = raised or asked, dashed = back to the hub) | "
                 "amber = no-answer and celebration paths | red = safety and staff states. Transition hygiene: stop BEFORE start; the stop is confirmed, not assumed.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/A1-the-experience-as-a-state-machine.md (overview states, arrival, offer hub, following the lead, "
    "celebrating and closing, the eight invariants, state the hub must track, transition hygiene); B1 (safety supervisor above the state machine). "
    "Termination argument: a finite offering set with at most one offer each ends every visit (A1, 'How it is designed and tested')."],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
