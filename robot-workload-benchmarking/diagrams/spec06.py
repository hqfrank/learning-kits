# -*- coding: utf-8 -*-
# 06 — Campaign flow (C1/C4/C5/C6): predict -> pre-register -> solo -> review -> combined tiers
#      (seeded interleaved) -> gates per window -> carries verdict per KPI band -> first-limit
#      attribution; loops back via addenda/supersede ONLY for harness bugs, never for stack behaviour.
# Source: C1 (ledger), C5 (pre-registration, interleaving, addenda/supersede), C2 (solo levels),
#         C4 (windows + validity gates: valid/flagged/void), C6 (tiers, bands, first-limit attribution).

PAGE = dict(name="06-campaign-flow", w=1340, h=790)

STEP = "#dae8fc"; STEP_S = "#6c8ebf"
GATE = "#ffe6cc"; GATE_S = "#d79b00"
VERD = "#d5e8d4"; VERD_S = "#82b366"
LOOP = "#e1d5e7"; LOOP_S = "#9673a6"
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"
HI = "#f8cecc"; HI_S = "#b85450"

BOXES = [
    dict(id="title", x=20, y=12, w=1300, h=30, rounded=False, align="center", valign="middle",
         bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="The campaign flow: predict before you measure, freeze the plan, build up in tiers, gate every window, then attribute the first limit"),

    # Row 1: predict -> pre-register
    dict(id="predict", x=40, y=66, w=280, h=92, fill=STEP, stroke=STEP_S, font=11,
         align="left", valign="top",
         label="1. PREDICT - compute-budget ledger (C1)\nt = FLOP/R + bytes/B + t_CPU per stage.\nR, B MEASURED on target, not datasheet.\nName bound class + falsifiable predictions.\nSmall batch-1 models = launch-bound."),
    dict(id="prereg", x=360, y=66, w=280, h=92, fill=STEP, stroke=STEP_S, font=11,
         align="left", valign="top",
         label="2. PRE-REGISTER (C5)\nFreeze hypotheses, PASS/FAIL thresholds,\nand the seeded run order BEFORE data.\nNo tuning after data. Disclose anything\nseen early."),
    dict(id="solo", x=680, y=66, w=280, h=92, fill=STEP, stroke=STEP_S, font=11,
         align="left", valign="top",
         label="3. SOLO runs (C2)\nEach service alone: L1 engine / L2 deployed /\nL3 + upstream. DRIVE event-driven services\n(no idle floors). Clean baseline = the\nDENOMINATOR for interference."),
    dict(id="review1", x=1000, y=66, w=300, h=92, fill=STEP, stroke=STEP_S, font=11,
         align="left", valign="top",
         label="4. REVIEW\nIndependent second person checks the\nsolo baselines, gate logic, and statistics\nbefore the combined runs begin."),

    # Row 2: combined tiers
    dict(id="combined", x=40, y=200, w=600, h=120, fill=STEP, stroke=STEP_S, font=11,
         align="left", valign="top",
         label="5. COMBINED runs in TIERS (C6), seeded INTERLEAVED order (C5)\nBuild up the stack: default load -> next-generation -> + manipulation -> + on-demand large models.\nInterleave A/B (ABBA / mirror) so slow drift cancels; replicate blocks; paired within-block comparisons.\nInterference factor = combined value / solo sum, read per KPI (the TAIL, not the mean)."),

    # Row 2 right: the gate funnel
    dict(id="gate", x=680, y=200, w=620, h=120, fill=GATE, stroke=GATE_S, font=11,
         align="left", valign="top",
         label="6. VALIDITY GATES per window (C4) - warm-up then a fixed window from a sample-count rule\nalive (rate DROP is an outcome, silence is a void) | expected input rates | crash scan | foreign-CPU census | clocks locked at BOTH ends\n=> each window is VALID (counts) / FLAGGED (kept with caveat) / VOID (thrown out, with a recorded void class)"),

    # per-window outcome chips
    dict(id="valid", x=680, y=336, w=195, h=48, fill=VERD, stroke=VERD_S, font=11, bold=True,
         align="center", valign="middle", label="VALID\nnumbers count"),
    dict(id="flagged", x=890, y=336, w=195, h=48, fill=GATE, stroke=GATE_S, font=11, bold=True,
         align="center", valign="middle", label="FLAGGED\nkept with a caveat"),
    dict(id="void", x=1100, y=336, w=200, h=48, fill=HI, stroke=HI_S, font=11, bold=True,
         align="center", valign="middle", label="VOID\nrecord the void class"),

    # Row 3: carries verdict
    dict(id="carries", x=40, y=410, w=600, h=120, fill=VERD, stroke=VERD_S, font=11,
         align="left", valign="top",
         label="7. 'CARRIES' VERDICT per KPI band (C6), over valid windows\nEach timing KPI (control-loop misses, camera rate, perception rate, VLA rate) has pre-set bands:\nPASS band | UNRESOLVED zone | FAIL band.\nA cell CARRIES only if EVERY applicable KPI is PASS. Any FAIL => does not carry. Any UNRESOLVED (no FAIL) => unresolved."),

    # Row 3 right: first-limit attribution
    dict(id="attrib", x=680, y=410, w=620, h=120, fill=VERD, stroke=VERD_S, font=11,
         align="left", valign="top",
         label="8. FIRST-LIMIT ATTRIBUTION (C6), pre-registered classifier\nCPU-pool (pool ~full + loser's drop tracks rising run-queue wait) | GPU (GPU-busy ~saturated, GPU loser, CPU flat) |\nmemory (mem index high, CPU-only loser, no CPU saturation) | none-observed; a loss with no matching signal = UNATTRIBUTED.\nSATURATED-BASELINE caveat: if the lightest tier is already at the wall, the classifier reads unattributed BY CONSTRUCTION - report the saturation, do not pretend it found nothing."),

    # the loop-back rule
    dict(id="loop", x=40, y=566, w=1260, h=78, rounded=True, fill=LOOP, stroke=LOOP_S, font=12,
         align="left", valign="middle",
         label="LOOP BACK ONLY for a HARNESS / INSTRUMENT bug (C5):  record a numbered ADDENDUM (defect, evidence, fix, impact on windows already run); if a recorded window was affected, SUPERSEDE it - re-run whole under the SAME seeds, keep the original, log it.  "
               "NEVER loop back to change stack behaviour: a surprise about the STACK is a FINDING, not a bug to tune away. No tuning after data (C5)."),
]

