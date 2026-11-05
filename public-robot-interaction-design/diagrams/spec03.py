# -*- coding: utf-8 -*-
# 03 — The voice pipeline as built: one LLM box among plain-code components; the degradation ladder (note B1).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="03-where-the-llm-is", w=W, h=0)

tick = V("behaviour_tick_illustrative"); t_tick = T("behaviour_tick_illustrative")
wd = V("wind_down_quiet_illustrative"); t_wd = T("wind_down_quiet_illustrative")

BOXES = [title("Only ONE box in the stack is a language model: perception, the engage trigger, the body and the gaze are plain code "
               "that unit tests can prove; the model's behaviour can only be measured live", W, h=46)]

BOXES += [
    box("mic", 30, 104, 160, 58, "MICROPHONE ARRAY\naudio in", NOTE, bold=True, font=11),
    box("cam", 30, 262, 160, 58, "HEAD CAMERA\nframes stay inside the stand", NOTE, bold=True, font=10.5),
    box("percep", 240, 222, 250, 126,
        "VISITOR PERCEPTION - not an LLM\nsmall vision and audio models: face detector, face embedding (anonymous session id), "
        "active-speaker detection, voice embedding; direction-of-arrival fusion; state machine absent -> arming -> engaged",
        VISIT, font=10.5),
    box("trigger", 240, 404, 250, 92,
        "ENGAGE TRIGGER - not an LLM\none deterministic edge: 'engaged' -> one system message to greet. "
        "Cooldown, re-arm on idle, wake-word precedence, fail closed if perception is stale",
        VISIT, font=10.5),
    box("reasoner", 560, 78, 320, 206,
        "THE REASONER - the only LLM\na realtime speech-to-speech session: audio in and out, server-side VAD, function calling; "
        "the only 'vision' is a camera frame per utterance.\n\nWrapped by: a local wake-word gate; TRIAGE (a per-utterance "
        "LLM decision: accept or ignore); a barge-in guard; context compaction; tracing.\n"
        "Behaviour lives in prompt files: base identity and safety <- stand profile <- one file per ability",
        LLM, font=10.5, sw=3),
    box("spk", 640, 336, 160, 46, "LOUDSPEAKER\nrobot voice out", NOTE, bold=True, font=10.5),
    box("behav", 950, 78, 300, 100,
        "BEHAVIOUR LIBRARY - not an LLM\na behaviour tree at %s Hz %s with blended priority layers; face lights, eyebrows and a nod "
        "follow the voice output level" % (tick, t_tick),
        BODY, font=10.5),
    box("gaze", 950, 230, 300, 86,
        "GAZE CONTROLLER - not an LLM\nactive-speaker bearing -> gaze policy -> head-pose command (diagram 05)",
        BODY, font=10.5),
    box("gw", 950, 376, 300, 92,
        "ROBOT GATEWAY - not an LLM\nthe only component that talks to the robot middleware; a few intent verbs: speak, play pose, "
        "look at, hand over, cancel, health",
        GREY, font=10.5),
]
EDGES = [
    dict(src="mic", dst="reasoner", sx=1, sy=0.5, dx=0, dy=0.16, color=PURPLE_C, label="audio, through a local wake-word gate",
         lw=250, lpos=(375, 116)),
    dict(src="mic", dst="percep", sx=0.5, sy=1, dx=0.2, dy=0, color=BLUE_C, dashed=True, points=[(110, 200), (290, 200)],
         label="audio for DoA and voice", lw=130, lpos=(200, 188)),
    dict(src="cam", dst="percep", sx=1, sy=0.5, dx=0, dy=0.65, color=BLUE_C),
    dict(src="percep", dst="trigger", sx=0.5, sy=1, dx=0.5, dy=0, color=BLUE_C, label="engaged", lw=55, lpos=(400, 376)),
    dict(src="trigger", dst="reasoner", sx=1, sy=0.5, dx=0.1, dy=1, color=BLUE_C, points=[(592, 450)],
         label="one system message: greet", lw=140, lpos=(668, 420)),
    dict(src="percep", dst="reasoner", sx=1, sy=0.18, dx=0, dy=0.8, color=BLUE_C,
         label="speaker labels, evidence for triage", lw=64, lpos=(525, 196)),
    dict(src="percep", dst="gaze", sx=1, sy=0.62, dx=0, dy=0.8, color=GREEN_C,
         label="active-speaker bearing", lw=130, lpos=(840, 312)),
    dict(src="reasoner", dst="spk", sx=0.5, sy=1, dx=0.5, dy=0, color=PURPLE_C),
    dict(src="reasoner", dst="behav", sx=1, sy=0.2, dx=0, dy=0.4, color=PURPLE_C,
         label="gesture tool call; returns on completion", lw=66, lpos=(915, 152)),
    dict(src="reasoner", dst="gaze", sx=1, sy=0.75, dx=0, dy=0.3, color=PURPLE_C,
         label="state: accepted speaker = addressee", lw=66, lpos=(915, 222)),
    dict(src="behav", dst="gw", sx=1, sy=0.5, dx=1, dy=0.5, color=GREEN_C, points=[(1266, 128), (1266, 422)]),
    dict(src="gaze", dst="gw", sx=0.5, sy=1, dx=0.5, dy=0, color=GREEN_C),
]

