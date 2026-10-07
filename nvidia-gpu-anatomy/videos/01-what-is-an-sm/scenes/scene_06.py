"""Scene 06 — why a robot engineer cares.
Narration clip = 27.38 s. Scene length target >= 27.88 s.
Numbers: l2_size (Thor 32 MB).
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, SOFTWARE, HARDWARE, LIMIT, SCHED, THOR, INK, MUTE, source_tag

CLIP = 27.38


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Why a robot engineer cares", font_size=30, color=INK).to_edge(UP, buff=0.35)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)
        self.add(source_tag("l2_size: Thor 32 MB"))

        # LEFT: a nearly-empty SM, one small block, 3 of 4 ports idle
        sm = RoundedRectangle(corner_radius=0.1, width=3.2, height=2.4,
                              stroke_color=HARDWARE, stroke_width=2,
                              fill_color=HARDWARE, fill_opacity=0.06)
        sm.shift(3.4 * LEFT + 0.4 * DOWN)
        ports = VGroup()
        for i in range(4):
            active = (i == 0)
            p = RoundedRectangle(corner_radius=0.05, width=0.6, height=0.6,
                                 stroke_color=SCHED if active else MUTE, stroke_width=2,
                                 fill_color=SCHED if active else MUTE,
                                 fill_opacity=0.5 if active else 0.1)
            ports.add(p)
        ports.arrange(RIGHT, buff=0.2).move_to(sm.get_center() + 0.4 * UP)
        small_block = RoundedRectangle(corner_radius=0.05, width=0.5, height=0.25,
                                       stroke_color=SOFTWARE, stroke_width=2,
                                       fill_color=SOFTWARE, fill_opacity=0.6)
        small_block.move_to(ports[0].get_center())
        idle = Text("3 of 4 ports idle", font_size=16, color=MUTE).next_to(ports, DOWN, buff=0.3)
        cap1 = Text("tiny control kernel", font_size=18, color=INK).next_to(sm, UP, buff=0.15)

        self.play(FadeIn(sm), run_time=0.6)
        self.play(FadeIn(cap1), FadeIn(ports), run_time=0.8)
        self.play(FadeIn(small_block), FadeIn(idle), run_time=0.8)
        self.wait(3.5)

        # RIGHT: two model blobs vs a 32 MB L2 line
        l2line = Line(1.6 * RIGHT, 5.4 * RIGHT, color=INK, stroke_width=2).shift(0.3 * UP)
        l2lab = Text("32 MB L2", font_size=18, color=INK).next_to(l2line, UP, buff=0.1)
        fit = Circle(radius=0.45, stroke_color=THOR, stroke_width=3, fill_color=THOR, fill_opacity=0.3)
        fit.next_to(l2line, UP, buff=0.6).shift(1.4 * RIGHT)
        spill = Circle(radius=0.75, stroke_color=LIMIT, stroke_width=3, fill_color=LIMIT, fill_opacity=0.25)
        spill.next_to(l2line, DOWN, buff=0.6).shift(2.6 * RIGHT)
        spill_l = Text("too big: DRAM tax", font_size=15, color=LIMIT).next_to(spill, DOWN, buff=0.1)

        self.play(Create(l2line), FadeIn(l2lab), run_time=0.8)
        self.play(FadeIn(fit), run_time=0.6)
        fit_l2 = Text("fits: resident", font_size=15, color=THOR).next_to(fit, UP, buff=0.12)
        self.play(FadeIn(fit_l2), run_time=0.5)
        self.play(FadeIn(spill), FadeIn(spill_l), run_time=0.8)

        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