# legend + sources
BOXES += [
    dict(id="legend", x=40, y=664, w=620, h=92, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\nblue = a campaign step (predict -> pre-register -> solo -> review -> combined)\namber = validity gates + the FLAGGED outcome   green = a verdict step (valid / carries / attribution)\nred = VOID / the saturated-baseline caveat (the honest failure modes)   purple = the addenda/supersede loop\nArrows = campaign order; the only backward arrow is the harness-bug loop, never a stack-behaviour loop."),
    dict(id="src", x=680, y=664, w=620, h=92, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Source: C1 (predict-then-measure, compute-budget ledger, bound class, falsifiable predictions, launch-bound batch-1 models); "
               "C5 (pre-registration, no tuning after data, seeded interleaved ABBA/mirror order, replicate blocks, paired comparisons, addenda + supersedes, independent review); "
               "C2 (solo L1/L2/L3, idle floors, drivers); C4 (warm-up + fixed window, sample-count rule, validity gates alive/rates/crash/census/clocks, valid vs flagged vs void + void class); "
               "C6 (workload tiers, interference factor, PASS/UNRESOLVED/FAIL bands, first-limit attribution CPU/GPU/memory/none, saturated-baseline failure). No measured robot numbers."),
]

EDGES = [
    dict(src="predict", dst="prereg", color="#6c8ebf", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="prereg", dst="solo", color="#6c8ebf", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="solo", dst="review1", color="#6c8ebf", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="review1", dst="combined", color="#6c8ebf", bold=True, sx=0.5, sy=1, dx=0.9, dy=0),
    dict(src="combined", dst="gate", color="#6c8ebf", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="gate", dst="carries", color="#82b366", bold=True, sx=0.1, sy=1, dx=0.5, dy=0),
    dict(src="carries", dst="attrib", color="#82b366", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="attrib", dst="loop", color="#9673a6", dashed=True, sx=0.5, sy=1, dx=0.9, dy=0),
]