# --- lower band: on-rails vs open, the degradation ladder, invariants -----------------
yl = 520
BOXES.append(text("rails_h", 30, yl, 600, 20, "TWO DESIGNS IN THE SOURCES", bold=True, font=12))
rows = [
    ("", "on-rails (designed first)", "speech-to-speech (as built)"),
    ("where the LLM sits", "inside one beat, fixed intents and output schema", "the voice AND the sequencer"),
    ("robustness in noise", "high", "lower"),
    ("latency", "near zero for canned lines", "one model round trip"),
    ("auditability", "every line enumerable, testable in CI", "not enumerable: safety is measured"),
    ("charm", "repetitive without pools", "varied"),
]
ry = yl + 24
for i, (a, b, c) in enumerate(rows):
    pal = GREY if i == 0 else WHITE
    BOXES.append(box("rt%da" % i, 30, ry, 150, 24, a, pal, rounded=False, font=10, bold=(i == 0), align="left"))
    BOXES.append(box("rt%db" % i, 180, ry, 225, 24, b, VISIT if i == 0 else WHITE, rounded=False, font=10, bold=(i == 0)))
    BOXES.append(box("rt%dc" % i, 405, ry, 225, 24, c, LLM if i == 0 else WHITE, rounded=False, font=10, bold=(i == 0)))
    ry += 24
BOXES.append(text("rails_n", 30, ry + 4, 600, 34,
                  "Likely posture under crowd noise: a hybrid (canned openers, live follow-ups). A voice pack of pre-rendered lines is always the floor.",
                  font=10.5))

BOXES.append(text("lad_h", 660, yl, 590, 20, "AUTOMATIC, FAIL-CLOSED AUDIO LADDER (each step down is more robust)", bold=True, font=12))
steps = [
    ("open microphone, full duplex (listens while speaking)", VISIT),
    ("half duplex: microphone closed while the robot speaks", VISIT),
    ("push-to-talk", GATE),
    ("canned lines + gestures driven by a hidden operator (Wizard-of-Oz floor): the visitor cannot tell", BAD),
]
for i, (lab, pal) in enumerate(steps):
    BOXES.append(box("st%d" % i, 660 + i * 40, yl + 26 + i * 40, 590 - i * 40, 34, "%d  %s" % (i + 1, lab), pal,
                     font=10.5, align="left"))
BOXES.append(text("lad_n", 660, yl + 26 + 4 * 40 + 2, 590, 34,
                  "A cloud call is never awaited on the critical path: a stall falls back to a canned line from the beat's pool.",
                  font=10.5))

yi = ry + 50
BOXES.append(box("inv", 30, yi, 1220, 46,
                 "DESIGN INVARIANTS. Camera data stays inside the stand; only bearings, flags and actions cross to the robot.  "
                 "Visitor context enriches conversation, never control: mood may shape a line, never a state transition.  "
                 "A safety supervisor sits above the state machine and pre-empts any state.  "
                 "Free conversation stays off the gateway seam.  The reasoner never returns to idle by itself: consumers infer "
                 "'conversation over', e.g. after %s s of quiet listening %s.  Exactly one publisher of the reasoner state." % (wd, t_wd),
                 GATE, font=10.5, align="left", valign="top"))
ylg = yi + 64
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: purple, thick border = the one language model (and its prompt-owned behaviour) | blue = perception and trigger (plain code) | "
                 "green = body and gaze | grey = sensors, speaker, gateway | purple arrows = model output, blue = perception output, green = motion commands.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B1-the-voice-pipeline.md (components as built, one visitor end to end, on-rails versus open conversation, "
    "reasoner as sequencer, degradation, design invariants, 'how it is designed and tested'); Wizard-of-Oz after Kelley 1984; "
    "cascade and speech-to-speech designs after Skantze 2021 (both cited in B1)."],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
