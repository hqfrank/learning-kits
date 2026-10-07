"""Scene 04 — occupancy and the twist (same occupancy, 4.24x runtime).
Narration clip = 39.92 s. Scene length target >= 40.42 s.
Numbers: max_warps_per_sm 48, registers_per_sm 65536; 67% and 4.24x from note 03 (B3).
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, HARDWARE, LIMIT, SCHED, INK, MUTE, source_tag

CLIP = 39.92


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Occupancy is not issue rate", font_size=30, color=INK).to_edge(UP, buff=0.35)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)
        self.add(source_tag("max_warps 48 - registers_per_sm 65536"))

        # 48-slot grid (6 rows x 8 cols)
        slots = VGroup(*[
            Square(side_length=0.42, stroke_color=MUTE, stroke_width=1.5,
                   fill_color=MUTE, fill_opacity=0.06)
            for _ in range(48)
        ])
        slots.arrange_in_grid(rows=6, cols=8, buff=0.08)
        slots.next_to(title, DOWN, buff=0.5).shift(3.2 * LEFT)
        cap = Text("48 warp slots / SM", font_size=20, color=INK).next_to(slots, UP, buff=0.2)
        self.play(FadeIn(slots), FadeIn(cap), run_time=1.2)
        self.wait(1.0)

        # fill 32 slots green (register limit), stop at 32 with a red line
        fills = []
        for i in range(32):
            fills.append(slots[i].animate.set_fill(HARDWARE, opacity=0.55).set_stroke(HARDWARE))
        self.play(LaggedStart(*fills, lag_ratio=0.03), run_time=3.0)

        # red limit line after slot 32 (between row 4 and row 5)
        line = Line(slots[32].get_corner(UL) + 0.04 * UP + 0.3 * LEFT,
                    slots[39].get_corner(UR) + 0.04 * UP + 0.3 * RIGHT,
                    color=LIMIT, stroke_width=5)
        occ = Text("32 / 48 = 67%", font_size=22, color=LIMIT).next_to(slots, DOWN, buff=0.25)
        reg = Text("register file bit first", font_size=18, color=LIMIT).next_to(occ, DOWN, buff=0.15)
        self.play(Create(line), run_time=0.8)
        self.play(FadeIn(occ), run_time=0.8)
        self.play(FadeIn(reg), run_time=0.6)
        self.wait(3.0)

        # the twist: two bars, same occupancy, 1x vs 4.24x runtime
        base = Rectangle(width=1.1, height=1.0, stroke_color=HARDWARE, stroke_width=3,
                         fill_color=HARDWARE, fill_opacity=0.4)
        slow = Rectangle(width=1.1, height=4.24, stroke_color=LIMIT, stroke_width=3,
                         fill_color=LIMIT, fill_opacity=0.4)
        base_l = Text("1x", font_size=20, color=INK)
        slow_l = Text("4.24x", font_size=22, color=LIMIT)
        bars = VGroup(base, slow).arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
        bars.scale(0.62)
        # right half, bottom-aligned low so the tall bar clears the title
        bars.to_edge(DOWN, buff=1.4).shift(3.3 * RIGHT)
        base_l.next_to(base, UP, buff=0.2)
        slow_l.next_to(slow, UP, buff=0.2)
        tw_title = Text("same occupancy", font_size=22, color=INK)
        tw_title.next_to(title, DOWN, buff=0.4).shift(3.3 * RIGHT)
        runtime_lab = Text("runtime", font_size=18, color=MUTE).next_to(bars, DOWN, buff=0.2)
        tag2 = Text("note 03 / B3", font_size=16, color=MUTE).next_to(runtime_lab, DOWN, buff=0.1)

        self.play(FadeIn(tw_title), run_time=0.6)
        self.play(GrowFromEdge(base, DOWN), FadeIn(base_l), run_time=1.0)
        self.play(GrowFromEdge(slow, DOWN), FadeIn(slow_l), run_time=1.4)
        self.play(FadeIn(runtime_lab), FadeIn(tag2), run_time=0.6)

        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
