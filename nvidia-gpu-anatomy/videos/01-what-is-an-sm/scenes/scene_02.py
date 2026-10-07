"""Scene 02 — the hardware ladder + the chip (SMs behind one L2 + controller).
Narration clip = 27.48 s. Scene length target >= 27.98 s.
Numbers: sm_count 16/20, smsp_per_sm 4.
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, SOFTWARE, HARDWARE, LIMIT, INK, MUTE, rung, source_tag

CLIP = 27.48


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = Text("The hardware that runs it", font_size=32, color=INK).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)
        self.add(source_tag("sm_count 16/20 - smsp_per_sm 4"))

        # software ladder (small, left) and hardware ladder (right)
        sw_labels = ["thread", "warp", "block", "grid"]
        hw_labels = ["lane", "sub-partition", "SM", "GPU"]
        sw = VGroup(*[rung(l, SOFTWARE, w=2.5, h=0.6, fs=22) for l in sw_labels]).arrange(UP, buff=0.3)
        hw = VGroup(*[rung(l, HARDWARE, w=2.8, h=0.6, fs=22) for l in hw_labels]).arrange(UP, buff=0.3)
        sw.next_to(title, DOWN, buff=0.5).shift(3.4 * LEFT)
        hw.next_to(title, DOWN, buff=0.5).shift(0.2 * LEFT)

        self.play(FadeIn(sw, shift=0.2 * UP), run_time=1.0)
        self.play(FadeIn(hw, shift=0.2 * UP), run_time=1.0)

        # mapping arrows (red = the key ones): warp->sub-partition, block->SM, grid->GPU
        pairs = [(1, 1), (2, 2), (3, 3)]
        arrows = VGroup()
        for i, j in pairs:
            a = Arrow(sw[i].get_right(), hw[j].get_left(), buff=0.1,
                      stroke_width=3, color=LIMIT, max_tip_length_to_length_ratio=0.12)
            arrows.add(a)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.4), run_time=2.4)
        self.wait(2.0)

        # the chip: grid of 16 SM squares over an L2 bar over a controller->DRAM bar
        sms = VGroup()
        for r in range(2):
            for c in range(8):
                sq = Square(side_length=0.34, stroke_color=HARDWARE, stroke_width=2,
                            fill_color=HARDWARE, fill_opacity=0.18)
                sms.add(sq)
        sms.arrange_in_grid(rows=2, cols=8, buff=0.09)
        chip_label = Text("Orin 16 SMs  /  Thor 20", font_size=20, color=INK)
        l2 = RoundedRectangle(corner_radius=0.08, width=3.5, height=0.5,
                              stroke_color=MUTE, stroke_width=3, fill_color=MUTE, fill_opacity=0.12)
        l2t = Text("shared L2", font_size=20, color=INK).move_to(l2)
        l2g = VGroup(l2, l2t)
        ctrl = RoundedRectangle(corner_radius=0.08, width=3.5, height=0.5,
                                stroke_color=MUTE, stroke_width=3, fill_color=MUTE, fill_opacity=0.08)
        ctrlt = Text("memory controller - DRAM", font_size=18, color=INK).move_to(ctrl)
        ctrlg = VGroup(ctrl, ctrlt)

        chip = VGroup(sms, chip_label, l2g, ctrlg)
        chip_label.next_to(sms, UP, buff=0.15)
        l2g.next_to(sms, DOWN, buff=0.2)
        ctrlg.next_to(l2g, DOWN, buff=0.2)
        chip.next_to(hw, RIGHT, buff=0.6).shift(0.0 * UP)
        chip.scale(0.9).to_edge(RIGHT, buff=0.3)

        self.play(LaggedStart(*[FadeIn(s) for s in sms], lag_ratio=0.03), run_time=2.0)
        self.play(FadeIn(chip_label), run_time=0.5)
        self.play(FadeIn(l2g, shift=0.2 * UP), run_time=0.8)
        self.play(FadeIn(ctrlg, shift=0.2 * UP), run_time=0.8)

        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
