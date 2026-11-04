# -*- coding: utf-8 -*-
# 01 — The message path (note 01): cloud -> four guards -> work executor -> agent graph -> one result.
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="01-message-path", w=W, h=0)

dedup = "%s %s %s" % (V("dedup_window_illustrative"), C["dedup_window_illustrative"]["unit"], T("dedup_window_illustrative"))
wd = "%s %s %s" % (V("watchdog_timeout_illustrative"), C["watchdog_timeout_illustrative"]["unit"], T("watchdog_timeout_illustrative"))
task_s = "%s %s %s" % (V("task_wall_time_illustrative"), C["task_wall_time_illustrative"]["unit"], T("task_wall_time_illustrative"))

OK = ("#d5e8d4", "#82b366"); BUSY = ("#ffe6cc", "#d79b00")

BOXES = [
    title("Four cheap guards run before any model token is spent, and every accepted task ends as exactly one result", W),
    box("cloud", 30, 110, 180, 110, "CLOUD SERVER\nsends one task message:\nmessage ID, session ID,\ntype, payload = task text", CLOUD, font=12),
    box("val", 270, 110, 150, 110, "1  VALIDATE\nwell-formed?\nknown message type?", GUARD, font=12),
    box("dup", 450, 110, 165, 110, "2  DE-DUPLICATE\nseen this message ID\nrecently?\nIDs kept " + dedup, GUARD, font=12),
    box("lock", 645, 110, 155, 110, "3  LOCK\nis another task\nrunning?\none screen = one task", GUARD, font=12),
    box("wd", 825, 66, 430, 174, "4  WATCHDOG: hard stop after " + wd, STOP, dashed=True, fill="none",
        valign="top", bold=True, font=12, sw=2),
    box("exe", 840, 116, 160, 104, "WORK EXECUTOR\nbackground job,\noutside the UI\n(e.g. WorkManager)", DEVICE, font=12),
    box("graph", 1025, 116, 215, 104, "AGENT GRAPH\norchestrator + two\nspecialists call the model\n(diagram 02)", MODEL, font=12, bold=False),

    box("err", 270, 300, 150, 70, "ERROR at once\nmalformed or\nunknown type", STOP, font=11),
    box("drop", 450, 300, 165, 70, "DROPPED\nnot a new task:\nno second run,\nno second result", NOTE, dashed=True, font=11),
    box("busy", 645, 300, 155, 70, "BUSY at once\nno queue: the cloud\ndecides on retry", BUSY, font=11),
    box("tout", 840, 300, 160, 70, "TIMEOUT\nstop, clean up,\nrelease the lock", STOP, font=11),
    box("succ", 1025, 300, 215, 70, "SUCCESS or ERROR\nFINISH reached, or a model\nerror / exception is caught", OK, font=11),

    box("result", 270, 430, 970, 56,
        "ONE RESULT MESSAGE up the channel, exactly once per accepted task:  status (SUCCESS | ERROR | BUSY | TIMEOUT)  +  execution time  +  task description",
        DEVICE, bold=True, font=12),

    box("why", 30, 520, 600, 98,
        "WHY THESE GUARDS (design choices)\n"
        "- BUSY instead of a queue: a queued task would run minutes later on a changed screen. BUSY hands the retry decision to the cloud, which knows whether the task is still wanted. Cost: the cloud must retry with back-off.\n"
        "- The timeout is a safety bound, not a performance number. Size it well above the slow tail of successful tasks, e.g. several x the " + task_s + " simple task.\n"
        "- One result per accepted task: a missing result looks like a lost message, so the cloud cannot decide whether to retry.",
        NOTE, align="left", valign="top", font=11),
    box("idem", 650, 520, 590, 98,
        "THE IDEMPOTENCY TRAP\n"
        "De-duplication makes an exact repeat of one message safe. It does NOT make the task idempotent: \"add an item to the list\" run twice adds two items.\n"
        "A retry with a NEW message ID runs the task again. So after a lost result the cloud must ask the device first, or send only tasks that are safe to repeat.",
        STOP, fill="#fff7f7", align="left", valign="top", font=11),
    box("legend", 30, 632, 1210, 40,
        "Legend:  purple = cloud side  |  amber = guard in device code  |  blue = device component  |  green = agent that calls the model  |  "
        "red = failure status or time limit (dashed frame = the limit wraps everything inside it)  |  dashed grey = dropped, no result sent.  Cloud message channel: down = task, up = result.",
        WHITE, align="left", font=11),
]

EDGES = [
    dict(src="cloud", dst="val", label="down", color="#9673a6", sx=1, sy=0.5, dx=0, dy=0.5, lpos=(240, 153), lw=40),
    dict(src="val", dst="dup", label="ok", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="dup", dst="lock", label="new", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="lock", dst="exe", label="free", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5, lpos=(812, 156), lw=40),
    dict(src="exe", dst="graph", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="val", dst="err", label="no", color="#b85450", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="dup", dst="drop", label="repeat", color="#999999", dashed=True, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="lock", dst="busy", label="held", color="#d79b00", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="wd", dst="tout", label="limit passed", color="#b85450", sx=0.221, sy=1, dx=0.5, dy=0),
    dict(src="graph", dst="succ", label="graph ends", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0, lpos=(1132, 270)),
    dict(src="err", dst="result", color="#6c8ebf", sx=0.5, sy=1, dx=0.077, dy=0),
    dict(src="busy", dst="result", color="#6c8ebf", sx=0.5, sy=1, dx=0.468, dy=0),
    dict(src="tout", dst="result", color="#6c8ebf", sx=0.5, sy=1, dx=0.670, dy=0),
    dict(src="succ", dst="result", color="#6c8ebf", sx=0.5, sy=1, dx=0.889, dy=0),
    dict(src="result", dst="cloud", label="up", color="#9673a6", bold=True, sx=0, sy=0.5, dx=0.5, dy=1,
         points=[(120, 458)], lpos=(150, 470), lw=30),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/01-the-message-path.md (five stages, four guards, the four result statuses, idempotency, design choices). "
    "Work executor example: Android WorkManager guide, https://developer.android.com/topic/libraries/architecture/workmanager (public). No measured numbers."],
    30, 686, 1210)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
