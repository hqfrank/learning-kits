# -*- coding: utf-8 -*-
# 06 — The conformance ladder and its milestones (notes C2, C1, C3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="06-conformance-ladder", w=W, h=0)

BOXES = [title("Every experience climbs the same ladder, and 'done' must name its milestone: simulation done "
               "authorises no physical deployment until the cross-target milestone holds", W, h=48)]

CX, CW, G = 30, 236, 10
rungs = [
    ("1  KERNEL CONFORMANCE SUITE", KERNEL,
     "Parameterised over EVERY registered experience, so a new one is covered with no new kernel test. Proves:\n"
     "- deterministic replay\n- safety preemption from every local state\n- departure enters common cleanup\n"
     "- stale session / generation / command / timestamp rejected\n- no raw adapter or middleware access\n"
     "- effect and primitive allowlists; reserved-policy refusal\n- materialise before dispatch; cleanup ack before new admission\n"
     "- back-to-back sessions keep no authority\n- bounded timers, queues, retries, diagnostics\n"
     "- the claim matrix: never two physical actions; audio-out conflict refused; exclusive head refused under gaze; "
     "head-defers-to-gaze in BOTH orders\n- stuck cancel -> forced cleanup -> recovery\n- lease expiry is never quiescence\n"
     "- readiness fails if the reasoner profile has tools, context, abilities or camera egress (negative test)\n"
     "- a gesture from a non-participant track is rejected (negative test)"),
    ("2  EXPERIENCE SUITE", EXPER,
     "Written per experience (by the authoring agent if agent-authored, and reviewed with the code):\n"
     "- transition-matrix tests\n- policy validation tests\n- happy-path and bounded-failure replay scenarios\n"
     "- capability-degradation scenarios\n- expected command and cancellation traces\n- projection tests\n\n"
     "Scenarios read as given / when / then (BDD): given a state and an input, when the event is admitted, then "
     "these effects and this evidence."),
    ("3  PLATFORM DEFINITION OF DONE", KERNEL,
     "Milestone criteria that name NO legacy experience. All three contract kinds added through the catalog and "
     "invoked through success, cancellation and failure by a purpose-built contract-smoke experience; one new input "
     "added through the catalog; the first-registry experiences (greeting, chat, wave, contract smoke) landed through "
     "the authoring flow."),
    ("4  SIMULATION ACCEPTANCE", WORLD,
     "Per experience, on the simulation target; per experience, a clean second browser session back to back with "
     "the first."),
    ("5  PHYSICAL ACCEPTANCE", BAD,
     "Hardware-in-the-loop on the robot; sign-off by the architecture and quality reviewers. Agent authorship does "
     "not change this gate."),
]
YTOP, YB0, SH, RISE = 70, 420, 44, 46
for i, (name, pal, body) in enumerate(rungs):
    x = CX + i * (CW + G)
    yh = YB0 - i * RISE
    BOXES.append(box("r%d" % i, x, yh, CW, SH, name, pal, bold=True, font=11, sw=2))
    bh = [yh - YTOP - 6, 168, 112, 52, 52][i]
    BOXES.append(box("b%d" % i, x, yh - 6 - bh, CW, bh, body, WHITE, font=9.5, align="left", valign="top"))
EDGES = [dict(src="r%d" % i, dst="r%d" % (i + 1), color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5)
         for i in range(4)]

# milestones as bars under the ladder columns
YM = YB0 + SH + 16
col_x = lambda i: CX + i * (CW + G)
col_end = lambda i: col_x(i) + CW
BOXES += [
    box("m_sim", col_x(0), YM, col_end(3) - col_x(0), 58,
        "SIMULATION MILESTONE - on the simulation target with no cloud credentials, no network egress, no hardware: "
        "rungs 1-4, every safety, authority and cleanup invariant shown by a FAILING negative test, deterministic replay "
        "(identical inputs under the replay clock -> identical state encodings, invocation sequences, evidence digests). "
        "Showcase artifact: one command -> evidence + a shareable video.", WORLD, font=10, align="left", valign="top"),
    box("m_chat", col_x(3), YM + 66, CW, 58,
        "LIVE-CHAT GATE - the real model, on simulation. A cloud outage may block it, never invalidate the offline "
        "milestone.", REASON, font=9.5, align="left", valign="top"),
    box("m_x", col_x(0), YM + 132, col_end(4) - col_x(0), 44,
        "CROSS-TARGET MILESTONE - the same experiences pass hardware-in-the-loop with physical adapter and producer "
        "contracts AND give equivalent evidence under the cross-target comparator (C3). Until then every profile is "
        "simulation-only and physical execution stays disabled.", BAD, font=10, align="left", valign="top"),
    box("m_note", col_x(0), YM + 66, col_end(2) - col_x(0), 58,
        "A RICH LEGACY EXPERIENCE IS NOT THE DEFINITION OF DONE: an earlier draft made parity with it the exit "
        "criterion and bent the platform toward it. It became a required but non-blocking regeneration experiment (C3).",
        NOTE, font=10, align="left", valign="top"),
    box("cant", col_x(4), YM, CW, 124,
        "WHAT SIMULATION CANNOT PROVE (C1): contact force or hardware safety from simulated grasp; collision truth "
        "from browser monocular depth; perception, conversation, social-timing or manipulation quality; a live human "
        "run is never a CI test.", BAD, font=9.5, align="left", valign="top"),
]
YR = YM + 190
BOXES += [
    box("rules", 30, YR, 1220, 44,
        "EVIDENCE RULES: every invariant needs a negative test that fails when the rule is broken  |  schema-versioned "
        "evidence carries the full resource lifecycle of every invocation; comparators READ held intervals from these "
        "fields and never infer them from presentation events or terminal outcomes  |  the video illustrates, the "
        "evidence proves", KERNEL, font=10, align="left"),
    box("legend", 30, YR + 56, 1220, 40,
        "Legend:  rising steps = the ladder, climbed left to right (each rung's box above it says what it proves)  |  "
        "amber = kernel-level gates  |  green = per-experience tests  |  blue = simulation  |  purple = live model  |  "
        "red = the physical robot and what simulation cannot prove  |  bars below = milestones and the rungs they span.",
        WHITE, font=10, align="left"),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/C2-the-conformance-ladder.md (ladder, kernel conformance list, experience suite, milestones, "
    "showcase artifact, live-chat gate, cross-target milestone, platform-native done, evidence rules); "
    "C1-simulation-first.md (what simulation cannot prove); C3-regeneration-and-comparison.md (non-blocking "
    "regeneration, cross-target comparator). Public: Pact documentation, docs.pact.io (consumer-driven contract "
    "tests); North, 'Introducing BDD', 2006 (given / when / then). This page carries no numeric design parameter."],
    30, YR + 110, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
