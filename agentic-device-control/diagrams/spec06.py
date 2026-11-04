# -*- coding: utf-8 -*-
# 06 — Safety (note 08): screen content is data, device code disposes, gates for the irreversible, audit log.
# This note has no numbers; the page carries only public OWASP identifiers.
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="06-safety-layers", w=W, h=0)

BOXES = [
    title("The model proposes, device code disposes: each layer after the prompt assumes the one before it has failed, and the log records every step", W),
    box("task", 30, 84, 230, 92, "TASK  (trusted)\nfrom the authenticated cloud\nmessage: the ONLY instruction", CLOUD, font=12),
    box("screen", 30, 206, 230, 140,
        "SCREEN CONTENT  (untrusted DATA)\nnotifications, web pages,\nin-app messages, text inside images\n-> indirect prompt injection\n(OWASP LLM01)", STOP, font=11),
    box("model", 300, 120, 230, 176,
        "THE MODEL PROPOSES\n(orchestrator / specialists)\n\nLAYER 1  INSTRUCTION HIERARCHY\nin the system prompt: only the task is an instruction; screen text is content to read.\nLowers the injection rate. Does NOT remove it.",
        MODEL, font=11),
    box("dev", 570, 70, 680, 330, "DEVICE CODE DISPOSES  (the model cannot change anything in this frame)", DEVICE,
        fill="none", dashed=True, valign="top", bold=True, font=12, sw=2),
    box("l2", 590, 112, 200, 160,
        "LAYER 2  ALLOW-LIST\nnamed, typed tools only; no \"run this command\" tool.\nArguments checked: launch_app accepts listed packages, open_settings listed pages.",
        GUARD, font=11),
    box("l3", 810, 112, 200, 160,
        "LAYER 3  SCOPE LIMITS\nscreen taps cannot be listed one by one, so limit the context: only apps on the per-task list; refuse to type into password, payment or account-deletion screens.",
        GUARD, font=11),
    box("l4", 1030, 112, 200, 160,
        "LAYER 4  CONFIRMATION GATE\nirreversible or costly (purchase, delete, send a message, factory reset): approval from a human or a cloud policy, before EACH action in a batch.",
        GUARD, font=11),
    box("refuse", 590, 318, 380, 62, "REFUSED  ->  error result to the model, and logged", STOP, font=12, bold=True),
    box("exec", 1030, 318, 200, 62, "EXECUTE on the device", MODEL, font=12, bold=True),
    box("log", 30, 430, 1220, 54,
        "LAYER 5  AUDIT LOG  (append-only, stored off the device with the result report, diagram 01):  the task  |  every routing decision  |  every tool call with its arguments  |  every result  |  a reference to each screenshot",
        NOTE, font=12, bold=False, align="left"),

    box("trade", 30, 504, 610, 112,
        "TRADE-OFFS\n"
        "- Least privilege vs capability: every tool removed shrinks the blast radius and removes something a task might need. Start narrow; add a tool when an evaluated task needs it.\n"
        "- Privileged installation is a target: authenticate cloud messages, use short-lived credentials, keep one task source.\n"
        "- Screenshots hold personal data (OWASP LLM02): minimise retention, redact, access-control the logs.\n"
        "- Gates cost latency and autonomy: gate the irreversible few, not every tap.",
        NOTE, align="left", valign="top", font=11),
    box("owasp", 655, 504, 595, 112,
        "OWASP TOP 10 FOR LLM APPLICATIONS 2025 -> WHICH LAYER ANSWERS IT\n"
        "- LLM01 Prompt Injection (the screen is the channel): layer 1 lowers it; layers 2-4 bound the damage when it succeeds.\n"
        "- LLM06 Excessive Agency (more tools, permissions or autonomy than the job needs): layers 2, 3, 4.\n"
        "- LLM02 Sensitive Information Disclosure: retention, redaction and access control on screenshots and logs (layer 5).\n"
        "A gate the model can approve for itself is not a gate.",
        STOP, fill="#fff7f7", align="left", valign="top", font=11),
    box("legend", 30, 630, 1220, 36,
        "Legend:  purple = trusted input  |  red = untrusted input, refusal  |  green = model / execution  |  amber = a check in device code  |  "
        "dashed blue frame = code the model cannot alter  |  dashed grey arrows = written to the audit log",
        WHITE, align="left", font=11),
]

LOG = "#999999"
EDGES = [
    dict(src="task", dst="model", label="instruction", color="#9673a6", bold=True, sx=1, sy=0.5, dx=0, dy=0.2, points=[(280, 130), (280, 155)], lpos=(282, 114), lw=80),
    dict(src="screen", dst="model", label="read as data", color="#b85450", sx=1, sy=0.5, dx=0, dy=0.8, points=[(280, 276), (280, 261)], lpos=(282, 294), lw=90),
    dict(src="model", dst="l2", label="tool\ncall", color="#82b366", bold=True, sx=1, sy=0.4, dx=0, dy=0.4, lpos=(550, 150), lw=40),
    dict(src="l2", dst="l3", label="ok", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="l3", dst="l4", label="ok", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="l2", dst="refuse", label="fails", color="#b85450", sx=0.5, sy=1, dx=0.263, dy=0),
    dict(src="l3", dst="refuse", label="fails", color="#b85450", sx=0.5, sy=1, dx=0.842, dy=0),
    dict(src="l4", dst="refuse", label="denied", color="#b85450", sx=0.15, sy=1, dx=1, dy=0.5, points=[(1060, 296), (1000, 296), (1000, 349)], lpos=(1030, 288), lw=50),
    dict(src="l4", dst="exec", label="approved", color="#82b366", sx=0.7, sy=1, dx=0.7, dy=0, lpos=(1170, 295), lw=60),
    dict(src="refuse", dst="model", label="error result: re-plan", color="#b85450", sx=0, sy=0.5, dx=0.5, dy=1, points=[(415, 349)], lpos=(480, 362), lw=120),
    dict(src="model", dst="log", color=LOG, dashed=True, sx=0.3, sy=1, dx=0.278, dy=0),
    dict(src="refuse", dst="log", color=LOG, dashed=True, sx=0.5, sy=1, dx=0.615, dy=0),
    dict(src="exec", dst="log", color=LOG, dashed=True, sx=0.5, sy=1, dx=0.902, dy=0),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/08-safety.md (two dominant risks, five controls, trade-offs). Public: OWASP Top 10 for LLM Applications 2025, https://genai.owasp.org/llm-top-10/ (LLM01, LLM02, LLM06); "
    "computer-use tool documentation, 'Limitations' (prompt injection via web pages or images) and 'Batch actions' (confirm before each action in a batch).",
    "This page carries no numbers from ../constants.json: note 08 states none. OWASP identifiers are public labels, not quantities."],
    30, 680, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
