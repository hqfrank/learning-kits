"""Scene 05 — The ladder: what buys the loop back. Narration ~39.23 s."""
from manim import *
from theme import (BG, CONTROL, MEMORY, VLA, DANGER, GHOST, INK,
                   SHARED_CTX_P99, SEP_CTX_P99, PLAIN_MPS_P99, MPS_CAP25_P99,
                   WBC_DEADLINE, src_tag)

CLIP = 39.23


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The ladder: buying the loop back", font_size=36, color=INK).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # four steps, left to right, each a box whose colour = pass/fail vs 10 ms
        steps = [
            ("Shared\ncontext", f"p99 {SHARED_CTX_P99:g} ms\n51% dropped", DANGER, "loop destroyed"),
            ("Separate\nprocess", f"~{SEP_CTX_P99:g} ms\n4.9% dropped", MEMORY, "~90% back"),
            ("Plain\nMPS", f"{PLAIN_MPS_P99:g} ms", DANGER, "doesn't help"),
            ("MPS +\n25% SM cap", f"{MPS_CAP25_P99:g} ms\n0% dropped", CONTROL, "THE FIX"),
        ]

        boxes = VGroup()
        x = -5.2
        heights = [3.4, 2.2, 3.0, 1.3]
        for (name, val, col, note), h in zip(steps, heights):
            box = Rectangle(width=2.3, height=h, stroke_color=col, fill_color=col, fill_opacity=0.2, stroke_width=3)
            box.move_to([x, -1.9 + h / 2, 0])
            nm = Text(name, font_size=18, color=col).next_to(box, UP, buff=0.12)
            vl = Text(val, font_size=15, color=INK).move_to(box.get_center())
            nt = Text(note, font_size=15, color=col).next_to(box, DOWN, buff=0.12)
            boxes.add(VGroup(box, nm, vl, nt))
            x += 2.7

        # 10 ms deadline reference across the staircase (scaled: 1 ms = 0.28 units, base y=-1.9)
        base_y = -1.9
        scale = 3.4 / SHARED_CTX_P99  # map 110.7 ms box height; but deadline line uses its own small scale
        # draw deadline relative to the FIX/plain scale: use a simple annotated line near bottom
        dline = DashedLine([-6.3, base_y + 0.9, 0], [6.3, base_y + 0.9, 0], color=DANGER, stroke_width=2)
        dlab = Text("10 ms deadline (only the cap clears it)", font_size=15, color=DANGER)
        dlab.next_to(dline, UP, buff=0.05).align_to(dline, LEFT).shift(RIGHT * 0.2)

        for grp in boxes:
            self.play(FadeIn(grp[0], shift=UP * 0.2), FadeIn(grp[1]), run_time=0.8)
            self.play(FadeIn(grp[2]), FadeIn(grp[3]), run_time=0.7)

        self.play(Create(dline), FadeIn(dlab), run_time=1.0)

        # VLA cost tag beside the fix
        cost = Text("VLA  5 -> 3.6 Hz", font_size=18, color=VLA)
        cost.next_to(boxes[3][0], RIGHT, buff=0.1).shift(UP * 0.4)
        self.play(FadeIn(cost, shift=LEFT * 0.2), run_time=1.0)

        tag = src_tag("params: shared/separate_context, plain_mps, mps_cap_wbc_p99  (L4)").to_corner(DR, buff=0.12)
        self.play(FadeIn(tag), run_time=0.5)

        used = 1.0 + 4 * (0.8 + 0.7) + 1.0 + 1.0 + 0.5
        self.wait(max(0.5, CLIP + 0.5 - used))
