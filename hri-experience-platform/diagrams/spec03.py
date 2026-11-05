# -*- coding: utf-8 -*-
# 03 — State ownership: the kernel envelope around an opaque local story (notes B2, B1).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="03-state-ownership", w=W, h=0)

gw = V("gesture_wait_timeout_s_illustrative"); t_gw = T("gesture_wait_timeout_s_illustrative")
ck = V("cleanup_ack_timeout_ms_illustrative"); t_ck = T("cleanup_ack_timeout_ms_illustrative")

BOXES = [title("The kernel owns the envelope; each experience owns only an opaque local story that runs inside "
               "the one shared phase 'in story', and cannot write anything around it", W, h=48)]

# left: the envelope
BOXES += [
    box("env", 30, 70, 820, 440, "", KERNEL, fill="none", dashed=True, sw=2),
    text("env_t", 42, 74, 796, 20, "THE KERNEL ENVELOPE  (kernel-owned; an experience reads it through a read-only view)",
         bold=True, font=12),
    box("fields", 45, 98, 790, 74,
        "execution mode and lifecycle phase | deployment generation and session ID | provisional visitor candidate, "
        "active participant binding, reattach / departure / retirement state | capability health | visitor-audio "
        "permit (listening, per session) and speech-output lease (speaking, per turn), kept apart | action leases "
        "and per-invocation claims, open intervals, pending cancellations | timers, deadlines, pending commands | "
        "cleanup, safety, stop and recovery state | selected experience ID + revision | the opaque local state",
        KERNEL, font=10, align="left", valign="top"),
    text("ph_t", 45, 180, 790, 18, "LIFECYCLE PHASE - one closed set shared by every experience (listed in the order of note B2)",
         bold=True, font=10),
]
phases = ["not ready", "ready", "selecting", "in story", "cleanup", "safe cleanup", "stopped", "recovery"]
for i, p in enumerate(phases):
    pal = EXPER if p == "in story" else (BAD if p == "recovery" else KERNEL)
    BOXES.append(box("ph%d" % i, 45 + i * 99, 200, 90, 36, p, pal, font=11, bold=(p in ("in story", "recovery"))))

# the local story (wave example) under 'in story'
BOXES += [
    box("story", 45, 286, 790, 210, "", EXPER, fill="none", dashed=True),
    text("story_t", 57, 290, 770, 34,
         "LOCAL STORY STATE - private to the selected experience, opaque to the kernel, valid only in 'in story'. "
         "Example: the wave experience, story greet -> await_wave -> wave (B1).", bold=True, font=10.5),
    box("greet", 70, 352, 140, 54, "greet\n(chapter)", EXPER, font=11, bold=True),
    box("await", 290, 352, 200, 54, "await_wave\nstarts a %s s gesture-wait timer %s" % (gw, t_gw), EXPER, font=11),
    box("wave", 640, 352, 170, 54, "wave\n(timer cancelled)", EXPER, font=11, bold=True),
    box("gno", 290, 438, 200, 50, "gesture_not_observed\n(terminal local state)", EXPER, font=11),
    text("gno_n", 510, 434, 310, 60,
         "Its only effect: 'request completion cleanup'. A visitor-gesture input from any OTHER track is rejected at "
         "admission and never reaches this reducer (B4).", font=10),
]
EDGES = [
    dict(src="greet", dst="await", color="#82b366", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="await", dst="wave", label="gesture = wave from the\ncurrent participant track", color="#82b366", bold=True,
         sx=1, sy=0.5, dx=0, dy=0.5, lpos=(565, 340), lw=150, font=9),
    dict(src="await", dst="gno", label="timer expiry", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0, lpos=(440, 422), lw=80, font=9),
    dict(src="ph3", dst="story", color="#82b366", dashed=True, sx=0.5, sy=1, dx=(342 + 45 - 45) / 790.0, dy=0),
    dict(src="ph3", dst="ph4", label="", color="#d79b00", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="ph4", dst="ph7", label="cleanup deadline %s ms %s passes without quiescence proof" % (num(ck), t_ck), color="#b85450", bold=True,
         sx=0.5, sy=1, dx=0.5, dy=1, points=[(486, 262), (783, 262)], lpos=(634, 268), lw=330, font=9),
]

# below the envelope: recovery
BOXES += [
    box("recov", 30, 525, 820, 58,
        "RECOVERY is kernel-owned: unresolved claims stay in evidence and visitor admission stays off. Only explicit "
        "operator recovery, or a clean restart that proves the old authority cannot act, leaves it. The first "
        "coordinator treated this timeout as a clean stop; the kernel design corrects that (B2).",
        BAD, font=10.5, align="left"),
]

# right column: authority vs policy, validators, local-state contract, two profiles
X, RW = 870, 380
BOXES += [
    box("auth", X, 70, RW, 150,
        "PARTICIPANT AUTHORITY - kernel\nselects the candidate, ties a handshake to a track, authorises lock, retarget, "
        "reattach and departure, retires the participant, and passes the reducer a typed decision: provisional | "
        "locked | retargeted | reattached | departed.\nCurrent participant track = active binding's track, else the "
        "candidate's; none before selection or after retirement. Invariant, independent of any story state: never a "
        "candidate AND an active participant.", KERNEL, font=10, align="left", valign="top"),
    box("pol", X, 228, RW, 72,
        "PARTICIPANT POLICY - experience\nonly its story response plus typed options the kernel exposes, e.g. 'lock "
        "the participant when the handshake times out: yes / no'. A new lock rule or grace is a kernel change and a "
        "safety review.", EXPER, font=10, align="left", valign="top"),
    box("vals", X, 308, RW, 62,
        "AFTER EVERY REDUCTION, in order: 1 kernel invariants on the tentative envelope (cannot be waived) -> "
        "2 story validator (reads the envelope view, cannot change it). A failure commits nothing.",
        NOTE, font=10, align="left", valign="top"),
    box("contract", X, 378, RW, 98,
        "LOCAL STATE CONTRACT: schema version | required state_name | deep immutability (scalars, enums, tuples, "
        "frozen records; no lists, maps, sets, callables) | one kernel-owned canonical encoding | equality = equal "
        "encodings. The simulation, browser and gateway may branch only on the kernel phase and on projector "
        "values, never on a local state name.", EXPER, font=10, align="left", valign="top"),
    box("prof", X, 484, RW, 98,
        "TWO LEVELS OF PROFILE: the experience PROFILE (content-addressed) pins target, images, config and ABI "
        "digests, accepted inputs and primitives, catalog policy, readiness, cleanup, evidence and acceptance, and "
        "exactly one definition. The DEFINITION selects only story logic, so a story never picks its own privileges.",
        WORLD, font=10, align="left", valign="top"),
    box("legend", 30, 596, 1220, 40,
        "Legend:  amber = kernel-owned  |  green = experience-owned  |  red = recovery  |  blue = deployment profile  |  "
        "dashed amber frame = the envelope, dashed green frame = the opaque story inside 'in story'. Only the "
        "transitions the notes state are drawn between phases; the others are not.", WHITE, font=10.5, align="left"),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B2-state-ownership.md (envelope fields, lifecycle phases, two validators, participant "
    "authority vs policy, current participant track, local state contract, cleanup failure to recovery, two "
    "profile levels); B1-experiences-as-reducers.md (the wave example); B4 (admission of participant-bound "
    "inputs). Public: Harel, 'Statecharts', Science of Computer Programming 8(3), 1987 (a story nested inside one "
    "lifecycle state)."],
    30, 650, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
