# -*- coding: utf-8 -*-
# 02 — One event's path: queue, admission, interception, reduction, atomic commit, dispatch (notes B4, B3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="02-one-event-path", w=W, h=0)

BOXES = [title("One event, one path: the kernel orders, admits and intercepts every input first; the reducer "
               "sees only what is left, and nothing is sent until one snapshot is committed", W, h=48)]

# row 1: sources -> queue -> admission -> interception
srcs = ["perception", "reasoner turn results", "motion-layer outcomes", "timers", "operator", "simulation"]
for i, s_ in enumerate(srcs):
    BOXES.append(box("s%d" % i, 30, 84 + i * 32, 150, 26, s_, WORLD, font=11))
BOXES += [
    text("srch", 30, 64, 150, 18, "INPUTS -> typed events", bold=True, font=9),
    box("queue", 215, 74, 300, 200,
        "1  ONE BOUNDED PRIORITY QUEUE, ONE WORKER\n\n"
        "priority order:\n1 safety  >  2 reset  >  3 operator control  >  4 correlated command outcomes  >  5 observations\n\n"
        "inside one priority, a total order from: normalised observation time -> source rank -> source "
        "sequence -> event ID (Lamport 1978: a deterministic tie-break yields one order every replay agrees on)\n\n"
        "replay uses the recorded accepted order",
        KERNEL, font=11, align="left", valign="top"),
    box("admit", 545, 74, 340, 200,
        "2  ADMISSION  (checks the event context: source, sequence, times, clock domain, epoch, "
        "uncertainty, session, generation, command)\n\nREJECTED, never reaching the reducer:\n"
        "- stale, duplicate, wrong generation, wrong session, wrong command\n"
        "- an outcome for a command that is not pending\n"
        "- age or timestamp uncertainty over its bound\n"
        "- a participant-bound input whose track is not the current participant track\n"
        "- a source not admitted for this target (B5: rejected before queue insertion)\n\n"
        "rejected, NOT deferred: queueing would let one visitor's content reach the next",
        KERNEL, font=10.5, align="left", valign="top"),
    box("icpt", 915, 74, 335, 200,
        "3  INTERCEPTION  (the kernel handles these itself)\n\n"
        "safety and reset | readiness assessment, refresh, loss | start and yield of the idle 'ready' "
        "behaviour | visitor-audio permit issue, revoke, refusal | runtime faults and queue overflow | "
        "operator abort | participant retirement needing cleanup | cleanup acknowledgements and the "
        "cleanup deadline | the startup proof that every store is clean\n\n"
        "No experience may override, delay or reject any of them. The kernel then derives the TENTATIVE "
        "envelope.", KERNEL, font=10.5, align="left", valign="top"),
]
EDGES = [dict(src="s%d" % i, dst="queue", color="#6c8ebf", sx=1, sy=0.5, dx=0,
              dy=(97 + i * 32 - 74) / 200.0) for i in range(len(srcs))]
EDGES += [dict(src="queue", dst="admit", color="#d79b00", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
          dict(src="admit", dst="icpt", color="#d79b00", bold=True, sx=1, sy=0.5, dx=0, dy=0.5)]

# row 2: atomic preparation and dispatch (B3 steps 2-7)
steps = [
    ("red", "4  REDUCER (the experience)\npure: (local state, read-only envelope, event) -> (next local state, ordered effects)", EXPER),
    ("val", "5  VALIDATE, in order:\nkernel invariants (cannot be waived) -> story invariants -> every effect", KERNEL),
    ("ids", "6  DERIVE COMMAND IDs\ndeterministically, so a re-dispatch is idempotent", KERNEL),
    ("mat", "7  MATERIALISE commands and verify the tentative snapshot", KERNEL),
    ("cmt", "8  COMMIT ONE SNAPSHOT\nenvelope + local state + pending commands + leases + timers", KERNEL),
    ("dsp", "9  DISPATCH\nin effect order, through the catalog to the per-target adapters", WORLD),
]
X0, SW, G, Y2 = 30, 190, 16, 320
for i, (id_, lab, pal) in enumerate(steps):
    BOXES.append(box(id_, X0 + i * (SW + G), Y2, SW, 84, lab, pal, font=11, bold=(id_ == "cmt"),
                     sw=(3 if id_ == "cmt" else 1.5)))
EDGES.append(dict(src="icpt", dst="red", label="delegate only what is left", color="#d79b00", bold=True,
                  sx=0.5, sy=1, dx=0.5, dy=0, points=[(1082, 297), (125, 297)], lpos=(600, 297), lw=200, font=10))
for i in range(len(steps) - 1):
    EDGES.append(dict(src=steps[i][0], dst=steps[i + 1][0], color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5))

# row 3: failure semantics under the steps
BOXES += [
    box("fail_pre", 30, 418, 808, 44,
        "Any failure in steps 4-7: NOTHING is committed and NOTHING is dispatched. A rejected event in step 2 "
        "never reaches the reducer, so no experience can act on it by mistake.", BAD, font=11, align="left"),
    box("outbox", 854, 418, 190, 96,
        "Transactional outbox: state and intent are recorded together, then sent; a fast completion can "
        "never arrive before the state that records its command.", NOTE, font=10, align="left", valign="top"),
    box("fail_post", 1060, 418, 190, 96,
        "A dispatcher failure AFTER commit takes the correlated failure path; it never erases or invents "
        "command state.", BAD, font=10, align="left", valign="top"),
    box("safety", 30, 470, 808, 44,
        "Safety sorts first and is still typed and admitted. Preemption is proven from every local state of every "
        "registered experience (C2). Software preemption is additive: the guaranteed stop is a hardware relay in "
        "the emergency-stop loop (B4).", KERNEL, font=10.5, align="left"),
    box("legend", 30, 528, 1220, 40,
        "Legend:  amber = kernel-owned steps  |  green = the one step the experience owns  |  blue = inputs and "
        "dispatch targets  |  red = what failure means  |  thick border = the commit point. One worker processes "
        "one event at a time: a public stand produces few events per second, so replayability, not throughput, "
        "is the constraint.", WHITE, font=10.5, align="left"),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B4-kernel-interception-and-arbitration.md (intercepted classes, one ordered queue, "
    "priority and tie-break, admission rejections, rejection not deferral, single worker, hardware stop); "
    "B3-the-effect-vocabulary.md (atomic preparation and dispatch steps, transactional outbox, deterministic "
    "command IDs); B5 (target-scoped producer admission); C2 (preemption from every local state). "
    "Public: Lamport, 'Time, clocks, and the ordering of events in a distributed system', Communications 21(7), "
    "1978; Richardson, 'Pattern: Transactional outbox', microservices.io. Step numbers on this page are a "
    "drawing order, not the numbering in the notes. This page carries no numeric design parameter."],
    30, 582, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
